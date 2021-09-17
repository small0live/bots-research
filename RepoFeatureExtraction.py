from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import os
import numpy as np
from scipy.stats.stats import pearsonr
import datetime
from lifelines.utils import datetimes_to_durations
from lifelines.utils import survival_table_from_events
from lifelines import KaplanMeierFitter
from pysal.inequality import gini

exp_dir = "/home/social-sim/SocialSim/Team/exp"
if not os.path.isdir(exp_dir):
    os.mkdir(exp_dir)

es = Elasticsearch(['10.0.0.100'], port=9200, timeout=600.0)
six_months = 6 * (365 / 12)

# work_events = ['PushEvent', 'PullRequestEvent', 'IssueCommentEvent', 'PullRequestReviewCommentEvent']


def aggregate_feature(feature_name):
    cur_day = datetime.datetime(2016, 1, 1)
    end_day = datetime.datetime(2016, 1, 31)
    dfs = []
    while cur_day <= end_day:
        print(cur_day)
        cur_dir = "%s/created_%s" % (exp_dir, cur_day.strftime("%Y-%m-%d"))
        cur_day += datetime.timedelta(days=1)
        feature_file = "%s/%s.csv" % (cur_dir, feature_name)
        df = pd.read_csv(feature_file)
        dfs.append(df)
    res_df = pd.concat(dfs)
    feature_file = "%s/features/%s.csv" % (exp_dir, feature_name)
    res_df.to_csv(feature_file, index=False)


def add_feature(feature_name):
    feature_file = "%s/features/%s.csv" % (exp_dir, feature_name)
    feature_df = pd.read_csv(feature_file)
    training_file = "%s/training_data/new2_training_data.csv" % exp_dir
    train_df = pd.read_csv(training_file)

    datetime.datetime.now()
    os.rename(training_file, "%s_%s.csv" % (training_file, datetime.datetime.now()))

    # df = pd.concat([feature_df, train_df], axis=1)
    print('train_df', train_df.shape, 'feature_df', feature_df.shape)
    df = train_df.merge(feature_df, how='left', on='name_h')
    print('df', df.shape)
    # df.index.name = 'name_h'
    df.to_csv(training_file, index=False)


def concat_performance_and_features(features_file, performance_file, feature_vectors_file):
    feat_df = pd.read_csv(features_file).set_index('name_h')
    perf_df = pd.read_csv(performance_file).set_index('name_h')

    df = pd.concat([feat_df, perf_df[['work']]], axis=1)
    print("feature vector df size", df.shape)
    df.to_csv(feature_vectors_file)


def extract_all_events_features(first_6m_file, event_features_file):
    df = pd.read_csv(first_6m_file).set_index('name_h')
    event_columns = list(df.columns)
    event_columns.remove('total')
    events_to_include = ['GollumEvent', 'CommitCommentEvent', 'IssuesEvent']
    for col in event_columns:
        df['prop_' + col] = df[col] / df['total']
        df['has_' + col] = np.where(df[col] > 0, True, False)
    feature_columns = [col for col in df.columns if
                       col == 'total' or col in events_to_include
                       or col.startswith('has') or col.startswith('prop')]
    df[feature_columns].to_csv(event_features_file)


def extract_repos_burstiness(active_repo_ids, detailed_events_file, cur_dir, feature_name):
    df = pd.read_csv(detailed_events_file)
    df = df[df.name_h.isin(active_repo_ids)]
    grouped = df.groupby('name_h')
    res_df = grouped.apply(calculate_burstiness)
    res_df.drop_duplicates('name_h', inplace=True)

    f = "%s/%s.csv" % (cur_dir, 'formation_burstiness')
    res_df[['name_h', feature_name]].to_csv(f, index=False)


def calculate_burstiness(df):
    # df = df[(df.type == 'IssueCommentEvent') | (df.type == 'PullRequestReviewCommentEvent')]
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at')

    delta = df['created_at'].diff()
    delta_min = [i // 60 for i in delta.dt.seconds.tolist()]

    sd = np.std(delta_min[1:])
    m = np.mean(delta_min[1:])
    burstiness = (sd - m) / (sd + m)
    df['burstiness'] = burstiness
    return df


def extract_repos_issue_labels(active_repo_ids, cur_day, cur_dir):
    # , feature_name = ['prop_labeled_issues', 'prop_bug_label']
    end_time = cur_day + datetime.timedelta(days=six_months)
    s = Search(using=es, index='events')
    start_time = cur_day.strftime("%Y-%m-%d") + "T00:00:00Z"
    end_time = end_time.strftime("%Y-%m-%d") + "T00:00:00Z"
    print(start_time, end_time)
    s = s.filter("range", **{'created_at': {
        'gte': start_time,
        'lt': end_time
    }})
    s = s.filter('terms', **{'repo.name_h.keyword': active_repo_ids})
    s = s.query('match', type="IssuesEvent")
    s = s.query('match_all')
    s = s.source(['repo.name_h', 'payload.issue.id_h', 'payload.issue.labels', 'created_at'])

    response = s.execute()
    print(response.hits.total)
#
    df = pd.DataFrame((d.to_dict() for d in s.scan()))
    df = pd.concat([df.drop(["repo"], axis=1), df["repo"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["payload"], axis=1), df["payload"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["issue"], axis=1), df["issue"].apply(pd.Series)], axis=1)

    df.sort_values(by='created_at', inplace=True, ascending=False)
    df.drop_duplicates('id_h', keep='first', inplace=True)

    df['labels'] = df['labels'].astype('str')

    grouped = df.groupby('name_h')
    res_df = grouped.apply(calc_labeled_issues_prop)
    res_df.drop_duplicates('name_h', inplace=True)

    f = "%s/%s.csv" % (cur_dir, 'formation_issue_label')
    # res_df[['name_h', 'prop_labeled_issues', 'prop_bug_labeled_issue']].to_csv(f, index=False)
    res_df[['name_h', 'labeled_issues_count', 'prop_labeled_issues']].to_csv(f, index=False)

def calc_labeled_issues_prop(df):
    # print(df['labels'].str.contains('bug'))
    all_issues = df.shape[0]
    labeled_issues_df = df[df['labels'].str.len() > 3]
    labeled_issues_prop = labeled_issues_df.shape[0] / all_issues
    # df['labels'] = df['labels'].str.lower()
    # bug_count = df[df['labels'].str.contains('bug')].shape[0]

    df['labeled_issues_count'] = labeled_issues_df.shape[0]
    df['prop_labeled_issues'] = labeled_issues_prop
    # df['prop_bug_labeled_issue'] = bug_count / all_issues
    # print(labeled_issues_prop, bug_count / all_issues)

    return df


def extract_repos_comment_feature(active_repo_ids, cur_day, cur_dir):
    end_time = cur_day + datetime.timedelta(days=six_months)
    s = Search(using=es, index='events')
    start_time = cur_day.strftime("%Y-%m-%d") + "T00:00:00Z"
    end_time = end_time.strftime("%Y-%m-%d") + "T00:00:00Z"
    print(start_time, end_time)
    s = s.filter("range", **{'created_at': {
        'gte': start_time,
        'lt': end_time
    }})
    s = s.filter('terms', **{'repo.name_h.keyword': active_repo_ids})
    s = s.query('match', type="IssueCommentEvent CommitCommentEvent PullRequestReviewCommentEvent")
    s = s.query('match_all')
    s = s.source(['repo.name_h', 'payload.comment.body_m'])

    response = s.execute()
    print(response.hits.total)

    df = pd.DataFrame((d.to_dict() for d in s.scan()))
    df = pd.concat([df.drop(["repo"], axis=1), df["repo"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["payload"], axis=1), df["payload"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["comment"], axis=1), df["comment"].apply(pd.Series)], axis=1)

    df.to_csv(cur_dir + "/formation_all_comments_text.csv", index=False)

    grouped = df.groupby('name_h')
    res_df = grouped.apply(comment_features)
    res_df.drop_duplicates('name_h', inplace=True)

    f = "%s/%s.csv" % (cur_dir, 'formation_comments')
    res_df[['name_h', 'prop_pos_comments', 'prop_neg_comments', 'prop_thank_comments',
            'avg_comment_len', 'prop_positive_word_comments', 'prop_regret_word_comments']].to_csv(f, index=False)


def comment_features(df):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['body_m'].apply(lambda x: sentiment_analyzer.polarity_scores(x))
    df = pd.concat([df.drop(["sentiment"], axis=1), df["sentiment"].apply(pd.Series)], axis=1)
    df['comment_len'] = df['body_m'].apply(lambda x: count_words(x))

    comments_count = df.shape[0]
    df['prop_pos_comments'] = (df.pos > 0).sum() / comments_count
    df['prop_neg_comments'] = (df.neg > 0).sum() / comments_count
    df['prop_thank_comments'] = (df.body_m.str.contains('thank')).sum() / comments_count
    df['avg_comment_len'] = df['comment_len'].mean()

    positive_words = ['help', 'feedback', 'appreciate', 'respect', 'grateful', 'please']
    df['prop_positive_word_comments'] = (df.body_m.str.contains('|'.join(positive_words))).sum() / comments_count
    regret_words = ['sorry', 'apologize', 'forgive']
    df['prop_regret_word_comments'] = (df.body_m.str.contains('|'.join(regret_words))).sum() / comments_count

    return df


stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
def count_words(text):
    stop_free = " ".join([i for i in text.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    words = normalized.split()
    return len(words)


def extract_issue_closure_rate(active_teams_ids, cur_day, cur_dir):
    start_time = cur_day + datetime.timedelta(days=365)
    end_time = start_time + datetime.timedelta(days=six_months)
    s = Search(using=es, index='events')
    start_time = start_time.strftime("%Y-%m-%d") + "T00:00:00Z"
    end_time = end_time.strftime("%Y-%m-%d") + "T00:00:00Z"
    print(start_time, end_time)
    s = s.filter("range", **{'created_at': {
        'gte': start_time,
        'lt': end_time
    }})
    s = s.filter('terms', **{'repo.name_h.keyword': active_teams_ids})
    s = s.query('match', type="IssuesEvent")
    s = s.source(['repo.name_h', 'payload.issue.id_h', 'payload.action', 'created_at'])

    response = s.execute()
    print(response.hits.total)

    df = pd.DataFrame((d.to_dict() for d in s.scan()))
    df = pd.concat([df.drop(["repo"], axis=1), df["repo"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["payload"], axis=1), df["payload"].apply(pd.Series)], axis=1)
    df = pd.concat([df.drop(["issue"], axis=1), df["issue"].apply(pd.Series)], axis=1)
    grouped = df.groupby('name_h')
    res_df = grouped.apply(issue_closure_rate)
    res_df.drop_duplicates('name_h', inplace=True)

    f = "%s/%s.csv" % (cur_dir, 'eval_issue_closure_and_count')
    res_df[['name_h', 'eval_survival_day_median', 'issues_count']].to_csv(f, index=False)



def issue_closure_rate(df):
    # The survival function defines the probability the death event has not occured yet at time t,
    # or equivalently, the probability of surviving past time t.
    df['eval_survival_day_median'] = np.nan
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at')

    issues_group = df.groupby('id_h')
    res_df = issues_group.apply(closure_rate)
    res_df = res_df[res_df.start_time.notnull()]
    # print(res_df.head())
    if res_df.shape[0] >= 5:
        T, E = datetimes_to_durations(res_df.start_time, res_df.end_time, freq='D')
        table = survival_table_from_events(T, E)
        # print(table.head())
        kmf = KaplanMeierFitter()
        kmf.fit(T, event_observed=E)  # or, more succinctly, kmf.fit(T, E)
        # print("kmf.median_", kmf.median_)
        # print(kmf.survival_function_)

        if kmf.median_ != np.inf:
            df['eval_survival_day_median'] = kmf.median_
            df['issues_count'] = res_df.shape[0]
    return df


def closure_rate(issue_df):
    actions = issue_df['action'].tolist()
    datetimes = issue_df['created_at'].tolist()
    issue_df['start_time'] = pd.NaT
    issue_df['end_time'] = pd.NaT
    if actions[0] != 'opened':
        return issue_df
    issue_df['start_time'] = datetimes[0]
    if actions[-1] == 'closed':
        issue_df['end_time'] = datetimes[-1]
    return issue_df


def all_events_per_person(active_teams_file, cur_dir):
    events_file = "%s/active_repos_6months_aggregated_events.csv" % cur_dir
    events_df = pd.read_csv(events_file)
    teams_df = pd.read_csv(active_teams_file)
    df = teams_df.merge(events_df, on='name_h', how='left')
    event_columns = [col for col in df.columns if col.endswith('Event') and col not in
                     ['IssueCommentEvent', 'PullRequestReviewCommentEvent', 'PushEvent', 'merged']]
    for col in event_columns:
        df[col + '_per_person'] = df[col] / df['formation_team_size']
    df = df[['name_h'] + [col for col in df.columns if col.endswith('per_person')]]
    df.to_csv("%s/events_per_person.csv" % cur_dir, index=False)


def work_events_to_work_ratio(active_teams_ids, cur_dir):
    events_file = "%s/active_repos_6months_aggregated_events.csv" % cur_dir
    df = pd.read_csv(events_file)
    df = df[df['name_h'].isin(active_teams_ids)]
    for col in work_events:
        df['percent_of_' + col + '_in_work'] = df[col] / df.work
    cols = ['name_h'] + [c for c in df.columns if c.startswith('percent')]
    df[cols].to_csv("%s/work_events_to_work_ratio.csv" % cur_dir, index=False)


# def extract_labor_division(team_members_file, detailed_events_file):
#     team_members = pd.read_csv(team_members_file)
#     events = pd.read_csv(detailed_events_file)
#     events = events[events.name_h.isin(team_members.name_h.unique().tolist())]
#     events = events[events.login_h.isin(team_members.login_h.unique().tolist())]
#     events = events[events.type.isin(work_events)]
#
#     df = events.groupby(['name_h', 'login_h'])['type'].count()
#     df = df.reset_index().groupby('name_h')
#     team_gini = {}
#     for name, group in df:
#         gini_obj = gini.Gini(np.array(group['type'].tolist()))
#         team_gini[name] = gini_obj.g
#     gini_df = pd.DataFrame([x for x in team_gini.items()], columns=['name_h', 'work_gini'])
#     gini_df.to_csv("%s/gini.csv" % cur_dir, index=False)


def extract_gini(cur_dir):
    df = pd.read_csv("%s/eval_team_members.csv" % cur_dir)
    res_df = df.groupby('name_h').apply(calc_gini)
    res_df.drop_duplicates('name_h', inplace=True)
    f = "%s/%s.csv" % (cur_dir, 'eval_gini')
    res_df[['name_h', 'eval_gini']].to_csv(f, index=False)


def calc_gini(df):
    work_list = df['total_work'].tolist()
    gini_obj = gini.Gini(work_list)
    df['eval_gini'] = gini_obj.g
    return df


if __name__ == '__main__':
    #
    # first_6m_file = "%s/first_6m_Jan.csv" % exp_dir
    # performance_1m_file = "%s/performance_1m_Jan.csv" % exp_dir
    #
    # event_features_file = "%s/all_event_features_first_6m_Jan.csv" % exp_dir
    # # extract_all_events_features(first_6m_file, event_features_file)
    #
    # feature_vectors_file = "%s/feature_vectors_first_6m_Jan.csv" % exp_dir
    # # concat_performance_and_features(event_features_file, performance_1m_file, feature_vectors_file)

    cur_day = datetime.datetime(2016, 1, 1)
    end_day = datetime.datetime(2016, 1, 31)
    while cur_day <= end_day:
        print(cur_day)
        cur_dir = "%s/created_%s" % (exp_dir, cur_day.strftime("%Y-%m-%d"))
        detailed_events_file = "%s/6months_detailed_events.csv" % cur_dir
        # active_repos_agg_events_file = "%s/active_repos_6months_aggregated_events.csv" % cur_dir
        # active_repo_ids = pd.read_csv(active_repos_agg_events_file)['name_h'].tolist()
        active_teams_file = "%s/formation_team_size_and_features.csv" % cur_dir
        active_teams_ids = pd.read_csv(active_teams_file)['name_h'].tolist()
        # team_members_file = "%s/_team_members.csv" % cur_dir

        # extract_repos_burstiness(active_teams_ids, detailed_events_file, cur_dir, feature_name='burstiness')
        # extract_repos_issue_labels(active_teams_ids, cur_day, cur_dir)
        # extract_repos_comment_feature(active_teams_ids, cur_day, cur_dir)
        extract_issue_closure_rate(active_teams_ids, cur_day, cur_dir)
        # all_events_per_person(active_teams_file, cur_dir)
        # work_events_to_work_ratio(active_teams_ids, cur_dir)
        #### extract_labor_division(team_members_file, detailed_events_file)
        # extract_gini(cur_dir)

        cur_day += datetime.timedelta(days=1)

    aggregate_feature(feature_name='eval_issue_closure_and_count')
    # add_feature(feature_name='events_per_person')

    # add_feature(feature_name='formation_issue_label')
    # add_feature(feature_name='formation_comments')
    # add_feature(feature_name='formation_burstiness')

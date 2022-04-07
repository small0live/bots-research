# Human-bot Teams in GitHub: 
# Research Article Supplement

## Purpose


This repository is used to host supplementary files for the research article, 'EveryBOTy Counts: Examining Human-Machine Teams in Open Source Software Development.'

## Contents

The repository contains both data and code files. Data files are in csv format. Code is in either R or Jupyter Notebook for Python file type. 

The data files contain information about 608 GitHub repos sampled from a data set that was collected from the GitHub API in 2017. The data variables in each file were computed at the repo level. No individual user data is included in these files. The repos represented in this data set were created in January 2016. The data have been aggregated over a period of 13 months. 

### Data


team_expertise_info_raw.csv
* Contains the data used as input for Expertise.ipynb

| Variable Name  | Variable Description | 
| :------------ |:---------------|
name_h | Alphanumeric hash generated by data provider to anonymize repo name |
Team type | A qualitative descriptor indicating whether the team was made of only humans or a blend of humans and bots (two levels: human, human-bot) |
followers | The numbers of users who follow all human users in the repo (cumulative) |
following | The numbers of users followed by all human users in the repo (cumulative) |
public_repos | The numbers of repos owned by all human users in the repo (cumulative) |
gh_impact | A quantitative measure of influence based on the stars a repo receives (an account has a gh-impact score of n if they have n projects with n stars", https://github.com/iandennismiller/gh-impact) for all human users in the repo (cumulative) |

gh_teams_research_EveryBOTy-counts.csv
* Contains the data used as input for gh_teams_research_analysis.R

| Variable Name  | Variable Description | 
| :------------ |:---------------|
| name_h | Alphanumeric hash generated to anonymize repo name |
| Team type |  A qualitative descriptor indicating whether the team was made of only humans or a blend of humans and bots (two levels: human, human-bot) |
| Team size |  A qualitative descriptor indicating the size of the team, derived from human_members_count (three levels: small [2, 3], medium [4, 6], large [7, 246]) |
| human_members_count  | The number of human users in the repo |
| bot_members_count | The number of bots in the repo |
| human_work | The number of work events generated by humans in the repo |
| work_per_human | The ratio of works events to humans, derived from human_members_count and human_work |
| human_gini | Gini coefficient for human work in the repo |
| human_Push | The number of push events generated by humans in the repo |
| human_IssueComments | The number of issue comment events generated by humans in the repo |
| human_PRReviewComment | The number of pull request review comment events generated by humans in the repo |
| human_MergedPR | The number of merged pull request events generated by humans in the repo |
| bot_work | The number of work events generated by bots in the repo |
| bot_Push | The number of push events generated by bots in the repo |
| bot_IssueComments | The number of issue comment events generated by bots in the repo |
| bot_PRReviewComment | The number of pull request review comment events generated by bots in the repo |
| bot_MergedPR | The number of merged pull request events generated by bots in the repo |
| eval_survival_day_median | The median number of days that an issue remained open in the repo (teams who were not included in issue survival analysis have NA value) |
| issues_count | The number of issues in the repo |

### Code

RepoFeatureExtraction.py
* Contains code for the extraction and calculation of productivity measures reported in our publication (data file is not included in this repo due to data sharing constraints).

Expertise.ipynb
* Contains code for smart sampling algorithm developed by Saadat and Sukthankar (2020).

gh_teams_research_analysis.R
* Contains code for statistical modeling of variable relationships reported in our publication. 

## References

Saadat, S., & Sukthankar, G. (2020). Explaining Differences in Classes of Discrete Sequences. ArXiv:2011.03371 [Cs]. http://arxiv.org/abs/2011.03371

## Citation


### APA

Newton, O. B., Saadat, S., Song, J., Sukthankar, G., & Fiore, S. M. (in press). EveryBOTy Counts: Examining Human-Machine Teams in Open Source Software Development. *Topics in Cognitive Science.* 

### ACM 

Olivia B. Newton, Samaneh Saadat, Jihye Song, Gita Sukthankar, and Stephen M. Fiore. EveryBOTy Counts: Examining Human-Machine Teams in Open Source Software Development. *Topics in Cognitive Science.*




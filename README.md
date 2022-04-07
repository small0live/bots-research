# Human-bot Teams in GitHub: Research Article Supplement

## Purpose


This repository is used to host supplementary files for the research article, 'EveryBOTy Counts: Examining Human-Machine Teams in Open Source Software Development.'

## Contents

The repository contains both data and code files. Data files are in csv format. Code is in either R or Jupyter Notebook for Python file type. 

The data files contain information about 608 GitHub repos sampled from a data set that was collected from the GitHub API in 2017. The data variables in each file were computed at the repo level. No individual user data is included in these files. The repos represented in this data set were created in January 2016. The data have been aggregated over a period of 13 months. 

### Data


team_expertise_info_raw.csv
* Contains the data used as input for Expertise.ipynb

gh_teams_research_EveryBOTy-counts.csv
* Contains the data used as input for gh_teams_research_analysis.R

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




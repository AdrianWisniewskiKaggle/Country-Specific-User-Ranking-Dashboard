# Kaggle Country-Specific User Ranking Dashboard

This project is a web application built using Dash that visualizes user rankings from a Kaggle dataset. It allows users to filter rankings based on country and achievement type, displaying the results in a dynamic data table.

![](./gifs/dashboard.mp4)

## Local
Prerequisites: anaconda/miniconda3, Kaggle Account

```bash
git clone git@gitlab.com:AdrianWisniewski/kaggle-country-competitions-ranking-dashboard.git
cd kaggle-country-competitions-ranking-dashboard
conda env create --file=environment.yml
conda activate dashboard
python scripts/dashboard.py
[optionally]: python scripts/dashboard.py --update_metadata   (Uploads latest kaggle meta-data dataset.)
[optionally]: python scripts/dashboard.py --max_page_size 100 (Defines max number of rows in rendered table.)
# Dash is running on http://0.0.0.0:8050/
```

## Docker
Prerequisites: Docker, Kaggle Account

```bash
git clone git@gitlab.com:AdrianWisniewski/kaggle-country-competitions-ranking-dashboard.git
cd kaggle-country-competitions-ranking-dashboard
docker build -t dashboard .
docker run -p 8050:8050 dashboard
[optionally]: docker run -p 8050:8050 dashboard --update_metadata (Uploads latest kaggle meta-data dataset)
[optionally]: docker run -p 8050:8050 dashboard --max_page_size   (Defines max number of rows in rendered table.)
# Dash is running on http://0.0.0.0:8050/
```
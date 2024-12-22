# Kaggle Country-Specific User Ranking Dashboard

This project is a web application built using Dash that visualizes user rankings from a Kaggle dataset. It allows users to filter rankings based on country and achievement type, displaying the results in a dynamic data table. 
> **NOTE ** This repository already contains the necessary data to create the required tables. However, please note that the current dataset file originates from December 22, 2024. If you wish to update the dataset, use the --update-metadata flag when running your command to fetch the latest data.

![](./gifs/dashboard.mp4)

## Local
Prerequisites: anaconda/miniconda3, Kaggle Account

```bash
git clone git@gitlab.com:AdrianWisniewski/kaggle-country-competitions-ranking-dashboard.git
cd kaggle-country-competitions-ranking-dashboard
conda env create --file=environment.yml
conda activate dashboard
python scripts/dashboard.py
[optionally]: python scripts/dashboard.py --update_metadata (Uploads latest kaggle meta-data dataset.)
[optionally]: python scripts/dashboard.py --max_page_size 5 (Defines max number of rows in rendered table.)
# Dash is running on http://0.0.0.0:8050/
```

## Docker
Prerequisites: Docker, Kaggle Account

```bash
git clone git@gitlab.com:AdrianWisniewski/kaggle-country-competitions-ranking-dashboard.git
cd kaggle-country-competitions-ranking-dashboard
docker build -t dashboard .
docker run -e KAGGLE_USERNAME='your_kaggle_username' -e KAGGLE_KEY='your_kaggle_key' dashboard
[optionally]: docker run -e KAGGLE_USERNAME='your_kaggle_username' -e KAGGLE_KEY='your_kaggle_key' dashboard --update_metadata (Uploads latest kaggle meta-data dataset)
[optionally]: docker run -e KAGGLE_USERNAME='your_kaggle_username' -e KAGGLE_KEY='your_kaggle_key' dashboard --max_page_size 5 (Defines max number of rows in rendered table.)
# Dash is running on http://0.0.0.0:8050/
```

> **Note:** To set up your Kaggle API authentication on Ubuntu using a hidden .kaggle directory containing your kaggle.json file, follow these steps:\
> Step 1: Create a Kaggle Account\
> Step 2: Generate the API Token: Navigate to Kaggle Profile. Scroll down to the API section and click on Create New API Token. This will download a kaggle.json file to your computer.\
> Step 3 (Local): mkdir -p ~/.kaggle\
> Step 4 (Local): mv ~/Downloads/kaggle.json ~/.kaggle/\
> Step 5 (Local): chmod 600 ~/.kaggle/kaggle.json \
> Step 6 (Docker): Open kaggle.json, use credentials as KAGGLE_USERNAME / KAGGLE_KEY in Docker.
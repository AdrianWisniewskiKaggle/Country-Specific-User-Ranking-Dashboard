#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import pandas as pd
import kaggle

class KaggleDataProcessor:
    USER_HEADER = {
        "Id": "uint32", 
        "UserName": "str",
        "DisplayName": "str",
        "PerformanceTier": "uint8",
        "Country": "str"
    }
    ACHIEVEMENTS_HEADER = {
        "UserId": "uint32", 
        "AchievementType": "str",
        "Tier": "uint8",
        "CurrentRanking": "str",
        "HighestRanking": "str",
        "TotalGold": "uint16",
        "TotalSilver": "uint16",
        "TotalBronze": "uint16",
    }

    def __init__(self, output_path="conf"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)
        
    def authenticate(self):
        """Authenticate with Kaggle."""
        kaggle.api.authenticate()

    def download_files(self, dataset_slug, files):
        """Download the specified files from the Kaggle dataset."""
        for file in files:
            kaggle.api.dataset_download_file(dataset_slug, 
                                             file, 
                                             path=self.output_path, 
                                             quiet=False)

    def load_data(self):
        """Load user and achievement data into DataFrames."""
        users = pd.read_csv(os.path.join(self.output_path, "Users.csv"),
                            usecols=self.USER_HEADER.keys(),
                            dtype=self.USER_HEADER)
        
        achievements = pd.read_csv(os.path.join(self.output_path, "UserAchievements.csv"),
                                    usecols=self.ACHIEVEMENTS_HEADER.keys(),
                                    dtype=self.ACHIEVEMENTS_HEADER).dropna(
                                        subset=['CurrentRanking', 'HighestRanking'])

        return users, achievements

    def process_data(self, users, achievements):
        """Merge and process the user and achievement data."""
        records = pd.merge(users, achievements, left_on="Id", right_on="UserId")
        records['Profile'] = "https://www.kaggle.com/" + records['UserName']
        records['CurrentRanking'] = records['CurrentRanking'].astype("uint16")
        records['HighestRanking'] = records['HighestRanking'].astype("uint16")
        
        return records

    def save_to_parquet(self, records):
        """Save the processed records to a Parquet file."""
        output_file = os.path.join(self.output_path, "records.parquet")
        records.to_parquet(output_file)

    def __call__(self, dataset_slug='kaggle/meta-kaggle'):
        """Main method to execute the download and processing pipeline."""
        self.authenticate()
        files = ['Users.csv', 'UserAchievements.csv']
        self.download_files(dataset_slug, files)
        users, achievements = self.load_data()
        records = self.process_data(users, achievements)
        self.save_to_parquet(records)

if __name__ == "__main__":
    KaggleDataProcessor()()
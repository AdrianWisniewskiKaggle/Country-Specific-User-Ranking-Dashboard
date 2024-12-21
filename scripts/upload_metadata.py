#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import kaggle
import pandas as pd

if __name__ == '__main__':
    '''
    kaggle.api.authenticate()
    files = ['Users.csv', 'UserAchievements.csv']
    for file in files:
        kaggle.api.dataset_download_file('kaggle/meta-kaggle', 
                                         file, 
                                         path=os.path.join(f"../conf"), 
                                         quiet=False)
    '''
    users = pd.read_csv("../conf/Users.csv", 
                        usecols=["Id",
                                 "UserName",
                                 "DisplayName",
                                 "PerformanceTier",
                                 "Country"],
                        dtype={"Id": "uint32", 
                               "UserName": "str",
                               "DisplayName": "str",
                               "PerformanceTier": "uint8",
                               "Country": "str"})
    achievements = pd.read_csv("../conf/UserAchievements.csv", 
                               usecols=["UserId", 
                                        "AchievementType",
                                        "Tier",
                                        "CurrentRanking",
                                        "HighestRanking",
                                        "TotalGold",
                                        "TotalSilver",
                                        "TotalBronze"],
                               dtype={"UserId": "uint32", 
                                      "AchievementType": "str",
                                      "Tier": "uint8",
                                      "CurrentRanking": "str",
                                      "HighestRanking": "str",
                                      "TotalGold": "uint16",
                                      "TotalSilver": "uint16",
                                      "TotalBronze": "uint16",}).dropna(subset=['CurrentRanking', 'HighestRanking'])
    records = pd.merge(users, achievements, left_on="Id", right_on="UserId")
    records['Profile'] = "https://www.kaggle.com/" + records['UserName']
    records['CurrentRanking'] = records['CurrentRanking'].astype("uint16")
    records['HighestRanking'] = records['HighestRanking'].astype("uint16")
    records.to_parquet("../conf/records.parquet")
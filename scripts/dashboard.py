#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from dash.dash_table import DataTable
from flask import Flask
from flask_caching import Cache
from upload_metadata import KaggleDataProcessor

class DataVisualizer:
    """A class to handle the loading and filtering of data, and the creation of a Dash application."""

    def __init__(self, data, page_size):
        self.data = data
        self.page_size = page_size
        self.app = self.create_app()

    @staticmethod
    def load_data(file_path='conf/records.parquet'):
        """Load preprocessed parquet input data."""
        return pd.read_parquet(file_path)

    @staticmethod
    def get_unique_countries(data):
        """Get a sorted list of unique countries from the dataset."""
        return sorted(data['Country'].dropna().unique())

    @staticmethod
    def get_unique_achievement_types(data):
        """Get a sorted list of unique achievement types from the dataset."""
        return sorted(data['AchievementType'].dropna().unique())

    def get_filtered_data(self, selected_country, selected_achievement_type):
        """Retrieve data based on selected criteria."""
        filtered_data = self.data.copy()
        
        if selected_country:
            filtered_data = filtered_data[filtered_data['Country'] == selected_country]
        if selected_achievement_type:
            filtered_data = filtered_data[filtered_data['AchievementType'] == selected_achievement_type]

        return filtered_data

    def create_app(self):
        """Create and configure the Dash web application."""
        server = Flask(__name__)
        app = Dash(__name__, server=server)
        cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

        app.layout = html.Div(
            style=self.layout_style(),
            children=self.get_layout_children()
        )

        @app.callback(
            Output('achievements-table', 'data'),
            [Input('country-dropdown', 'value'),
             Input('achievement-type-dropdown', 'value')]
        )
        def update_table(selected_country, selected_achievement_type):
            """Update the achievements table based on filters."""
            filtered_data = self.get_filtered_data(selected_country, selected_achievement_type)
            return self.prepare_table_data(filtered_data)

        return app

    @staticmethod
    def layout_style():
        """Return the style dictionary for the layout."""
        return {
            'height': '94vh',
            'overflow': 'hidden',
            'position': 'relative',
            'backgroundImage': 'url("https://www.toptal.com/designers/subtlepatterns/uploads/blue-snow.png")',
            'backgroundSize': 'cover'
        }

    def get_layout_children(self):
        """Return the layout children for the Dash app."""
        return [
            self.get_header(),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in self.get_unique_countries(self.data)],
                placeholder='Select a country',
                multi=False
            ),
            dcc.Dropdown(
                id='achievement-type-dropdown',
                options=[{'label': achievement_type, 'value': achievement_type} \
                         for achievement_type in self.get_unique_achievement_types(self.data)],
                value='Competitions',
                placeholder='Select Achievement Type',
                multi=False
            ),
            self.create_data_table()
        ]

    @staticmethod
    def get_header():
        """Return the header components for the layout."""
        return html.Div([
            html.H1("Kaggle", style={'textAlign': 'center', 'color': '#007bff'}),
            html.H1("Country Ranking", style={'textAlign': 'center', 'color': 'black'})
        ], style={'padding': '0px'})

    def create_data_table(self):
        """Create the DataTable component."""
        return DataTable(
            id='achievements-table',
            columns=[
                {'name': 'No.', 'id': 'No.'},
                {'name': 'DisplayName', 'id': 'DisplayName'},
                {'name': 'CurrentRanking', 'id': 'CurrentRanking'},
                {'name': 'HighestRanking', 'id': 'HighestRanking'},
                {'name': 'Country', 'id': 'Country'},
                {'name': 'Tier', 'id': 'Tier'},
                {'name': 'Medals', 'id': 'Medals', 'presentation': 'markdown'},
                {'name': 'Profile', 'id': 'Profile', 'presentation': 'markdown'},
            ],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '2px solid #007bff',
                'backgroundColor': 'rgba(255, 255, 255, 0.9)',
            },
            style_table={
                'height': '70vh',
                'overflowY': 'auto',
                'border': '3px solid #007bff',
            },
            page_size=self.page_size,  # Use the page size from the argument
            sort_action='native',
            style_header={
                'backgroundColor': '#007bff',
                'fontWeight': 'bold',
                'color': 'white',
                'border': '2px solid #007bff',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f2f2f2',
                },
                {
                    'if': {'filter_query': '{CurrentRanking} > 0', 'column_id': 'CurrentRanking'},
                    'backgroundColor': '#d4edda',
                    'color': '#155724'
                },
                {
                    'if': {'filter_query': '{CurrentRanking} <= 0', 'column_id': 'CurrentRanking'},
                    'backgroundColor': '#f8d7da',
                    'color': '#721c24'
                },
            ],
            markdown_options={"link_target": "_blank"},
        )

    def prepare_table_data(self, filtered_data):
        """Prepare data for the achievements table."""
        if not filtered_data.empty:
            # Sort by CurrentRanking and prepare the Medals column
            filtered_data = filtered_data.sort_values(by='CurrentRanking', ascending=True).reset_index(drop=True)
            filtered_data['No.'] = filtered_data.index + 1
            filtered_data['Medals'] = self.format_medals(filtered_data)
            filtered_data['Profile'] = self.format_profiles(filtered_data)

            # Map Tier values
            tier_mapping = {0: "Novice", 1: "Contributor", 2: "Expert", 3: "Master", 4: "Grandmaster"}
            filtered_data['Tier'] = filtered_data['Tier'].replace(tier_mapping)

            return filtered_data[['No.', 'DisplayName', 'CurrentRanking', 'HighestRanking', 
                                  'Country', 'Tier', 'Medals', 'Profile']].to_dict('records')

        return [{'DisplayName': 'No Data', 'CurrentRanking': 'N/A', 'HighestRanking': 'N/A',
                 'Country': 'N/A', 'Tier': 'N/A', 'Medals': 'N/A', 'No.': 'N/A', 'Profile': 'N/A'}]

    @staticmethod
    def format_medals(filtered_data):
        """Format the Medals information for display."""
        filtered_data['TotalGold'] = filtered_data['TotalGold'].fillna(0).astype(int)
        filtered_data['TotalSilver'] = filtered_data['TotalSilver'].fillna(0).astype(int)
        filtered_data['TotalBronze'] = filtered_data['TotalBronze'].fillna(0).astype(int)

        return (
            "🏅 " + filtered_data['TotalGold'].astype(str) + " " +
            "🥈 " + filtered_data['TotalSilver'].astype(str) + " " +
            "🥉 " + filtered_data['TotalBronze'].astype(str)
        )

    @staticmethod
    def format_profiles(filtered_data):
        """Format the Profile URL for display."""
        return filtered_data['Profile'].apply(lambda profile_url: f"[View Profile]({profile_url})" \
                                              if pd.notna(profile_url) else "N/A")

def main():
    """Main function to run the Dash application."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--update_metadata', action='store_true',
                        help="Whether to re-upload the latest Meta-Kaggle Dataset.")
    parser.add_argument('--max_page_size', type=int, default=250,
                        help="Max page size to render.")
    args = parser.parse_args()
    
    if args.update_metadata:
        KaggleDataProcessor()()

    data = DataVisualizer.load_data()
    visualizer = DataVisualizer(data, args.max_page_size)  # Pass the page_size argument
    visualizer.app.run_server(host='0.0.0.0', port=8050, debug=True)

if __name__ == '__main__':
    main()
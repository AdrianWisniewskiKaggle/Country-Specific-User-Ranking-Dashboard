#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from dash import Dash, dcc, html
from dash import Input, Output
from dash.dash_table import DataTable
from flask_caching import Cache

def load_data():
    """
    Load preprocessed parquet input data from:
    https://www.kaggle.com/datasets/kaggle/meta-kaggle.

    Returns:
        pd.DataFrame: DataFrame containing the loaded dataset.
    """
    data = pd.read_parquet('../conf/records.parquet')
    return data

def get_unique_countries(data):
    """Get a sorted list of unique countries from the dataset."""
    unique_countries = data['Country'].unique()
    return sorted([country for country in unique_countries if pd.notna(country)])

def get_unique_achievement_types(data):
    """Get a sorted list of unique achievement types from the dataset."""
    unique_achievement_types = data['AchievementType'].unique()
    return sorted([achievement_type for achievement_type in unique_achievement_types if pd.notna(achievement_type)])

def get_filtered_data(data, selected_country, selected_achievement_type):
    """
    Retrieve data for the selected country and achievement type.

    Parameters:
        data (pd.DataFrame): The DataFrame containing the dataset.
        selected_country (str): The name of the country to filter data for.
        selected_achievement_type (str): The type of achievement to filter data for.

    Returns:
        pd.DataFrame: Filtered DataFrame for the selected country and achievement type,
                      or the entire DataFrame if no filters are selected.
    """
    filtered_data = data.copy()
    if selected_country:
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]
    if selected_achievement_type:
        filtered_data = filtered_data[filtered_data['AchievementType'] == selected_achievement_type]
    
    return filtered_data

def create_app(data):
    """
    Create and configure the Dash web application.

    Parameters:
        data (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
        Dash: The Dash application object.
    """
    from flask import Flask
    server = Flask(__name__)
    app = Dash(__name__, server=server)
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

    @cache.memoize(timeout=60)
    def cached_get_unique_countries():
        """Cache for unique countries."""
        return get_unique_countries(data)

    app.layout = html.Div(
        style={
            'height': '100vh',
            'overflow': 'hidden',
            'position': 'relative',
            'backgroundImage': 'url("https://www.toptal.com/designers/subtlepatterns/uploads/blue-snow.png")',
            'backgroundSize': 'cover',
            'backgroundRepeat': 'no-repeat',
            'backgroundPosition': 'center'
        },
        children=[
            html.Div(
                style={
                    'padding': '0px', 
                    'backgroundColor': 'rgba(255, 255, 255, 0.8)', 
                    'marginBottom': '10px'
                }
            ),
            html.Div([
                html.H1("Kaggle", style={'textAlign': 'center', 'color': '#007bff'}),
                html.H1("Country Competitions Ranking", style={'textAlign': 'center', 'color': 'black'})
            ], style={'padding': '2px'}),

            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in cached_get_unique_countries()],
                value=None,  # Default to None for "All Countries"
                placeholder='Select a country',
                multi=False
            ),

            dcc.Dropdown(
                id='achievement-type-dropdown',
                options=[{'label': achievement_type, 'value': achievement_type} for achievement_type in get_unique_achievement_types(data)],
                value='Competitions',  # Set default to "Competitions"
                placeholder='Select Achievement Type',
                multi=False
            ),

            DataTable(
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
                page_size=250,
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
        ]
    )

    @app.callback(
        Output('achievements-table', 'data'),
        [Input('country-dropdown', 'value'),
         Input('achievement-type-dropdown', 'value')]
    )
    def update_table(selected_country, selected_achievement_type):
        """
        Update the achievements table based on the selected country and achievement type.

        Parameters:
            selected_country (str): The name of the country selected in the dropdown.
            selected_achievement_type (str): The achievement type selected in the dropdown.

        Returns:
            list: A list of dictionaries with the column data for the DataTable.
        """
        filtered_data = get_filtered_data(data, selected_country, selected_achievement_type)

        if not filtered_data.empty:
            # Sort by CurrentRanking in ascending order
            filtered_data = filtered_data.sort_values(by='CurrentRanking', ascending=True)

            # Calculate totals and prepare the Medals column
            filtered_data['TotalGold'] = filtered_data.get('TotalGold', 0).fillna(0).astype(int)
            filtered_data['TotalSilver'] = filtered_data.get('TotalSilver', 0).fillna(0).astype(int)
            filtered_data['TotalBronze'] = filtered_data.get('TotalBronze', 0).fillna(0).astype(int)

            filtered_data['Medals'] = (
                "🏅 " + filtered_data['TotalGold'].astype(str) + " " +
                "🥈 " + filtered_data['TotalSilver'].astype(str) + " " +
                "🥉 " + filtered_data['TotalBronze'].astype(str)
            )

            filtered_data = filtered_data.reset_index(drop=True)
            filtered_data['No.'] = filtered_data.index + 1  # Start numbering from 1

            # Create Profile links
            filtered_data['Profile'] = filtered_data['Profile'].apply(
                lambda profile_url: f"[View Profile]({profile_url})" if pd.notna(profile_url) else "N/A"
            )

            # Map Tier values to human-readable form
            tier_mapping = {
                0: "Novice",
                1: "Contributor",
                2: "Expert",
                3: "Master",
                4: "Grandmaster"
            }
            filtered_data['Tier'] = filtered_data['Tier'].replace(tier_mapping)

        else:
            return [{
                'DisplayName': 'No Data', 
                'CurrentRanking': 'N/A', 
                'HighestRanking': 'N/A', 
                'Country': 'N/A', 
                'Tier': 'N/A', 
                'Medals': 'N/A',
                'No.': 'N/A',
                'Profile': 'N/A'
            }]

        return filtered_data[['No.', 'DisplayName', 'CurrentRanking', 'HighestRanking',
                              'Country', 'Tier', 'Medals', 'Profile']].to_dict('records')

    return app

if __name__ == '__main__':
    data = load_data()
    app = create_app(data)
    app.run_server(host='0.0.0.0', port=8050, debug=True)
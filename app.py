# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 18:27:05 2021

@author: utente
Energy services project 2: Build dash for heroku deployment with cleaned data

Output files:
central_data.csv
general_stats.csv

cluster_data.csv
df_score_Nc.csv

scores_f.csv
scores_MI.csv
scores_RFR.csv
Recursive_elimnations.csv

forecast_df.csv
"""

#%%1. IMPORT CLEANED AND PROCESSED DATA
import pandas as pd

central_data = pd.read_csv("central_data.csv", index_col = 0)
central_data.index = pd.to_datetime(central_data.index)

general_stats = pd.read_csv("general_stats.csv", index_col = 0)

cluster_data = pd.read_csv("cluster_data.csv", index_col = 0)
df_score_Nc = pd.read_csv("df_score_Nc.csv", index_col = 0)
df_score_Nc.index += 1


df_scores_f = pd.read_csv("scores_f.csv", index_col = 0)
df_scores_MI = pd.read_csv("scores_MI.csv", index_col = 0)
df_scores_RFR = pd.read_csv("scores_RFR.csv", index_col = 0)

Recursive_eliminations = pd.read_csv("Recursive_eliminations.csv", index_col = 0)

forecast_df = pd.read_csv("forecast_df.csv", index_col = 0)

#%%3. DEFINE FUNCTIONS

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def generateHisto(scores_df):
    # tmp = pd.DataFrame(listOfTuples)
    fig = px.bar(scores_df, x = "0", y = "1")
    fig.update_layout(title_text = "Scores of the features")
    fig.update_xaxes(title_text='Features')
    fig.update_yaxes(title_text='Scores')
    return fig

#%%2. BUILD DASHBOARD
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly
import plotly.express as px

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.H2(children='IST Central Building - Energy Consumption and Forecasting'),
    dcc.Tabs(
        id='tabs', 
        value='tab-1', 
        children=[
            dcc.Tab(label='Exploratory data analysis', value='tab-1'),
            dcc.Tab(label='Clustering', value='tab-2'),
            dcc.Tab(label="Feature Selection", value = "tab-3"),
            dcc.Tab(label="Energy Forecast", value = "tab-4")
            ]
        ),
    html.Div(
        id='tabs-content'
        )
])

#RENDER TABS
@app.callback(Output(component_id='tabs-content', component_property='children'), #explicit sintax to remember how the callback works
              Input(component_id='tabs', component_property='value'))

def render_tab(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H6('Select which part of the EDA to visualize'),
            dcc.Dropdown(
                id='select-EDA',
                options=[
                    {'label': 'Raw Feature Timeseries', 'value': 'Raw Feature Timeseries'},
                    {'label': 'General Statistics', 'value': 'General Statistics'},
                    {'label': 'Boxplots', 'value': 'Boxplots'}
                ],
                value='Raw Feature Timeseries'
                ),
            html.Div(
                id="dropdown-content"
                )
        ])
    
    elif tab == 'tab-2': 
        return html.Div([
            html.H6('Clustering analysis was performed on two sets of features:'),
            dcc.Dropdown(
                id = "select-clustering-features",
                options = [
                    {"label":"Clustering 2D analysis",
                      "value":"Clustering 2D analysis"},
                    {"label":"Clustering 3D analysis",
                      "value":"Clustering 3D analysis"}],
                value = "Clustering 2D analysis"
                ),
            html.Div(
                id = "display-clustering")
        ])
    
    elif tab == 'tab-3': 
        return html.Div([
            html.H6('Select feature selection method'),
            dcc.Dropdown(
                id = "select-featureSelection",
                options = [
                    {"label":"f-function Regression", "value":"f-function Regression"},
                    {"label":"Mutual Information Regression", "value":"Mutual Information Regression"},
                    {"label":"Recursive Feature Elimination", "value":"Recursive Feature Elimination"},
                    {"label":"Random Forest Regression", "value":"Random Forest Regression"},
                    ],
                value = "Recursive Feature Elimination"
                ),
            html.Div(
                id = "featureSelection-content"
                )                      
        ])
    
    elif tab == 'tab-4':
        return html.Div([
            html.H6('Select the method for power consumption forecasting:'),
            dcc.Dropdown(
                id = "select-forecasting",
                options = [
                    {"label":"Linear Regression", 
                      "value":"Linear Regression"},
                    {"label":"Support Vector Regression",
                      "value":"Support Vector Regression"},
                    {"label":"Decision Tree Regression", 
                      "value":"Decision Tree Regression"},
                    {"label":"Random Forest Regression",
                      "value":"Random Forest Regression"},
                    {"label":"Random Forest Regression (standardized data)",
                      "value":"Random Forest Regression (standardized data)"},
                    {"label":"Gradient Boosting", 
                      "value":"Gradient Boosting"},
                    {"label":"Extreme Gradient Boosting",
                      "value":"Extreme Gradient Boosting"},
                    {"label":"Bootstrapping",
                      "value":"Bootstrapping"},
                    {"label":"Neural Networks", 
                      "value":"Neural Networks"}
                    ],
                value = "Linear Regression"),
            html.Div(
                id = "render-forecasting")
        ])

#RENDER DROPDOWN TAB 1
@app.callback(Output('dropdown-content', 'children'),
    Input('select-EDA', 'value'))

def render_EDA_dropdown(choice):
    if choice == "Raw Feature Timeseries":
        return html.Div([
            html.H6("Which feature do you want to visualize?"),
            dcc.Dropdown(
                id = "select-feature",
                options=[{"label":x, "value":x} for x in central_data.columns],
                clearable=False,
                value = "Power_kW"),
            dcc.Graph(
                id = "time-series-chart"
                ),
            ])
    
    elif choice == "General Statistics":
        return html.Div([
            html.H6("General statistics of the dataset"),
            generate_table(general_stats)
            ])
    
    elif choice == "Boxplots":
        return html.Div([
            html.H6("Choose the features"),
            dcc.Dropdown(
                id = "boxplot-feature",
                options=[{"label":x, "value":x} for x in central_data.columns],
                value = "Power_kW",
                ),
            dcc.Graph(
                id = "boxplot-graph",
                        )
                ])
    
#connecting the dropdown menu in the "raw feature timeseries" to the graph of each feature
@app.callback(Output("time-series-chart", "figure"),
              Input("select-feature", "value"))

def display_timeseries(feature):
    central_data_filt = central_data[[feature]]
    fig = px.line(central_data_filt, x=central_data_filt.index, y=central_data_filt[feature])
    fig.update_layout(title_text="Raw Timeseries with Range Slider of: "+ feature)
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                          label="1m",
                          step="month",
                          stepmode="backward"),
                    dict(count=6,
                          label="6m",
                          step="month",
                          stepmode="backward"),
                    dict(count=1,
                          label="YTD",
                          step="year",
                          stepmode="todate"),
                    dict(count=1,
                          label="1y",
                          step="year",
                          stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    return fig

#callback for the feature selection dropdown menu and checklist for the year of the boxplots
@app.callback(Output("boxplot-graph", "figure"),
              Input("boxplot-feature", "value"))

def render_boxplot(feature):
    central_data_filt = central_data[[feature]]
    fig = px.box(central_data_filt, x = central_data_filt.index.year, y = central_data_filt[feature])
    fig.update_layout(title_text = "Boxplot for 2017 and 2018 of: " + feature)
    fig.update_xaxes(title_text='Years')
    return fig

#callback for the selection of the feature selection method to display
@app.callback(Output("featureSelection-content", "children"),
              Input("select-featureSelection", "value"))

def render_FS_dropdown(methodChosen):
    if methodChosen == "f-function Regression":
        return html.Div([
            dcc.Graph(
                id = "histo1",
                figure = generateHisto(df_scores_f))
            ])
    elif methodChosen == "Mutual Information Regression":
        return html.Div([
            dcc.Graph(
                id = "histo2",
                figure = generateHisto(df_scores_MI))
            ])
    elif methodChosen == "Recursive Feature Elimination":
        return html.Div([
            html.H6("With this method are recursively identified the N best features correlated with the Power_kW variable. Choose the number of variables to compute with the RFE method using the sliders. The N-best meaningful variables are labelled with a 1 in the table."),
            html.Div(
                id = "table-RFE",
                ),
            html.P("Select the number of features using the slider:"),
            dcc.Slider(
                id='RFE-slider',
                min=1,
                max=12,
                step=1,
                value=5,
                marks={
                    i:str(i) for i in range(1, 12)
                    }
                ),
            ])
    elif methodChosen == "Random Forest Regression":
        return html.Div([
            html.H6("Insert here random forest regression"),
            dcc.Graph(
                id = "histo3",
                figure = generateHisto(df_scores_RFR))
            ])
    
#callback to link the slider to the dynamic table
@app.callback(Output("table-RFE", "children"),
              Input("RFE-slider", "value"))

def table_with_slider(n_features):
    n_features = int(n_features)
    return dash_table.DataTable(
        columns = [{"name":x, "id":x} for x in central_data.columns[1:]],
        data = Recursive_eliminations[n_features-1:n_features].to_dict("records")
        )

def generate_scatter(feature):
    cluster_data_filt = cluster_data[[feature, "Power_kW", "Clusters"]]
    fig = px.scatter(cluster_data_filt, x=feature, y="Power_kW", color="Clusters")
    fig.update_layout(title_text = "Power vs " + feature)
    fig.update_xaxes(title_text=feature)
    fig.update_yaxes(title_text="Power")
    return fig

#callback to display clustering sets of features
@app.callback(Output("display-clustering", "children"),
              Input("select-clustering-features", "value"))

def display_clustering(choice):
    if choice == "Clustering 2D analysis":
        return [html.Div([
            html.Div([
                html.P("\n\n\n\n\n\n\n\nIn this section, using the K means algorithm, the clusters of the power consumptiond data set will be analysed.\n"
                        "This analysis will be performed on the features 'Power_kW','WeekDay','Hour','Holiday','temp_C'.\n"
                        "First of all, using an elbow curve, the optimal number of clusters is identified in N = 3, then the Power Conusmption clusters are plotted for each of the features.\n"
                        )
                ], className = "six columns"),
            html.Div([
                dcc.Graph(
                    id = "Elbow Curve",
                    figure = px.line(df_score_Nc, x = df_score_Nc.index, y = df_score_Nc[df_score_Nc.columns[0]], title = "Elbow curve")
                    )
                ], className = "six columns"),
            ], style={'display': 'inline-block'}),
            html.Div([
            html.Div([
                dcc.Graph(
                    id = "scatter1",
                    figure = generate_scatter("temp_C"))
                ], className="four columns"),
            html.Div([
                dcc.Graph(
                    id = "scatter2",
                    figure = generate_scatter("Hour"))
                ], className="four columns"),
            html.Div([
                dcc.Graph(
                    id = "scatter3",
                    figure = generate_scatter("WeekDay"))
                ], className="four columns"),
            ])]
            
    elif choice == "Clustering 3D analysis":
        return html.Div([
            dcc.Graph(
                id = "clutering 3D",
                figure = px.scatter_3d(cluster_data, x = "Hour", y = "WeekDay",
                                        z = "Power_kW", color = "Clusters"))
            ])

@app.callback(Output("render-forecasting", "children"),
              Input("select-forecasting", "value"))

def render_forecasting(method_chosen):
    return html.Div([
        html.H6("Measured data vs predicted data scatterplot"),
        dcc.Graph(
            id = "scatter-forecast",
            figure = px.scatter(forecast_df, x = "Measured Data", y = method_chosen)),
        html.H6("Measured data vs predicted data line plot"),
        dcc.Graph(
            id = "time-series-forecast",
            # figure = display_forecast_timeseries(method_chosen),
            figure = px.line(forecast_df, y=["Measured Data", method_chosen])
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
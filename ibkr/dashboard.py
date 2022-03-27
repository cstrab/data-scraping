from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from datetime import timedelta
import plotly.graph_objects as go

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout design
app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div('Stock Tracker', style={'color': 'black', 'fontSize': 40})
                    ],
                    style={"width": 12, 'font-size': '20px'},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div('Start Date', style={'color': 'black', 'fontSize': 20}),
                        dcc.DatePickerSingle(id='startdate1',
                                             min_date_allowed=datetime(2022, 1, 1),
                                             date=datetime(2022, 1, 1))
                    ],
                    style={"width": 12, 'font-size': '20px'},
                ),
                dbc.Col(
                    [
                        html.Div('End Date', style={'color': 'black', 'fontSize': 20}),
                        dcc.DatePickerSingle(id='enddate1',
                                             min_date_allowed=datetime(2022, 1, 2),
                                             date=datetime(2022, 1, 2))
                    ],
                    style={"width": 12, 'font-size': '20px'},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div('Start Hour', style={'color': 'black', 'fontSize': 20}),
                        dcc.Dropdown(
                            id='dropdown1',
                            value=6,
                            options=[
                                {'label': '00:00', 'value': 23},
                                {'label': '01:00', 'value': 0},
                                {'label': '02:00', 'value': 1},
                                {'label': '03:00', 'value': 2},
                                {'label': '04:00', 'value': 3},
                                {'label': '05:00', 'value': 4},
                                {'label': '06:00', 'value': 5},
                                {'label': '07:00', 'value': 6},
                                {'label': '08:00', 'value': 7},
                                {'label': '09:00', 'value': 8},
                                {'label': '10:00', 'value': 9},
                                {'label': '11:00', 'value': 10},
                                {'label': '12:00', 'value': 11},
                                {'label': '13:00', 'value': 12},
                                {'label': '14:00', 'value': 13},
                                {'label': '15:00', 'value': 14},
                                {'label': '16:00', 'value': 15},
                                {'label': '17:00', 'value': 16},
                                {'label': '18:00', 'value': 17},
                                {'label': '19:00', 'value': 18},
                                {'label': '20:00', 'value': 19},
                                {'label': '21:00', 'value': 20},
                                {'label': '22:00', 'value': 21},
                                {'label': '23:00', 'value': 22}],
                            style={"width": '42%', 'font-size': '20px'}
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        html.Div('End Hour', style={'color': 'black', 'fontSize': 20}),
                        dcc.Dropdown(
                            id='dropdown2',
                            value=6,
                            options=[
                                {'label': '00:00', 'value': 23},
                                {'label': '01:00', 'value': 0},
                                {'label': '02:00', 'value': 1},
                                {'label': '03:00', 'value': 2},
                                {'label': '04:00', 'value': 3},
                                {'label': '05:00', 'value': 4},
                                {'label': '06:00', 'value': 5},
                                {'label': '07:00', 'value': 6},
                                {'label': '08:00', 'value': 7},
                                {'label': '09:00', 'value': 8},
                                {'label': '10:00', 'value': 9},
                                {'label': '11:00', 'value': 10},
                                {'label': '12:00', 'value': 11},
                                {'label': '13:00', 'value': 12},
                                {'label': '14:00', 'value': 13},
                                {'label': '15:00', 'value': 14},
                                {'label': '16:00', 'value': 15},
                                {'label': '17:00', 'value': 16},
                                {'label': '18:00', 'value': 17},
                                {'label': '19:00', 'value': 18},
                                {'label': '20:00', 'value': 19},
                                {'label': '21:00', 'value': 20},
                                {'label': '22:00', 'value': 21},
                                {'label': '23:00', 'value': 22}],
                            style={"width": '42%', 'font-size': '20px'}
                        ),
                    ],
                ),
            ]
        ),
        dbc.Row(
            [
                html.Button(id='button1', n_clicks=0, children='Refresh'),
            ],
                style=dict(width=2, display='table-cell')
        ),
        dbc.Row(
            [
                dcc.Graph(id='fig1',
                style={'height': '100%', 'width': '100%'}),
            ]
        ),
    ],
)

@app.callback(
    Output(component_id='fig1', component_property='figure'),
    Input(component_id='button1', component_property='n_clicks'),
    State(component_id='startdate1', component_property='date'),
    State(component_id='dropdown1', component_property='value'),
    State(component_id='enddate1', component_property='date'),
    State(component_id='dropdown2', component_property='value')
)
def update_fig(n, s1, d1, e1, d2):
    if n > 0:
        smin = 59
        sh = d1
        sdate = datetime.fromisoformat(s1).strftime("%m/%d/%Y")
        sm = int(sdate[0:2])
        sd = int(sdate[3:5])
        sy = int(sdate[-4:])
        start = datetime(year=sy, month=sm, day=sd, hour=sh, minute=smin)

        emin = 59
        eh = d2
        edate = datetime.fromisoformat(e1).strftime("%m/%d/%Y")
        em = int(edate[0:2])
        ed = int(edate[3:5])
        ey = int(edate[-4:])
        end = datetime(year=ey, month=em, day=ed, hour=eh, minute=emin)

        site = 'newark'
        tags1 = [
            "AI93529.PV",
            "AIC93528.PV",
            "AIC93528.SP",
            "AIC93528.OP",
            "DIC93527.PV",
            "FI93527.PV",
            "FIC91117.PV",
            "FIC91117.SP",
            "FIC91117.OP",
            "FIC93538.PV",
            "FIC93538.SP",
            "FIC93538.OP",

            "AI4029.PV",
            "ARC4027.PV",
            "ARC4027.SP",
            "ARC4027.OP",
            "DRC4028.PV",
            "FI4025.PV",
            "FIC91102.PV",
            "FIC91102.SP",
            "FIC91102.OP",
            "FIC4008.PV",
            "FIC4008.SP",
            "FIC4008.OP",

            "FX5127.PV",

            "AI99310.PV",
            "AI5167.PV",

            "L2:T088",
            "L2:T1016",
        ]

        new_col_name = {
            "AI93529.PV": "RST2_IC_PV",
            "AIC93528.PV": "RST2_pH_PV",
            "AIC93528.SP": "RST2_pH_SP",
            "AIC93528.OP": "RST2_pH_OP",
            "DIC93527.PV": "RST2_%_Solids",
            "FI93527.PV": "RST2_Flow",
            "FIC91117.PV": "Filter_2_Feed_Flow_PV",
            "FIC91117.SP": "Filter_2_Feed_Flow_SP",
            "FIC91117.OP": "Filter_2_Feed_Flow_OP",
            "FIC93538.PV": "Filter_2_DI_Wash_Flow_PV",
            "FIC93538.SP": "Filter_2_DI_Wash_Flow_SP",
            "FIC93538.OP": "Filter_2_DI_Wash_Flow_OP",

            "AI4029.PV": "RST4_IC_PV",
            "ARC4027.PV": "RST4_pH_PV",
            "ARC4027.SP": "RST4_pH_SP",
            "ARC4027.OP": "RST4_pH_OP",
            "DRC4028.PV": "RST4_%_Solids",
            "FI4025.PV": "RST4_Flow",
            "FIC91102.PV": "Filter_4_Feed_Flow_PV",
            "FIC91102.SP": "Filter_4_Feed_Flow_SP",
            "FIC91102.OP": "Filter_4_Feed_Flow_OP",
            "FIC4008.PV": "Filter_4_DI_Wash_Flow_PV",
            "FIC4008.SP": "Filter_4_DI_Wash_Flow_SP",
            "FIC4008.OP": "Filter_4_DI_Wash_Flow_OP",

            "FX5127.PV": "Niro_Feed_Rate_Dry",

            "AI99310.PV": "Fleck_Feed_Tank_IC",
            "AI5167.PV": "Niro_Feed_Tank_IC",

            "L2:T088": "Conductance_(Old Method)_(μS)",
            "L2:T1016": "Conductance_(New Method)_(μS)",
        }

        interval = "1m"
        pull_type = 'interpolated'
        pidata_df = get_data(site, start, end, tags1, interval, new_col_name, pull_type)
        pidata_df['Time'] = pidata_df.index
        pidata_df['Time'] = pd.to_datetime(pidata_df['Time'], infer_datetime_format=True)
        pidata_df = pidata_df[(pidata_df['Time'] > start) & (pidata_df['Time'] <= end)]

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=pidata_df['Time'],
            y=pidata_df['RST4_pH_SP'],
            line=dict(color="black"),
            showlegend=True
        ))
        fig1.add_trace(go.Scatter(
            x=pidata_df['Time'],
            y=pidata_df['RST4_pH_PV'],
            line=dict(color="lightcoral"),
            showlegend=True
        ))
        fig1 = ((
            fig1
            .update_layout(plot_bgcolor="white",
                    title='<b>Newark RST4 pH Probe/b> <br>',
                    title_x=0.5)))

        return fig1
    else:
        return ''

app.run_server(debug=False)
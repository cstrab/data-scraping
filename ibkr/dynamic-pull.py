from ib_insync import *
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import numpy as np
import asyncio

from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import datetime
import ta
from datetime import datetime
from datetime import timedelta
# from lib import stock_repo
from plotly.subplots import make_subplots
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
import plotly.graph_objects as go


#
# Pull stock price every 5 seconds update candle chart
# At end of the minute pull the 1 min data and store it into database

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

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
                # dcc.Graph(id='fig1',
                dcc.Graph(id='live-update-graph',
                style={'height': '100%', 'width': '100%'}),
                dcc.Interval(
                    id='interval-component',
                    interval=1*5000, # 5 seconds
                    n_intervals=0,
                    max_intervals=-1,)
            ]
        ),
        # dbc.Row(
        #     [
        #         html.Button(id='button1', n_clicks=0, children='Refresh'),
        #     ],
        #     style=dict(width=2, display='table-cell')
        # ),
    ],
)

@app.callback(
    # Output(component_id='fig1', component_property='figure'),
    Output(component_id='live-update-graph', component_property='figure'),
    # Input(component_id='button1', component_property='n_clicks'),
    Input(component_id='interval-component', component_property='n_intervals'),
)


def update_fig(n):
    # if n > 0:
    if n == 0:
        raise PreventUpdate
    else:
        random_id = np.random.randint(0, 9999)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=random_id, timeout=0)

        stocktik = 'PLTR'
        start = datetime.now() - timedelta(hours=9)
        stock = Stock(stocktik, 'SMART', 'USD')

        bars = ib.reqHistoricalData(
            stock,
            endDateTime=start,
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        df = util.df(bars)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df['date'],
                                      open=df['open'],
                                      high=df['high'],
                                      low=df['low'],
                                      close=df['close']))
        # fig.add_trace(go.Scatter(x=df['date'],
        #                         y=df['high']))
        return fig

app.run_server(debug=False)
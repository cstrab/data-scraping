import asyncio
from ib_insync import *
from sqlalchemy import create_engine
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
import config as cfg

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
                # dbc.Col(
                #     [
                #         html.Div('Start Date', style={'color': 'black', 'fontSize': 20}),
                #         dcc.DatePickerSingle(id='startdate1',
                #                              min_date_allowed=datetime(2022, 1, 1),
                #                              date=datetime(2022, 1, 1))
                #     ],
                #     style={"width": 12, 'font-size': '20px'},
                # ),
                # dbc.Col(
                #     [
                #         html.Div('End Date', style={'color': 'black', 'fontSize': 20}),
                #         dcc.DatePickerSingle(id='enddate1',
                #                              min_date_allowed=datetime(2022, 1, 2),
                #                              date=datetime(2022, 1, 2))
                #     ],
                #     style={"width": 12, 'font-size': '20px'},
                # ),
            ]
        ),
        # dbc.Row(
        #     [
        #         html.Button(id='button1', n_clicks=0, children='Refresh'),
        #     ],
        #         style=dict(width=2, display='table-cell')
        # ),
        dbc.Row(
            [
                dcc.Graph(id='live-update-graph',
                          style={'height': '100%', 'width': '100%'}),
                dcc.Interval(
                    id='interval-component',
                    interval=1 * 5000,  # 5 seconds
                    n_intervals=0,
                    max_intervals=-1,)
            ]
        ),
    ],
)

@app.callback(
    Output(component_id='live-update-graph', component_property='figure'),
    # Input(component_id='button1', component_property='n_clicks'),
    # State(component_id='startdate1', component_property='date'),
    # State(component_id='enddate1', component_property='date'),
    Input(component_id='interval-component', component_property='n_intervals'),
)
# def update_fig(n, s1, e1):
#     if n > 0:
def update_fig(n):
    if n == 0:
        raise PreventUpdate
    else:
        # start = datetime.fromisoformat(s1)
        # end = datetime.fromisoformat(e1)
        #
        # df = stock_repo.get_stock_data(start,end)

        random_id = np.random.randint(0, 9999)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=random_id, timeout=0)

        stocktik = 'PLTR'
        start = datetime.now() - timedelta(hours=9)
        stock = Stock(stocktik, 'SMART', 'USD')

        # if start is 00 sec we want to save data to add datapoint to database
        # otherwise keep pulling

        bars = ib.reqHistoricalData(
            stock,
            endDateTime=start,
            durationStr='3600 S',
            barSizeSetting='1 min',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        # bars2 = ib.reqHistoricalData(
        #     stock,
        #     endDateTime=start,
        #     durationStr='1 D',
        #     barSizeSetting='1 min',
        #     whatToShow='VOLUME',
        #     useRTH=True
        # )
        df = util.df(bars)
        # df2 = util.df(bars2)
        df = df.reset_index().set_index('date')
        # df.drop('volume', axis=1, inplace=True)
        # df2 = df2.reset_index().set_index('date')
        # pd.merge(df, df2, left_index=True, right_index=True)
        loop.close()

        if start.isoformat('T')[17:19] == "00":
            engine = create_engine(f'postgresql://{cfg.DATABASE_USER}:{cfg.DATABASE_PASSWORD}@{cfg.DATABASE_HOST}:{cfg.DATABASE_PORT}/{cfg.DATABASE_NAME}')
            df.head(1).to_sql('TEST', engine, if_exists='append')

        # Indicators
        bb_indicator = BollingerBands(df['close'])
        df['upper_band'] = bb_indicator.bollinger_hband()
        df['lower_band'] = bb_indicator.bollinger_lband()
        df['moving_average'] = bb_indicator.bollinger_mavg()

        # Add moving averages
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma5'] = df['close'].rolling(window=5).mean()

        # RSI indicator
        rsi_indicator = RSIIndicator(df['close'])
        df['rsi'] = rsi_indicator.rsi()

        # MACD
        macd = MACD(close=df['close'],
                    window_slow=26,
                    window_fast=12,
                    window_sign=9)

        # Stochastic
        stoch = StochasticOscillator(high=df['high'],
                                     close=df['close'],
                                     low=df['low'],
                                     window=14,
                                     smooth_window=3)

        # Candlestick Chart
        # fig1 = go.Figure()
        fig1 = make_subplots(rows=4, cols=1, shared_xaxes=True,
                             vertical_spacing=0.01,
                             row_heights=[0.5, 0.1, 0.2, 0.2])

        fig1.add_trace(go.Candlestick(x=df.index,
                                      open=df['open'],
                                      high=df['high'],
                                      low=df['low'],
                                      close=df['close']), row=1, col=1)
        # removing rangeslider
        # fig1.update_layout(xaxis_rangeslider_visible=False)

        # Upper band line
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df['upper_band'],
            fill=None,
            mode='lines',
            line=dict(color="lightgray"),
            showlegend=True
        ), row=1, col=1)

        # Lower band line
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df['lower_band'],
            fill='tonexty',
            mode='lines',
            line=dict(color="lightgray"),
            showlegend=True
        ), row=1, col=1)

        # Moving average line
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df['moving_average'],
            fill=None,
            line=dict(color="black"),
            showlegend=True
        ), row=1, col=1)

        # Moving average 20 - I think this is the same as 'moving_average
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df['ma20'],
            fill=None,
            line=dict(color="yellow"),
            showlegend=True
        ), row=1, col=1)

        # Moving average 20
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df['ma5'],
            fill=None,
            line=dict(color="purple"),
            showlegend=True
        ), row=1, col=1)

        # Want this as a subplot
        # fig1.add_trace(go.Scatter(
        #     x=df.index,
        #     y=df['rsi'],
        #     fill=None,
        #     line=dict(color="orange"),
        #     showlegend=True
        # ), row=1, col=1)

        # Volume - dont currently have this need to pull additional data
        # colors = ['green' if row['open'] - row['close'] >= 0
        #           else 'red' for index, row in df.iterrows()]
        # fig1.add_trace(go.Bar(x=df.index,
        #                      y=df['volume'],
        #                      marker_color=colors
        #                      ), row=2, col=1)

        # MACD
        colors = ['green' if val >= 0
                  else 'red' for val in macd.macd_diff()]
        fig1.add_trace(go.Bar(x=df.index,
                             y=macd.macd_diff(),
                             marker_color=colors
                             ), row=3, col=1)
        fig1.add_trace(go.Scatter(x=df.index,
                                 y=macd.macd(),
                                 line=dict(color='black', width=2)
                                 ), row=3, col=1)
        fig1.add_trace(go.Scatter(x=df.index,
                                 y=macd.macd_signal(),
                                 line=dict(color='blue', width=1)
                                 ), row=3, col=1)

        # Stochastics
        fig1.add_trace(go.Scatter(x=df.index,
                                 y=stoch.stoch(),
                                 line=dict(color='black', width=2)
                                 ), row=4, col=1)
        fig1.add_trace(go.Scatter(x=df.index,
                                 y=stoch.stoch_signal(),
                                 line=dict(color='blue', width=1)
                                 ), row=4, col=1)

        # Removing weekends and outside normal trading hours
        fig1.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 9.5], pattern='hour')])

        # Does not currently work......
        # Removing all empty dates, including holidays
        # Build complete timeline from start date to end date
        dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
        # Retrieve the dates that ARE in the original datset
        dt_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in pd.to_datetime(df.index)]
        # Define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d %H:%M:%S").tolist() if not d in dt_obs]
        fig1.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

        # update y-axis label
        fig1.update_yaxes(title_text="Price", row=1, col=1)
        fig1.update_yaxes(title_text="Volume", row=2, col=1)
        fig1.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
        fig1.update_yaxes(title_text="Stoch", row=4, col=1)

        # update layout by changing the plot size, hiding legends & rangeslider, and removing gaps between dates
        fig1.update_layout(height=900, #width=1200,
                          showlegend=False,
                          xaxis_rangeslider_visible=False,
                          xaxis_rangebreaks=[dict(values=dt_breaks)])

        fig1 = ((
            fig1
            .update_layout(plot_bgcolor="white",
                    title='<b>Technical Analysis</b> <br>',
                    title_x=0.5)))

        return fig1

app.run_server(debug=False)

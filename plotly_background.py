import plotly.graph_objects as go
from time import time,sleep
# Create random data with numpy
import numpy as np
import pandas as pd
import time
import os
from uuid import uuid4

import dash
from dash import DiskcacheManager, CeleryManager, html

import datetime as dt
from dash import Dash, html, dcc, Input, Output
from dash.dependencies import Input, Output
# from flask_caching import Cache
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


launch_uid = uuid4()

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(
        celery_app, cache_by=[lambda: launch_uid], expire=60
    )

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(
        cache, cache_by=[lambda: launch_uid], expire=60
    )

app = Dash(__name__, background_callback_manager=background_callback_manager, external_stylesheets=external_stylesheets)
# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })

# TIMEOUT = 600


def query_data():
    return pd.read_json(generate_data(), orient='split')

app.layout = html.Div([
    #html.Div('Data was updated within the last {} seconds'.format(TIMEOUT)),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(Output('live-graph', 'figure'),
              Input('interval-component', 'n_intervals'),
              background=True,
              manager=background_callback_manager)
def update_live_graph(n_intervals):
    now = dt.datetime.now()
    df2 = query_data()

    return {
        'data': [{
            'name': 'price_1',
            'x': df2['delivery_begin'],
            'y': df2["price"],
            'line': {
                'width': 1,
                'color': '#0074D9',
                'shape': 'line'
            }
        },
        {
            'name': 'price_2',
            'x': df2['delivery_begin'],
            'y': df2["price"]+100,
            'line': {
                'width': 1,
                'color': '#000000',
                'shape': 'line'
            }
        }
        
        ],
        "layout":{
            'legend': {'title': {'font': {'color': 'green'}}},
            'title': {'font': {'color': 'red', 'family': 'Times New Roman'}, 'text': 'Sample name'},
            'xaxis': {'title': {'font': {'family': 'Arial'}, 'text':'time'}},
            'yaxis': {'title': {'font': {'family': 'Arial'}, 'text':'price'}}
        }
    }

def generate_data():
    rng = np.random.default_rng()
    raw_curve = pd.DataFrame(pd.date_range('2022-01-01','2027-06-01',freq='H'),columns=['delivery_begin'])
    raw_curve = raw_curve.assign(price = 100 * rng.random((len(raw_curve),)) + 10)
    raw_curve['price'] = raw_curve['price'].round(2)

    return raw_curve.to_json(date_format='iso', orient='split')



if __name__ == '__main__':
    app.run_server(debug=True)


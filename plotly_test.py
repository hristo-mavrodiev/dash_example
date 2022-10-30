import plotly.graph_objects as go
from time import time,sleep
# Create random data with numpy
import numpy as np
import pandas as pd


import datetime as dt
from dash import Dash, html, dcc, Input, Output
from dash.dependencies import Input, Output
from flask_caching import Cache
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 600

# @cache.memoize(timeout=TIMEOUT)
# def query_data():
#     # This could be an expensive data querying step
#     np.random.seed(0)  # no-display
#     df = pd.DataFrame(
#         np.random.randint(0, 100, size=(100, 4)),
#         columns=list('ABCD')
#     )
#     now = dt.datetime.now()
#     df['time'] = [now - dt.timedelta(seconds=5*i) for i in range(100)]
#     return df.to_json(date_format='iso', orient='split')


def query_data():
    return pd.read_json(generate_data(), orient='split')

app.layout = html.Div([
    html.Div('Data was updated within the last {} seconds'.format(TIMEOUT)),
    dcc.Dropdown(["DE","NL","BE",'TT'], 'TT', id='live-dropdown'),
    dcc.Graph(id='live-graph')
])


@app.callback(Output('live-graph', 'figure'),
              Input('live-dropdown', 'value'))
def update_live_graph(value):
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
            'y': df2["price"],
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

@cache.memoize(timeout=TIMEOUT)
def query_data():
    print("sleeping..20")
    sleep(20)
    rng = np.random.default_rng()
    raw_curve = pd.DataFrame(pd.date_range('2022-01-01','2027-06-01',freq='H'),columns=['delivery_begin'])
    raw_curve = raw_curve.assign(price = 100 * rng.random((len(raw_curve),)) + 10)
    raw_curve['price'] = raw_curve['price'].round(2)

    return raw_curve.to_json(date_format='iso', orient='split')



if __name__ == '__main__':
    app.run_server(debug=True)


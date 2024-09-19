import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from flask import session

def create_rain_sum_chart(server):
    app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash_rain_sum/')

    app.layout = html.Div([
        dcc.Graph(id='rain-sum-graph')
    ], style={})

    @app.callback(
        Output('rain-sum-graph', 'figure'),
        [Input('rain-sum-graph', 'id')]
    )
    def update_graph(_):
        rain_sum_data_json = session.get('rain_sum_data', None)
        if rain_sum_data_json:
            rain_sum_df = pd.read_json(rain_sum_data_json)
            x_data = rain_sum_df['date']
            y_data = rain_sum_df['rain_sum']
        else:
            x_data = []
            y_data = []

        figure = {
            'data': [
                go.Bar(
                    x=x_data,
                    y=y_data,
                    name='Daily Rain Sum',
                    marker=dict(color='#5A65DC')
                )
            ],
            'layout': go.Layout(
                title='Daily Rain Sum',
                xaxis={'title': 'Date', 'color': 'white', 'tickfont': dict(color='white')},
                yaxis={'title': 'Rain Sum (mm)', 'color': 'white', 'tickfont': dict(color='white')},
                hovermode='closest',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white')
            )
        }
        return figure

    return app

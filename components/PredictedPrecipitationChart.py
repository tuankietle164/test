import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from flask import session

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')

    app.layout = html.Div([
        dcc.Graph(id='precipitation-graph')
    ])
    
    @app.callback(
        Output('precipitation-graph', 'figure'),
        [Input('precipitation-graph', 'id')]
    )
    def update_graph(_):
        # Lấy dữ liệu dự đoán từ session Flask
        pred_data_json = session.get('pred_data', None)

        if pred_data_json:
            pred_df = pd.read_json(pred_data_json)
            x_data = pred_df['date']
            y_data = pred_df['predicted_precipitation_sum']
        else:
            x_data = []
            y_data = []

        figure = {
            'data': [
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name='Predicted Precipitation',
                    line=dict(color='yellow')
                )
            ],
            'layout': go.Layout(
                xaxis={'title': 'Date', 'color': 'white', 'tickfont': dict(color='white')},
                yaxis={'title': 'Predicted Precipitation Sum (mm)', 'color': 'white', 'tickfont': dict(color='white')},
                hovermode='closest',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
        }
        return figure

    return app

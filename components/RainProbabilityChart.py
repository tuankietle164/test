import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from flask import session

def create_rain_probability_chart(server):
    # Tạo Dash app để hiển thị biểu đồ xác suất mưa
    app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash_rain_probability/')

    app.layout = html.Div([
        dcc.Graph(id='rain-probability-graph')
    ], style={})

    @app.callback(
        Output('rain-probability-graph', 'figure'),
        [Input('rain-probability-graph', 'id')]
    )
    def update_graph(_):
        # Lấy dữ liệu từ session Flask
        probabilities = session.get('precipitation_probabilities_14d', [])
        
        # Đảm bảo rằng probabilities là một danh sách và không bị lỗi
        if not isinstance(probabilities, list) or len(probabilities) == 0:
            probabilities = [0] * 14  # Giá trị mặc định nếu không có dữ liệu

        # Tạo ngày hiển thị cho biểu đồ
        dates = pd.date_range(start=pd.Timestamp.today(), periods=14)

        # Xử lý dữ liệu x và y cho biểu đồ
        x_data = [date.strftime('%Y-%m-%d') for date in dates]
        y_data = probabilities

        # Thiết lập cấu trúc biểu đồ
        figure = {
            'data': [
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name='Rain Probability for the Next 14 Days',
                    line=dict(color='#5A65DC')
                )
            ],
            'layout': go.Layout(
                title='Rain Probability for the Next 14 Days',
                xaxis={'title': 'Date', 'color': 'white', 'tickfont': dict(color='white')},
                yaxis={'title': 'Probability (%)', 'color': 'white', 'tickfont': dict(color='white')},
                hovermode='closest',
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Nền trong suốt
                paper_bgcolor='rgba(0, 0, 0, 0)',  # Nền trong suốt cho toàn bộ biểu đồ
                font=dict(color='white'),
                height=500  # Chiều cao biểu đồ là 500px
            )
        }
        return figure

    return app

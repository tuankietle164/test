import plotly.express as px
import plotly.io as pio

def create_temperature_map(weather_data, location_name, lat, lon):
    # Lấy dữ liệu cho nhiều tọa độ xung quanh
    nearby_coords = [
        {'lat': lat + 0.1, 'lon': lon + 0.1},
        {'lat': lat - 0.1, 'lon': lon - 0.1},
        {'lat': lat + 0.05, 'lon': lon - 0.05},
        {'lat': lat - 0.05, 'lon': lon + 0.05},
        {'lat': lat + 0.08, 'lon': lon + 0.08},
        {'lat': lat - 0.08, 'lon': lon - 0.08},
        {'lat': lat + 0.07, 'lon': lon - 0.07},
        {'lat': lat - 0.07, 'lon': lon + 0.07}
    ]
    
    # Lấy nhiệt độ cho từng tọa độ
    temperature_values = [weather_data['daily']['temperature_2m_max'][0]] * 9  # Điều chỉnh để có 9 phần tử
    location_names = [location_name] + [f"{location_name} nearby {i+1}" for i in range(8)]
    
    latitudes = [lat] + [coord['lat'] for coord in nearby_coords]
    longitudes = [lon] + [coord['lon'] for coord in nearby_coords]

    # Tạo biểu đồ map với Plotly
    fig = px.scatter_mapbox(
        lat=latitudes, 
        lon=longitudes, 
        text=[f"Max Temp: {temp}°C" for temp in temperature_values],
        zoom=10,
        mapbox_style="open-street-map",
        hover_name=location_names,
        size=temperature_values,  # Bubble size dựa trên giá trị nhiệt độ
        size_max=50,  # Kích thước tối đa của bubble
        color=temperature_values,  # Màu sắc dựa trên giá trị nhiệt độ
        color_continuous_scale=[  # Thang màu liên tục dựa trên nhiệt độ
            [0, "darkblue"],  # Nhiệt độ rất thấp (< -29.5°C)
            [0.2, "lightblue"],  # Nhiệt độ thấp (-15°C đến -9.5°C)
            [0.4, "yellow"],  # Nhiệt độ trung bình (0°C đến 5°C)
            [0.6, "orange"],  # Nhiệt độ cao (20°C đến 30°C)
            [0.8, "red"],  # Nhiệt độ rất cao (> 30°C)
            [1, "darkred"]  # Nhiệt độ cực kỳ cao
        ]
    )

    # Cập nhật layout với thanh chú thích chi tiết cho từng mốc màu
    fig.update_layout(
        mapbox=dict(center=dict(lat=lat, lon=lon)),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Temperature (°C / °F)",  # Tiêu đề cho thanh chú thích
            tickvals=[-30, -20, -10, 0, 10, 20, 30, 40],  # Các mốc giá trị cho Centigrade
            ticktext=[  # Nhãn cho các mốc nhiệt độ Centigrade và Fahrenheit
                "< -29.5°C / < -21°F", 
                "-29.5 to -15°C / -20.5 to 5°F", 
                "-15 to -5°C / 5 to 23°F", 
                "-5 to 5°C / 23 to 41°F", 
                "5 to 15°C / 41 to 59°F", 
                "15 to 25°C / 59 to 77°F", 
                "25 to 35°C / 77 to 95°F", 
                "> 35°C / > 95°F"
            ],
            ticks="outside",  # Hiển thị ticks bên ngoài thanh
            len=0.75,  # Độ dài của thanh
            thickness=20,  # Độ dày của thanh
            x=1.05  # Vị trí của thanh chú thích nằm bên phải bản đồ
        )
    )

    # Render bản đồ ra HTML
    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

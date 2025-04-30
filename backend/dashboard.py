import plotly.graph_objs as go
import plotly.io as pio

def create_dashboard():
    # Example Plotly graph
    fig = go.Figure(data=[
        go.Bar(x=['A', 'B', 'C'], y=[4, 7, 2])
    ])
    
    # Return the div to embed in HTML
    dashboard_html = pio.to_html(fig, full_html=False)
    return dashboard_html

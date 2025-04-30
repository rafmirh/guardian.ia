# dashboard.py

import plotly.graph_objs as go
import plotly.io as pio

class Dashboard:
    def __init__(self):
        self.figures = []

    def add_bar_chart(self, x, y, title="Bar Chart"):
        fig = go.Figure(data=[go.Bar(x=x, y=y)])
        fig.update_layout(title=title)
        self.figures.append(fig)

    def add_line_chart(self, x, y, title="Line Chart"):
        fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='lines+markers')])
        fig.update_layout(title=title)
        self.figures.append(fig)

    def add_pie_chart(self, labels, values, title="Pie Chart"):
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title=title)
        self.figures.append(fig)

    def render_dashboard(self):
        # Convert each figure to HTML and combine
        html_parts = [
            pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
            for fig in self.figures
        ]
        return "\n".join(html_parts)


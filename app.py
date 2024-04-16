from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly  # Add this line to import the plotly module

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    df = None
    pie_data = None
    bar_data = None
    chart_data = None

    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            df = pd.read_csv(file)
            if 'Department_Name' not in df.columns:
                return 'Error: Department_Name column not found in CSV file'

            pie_data = df['Department_Name'].value_counts()
            bar_data = df.groupby('Department_Name')['Division'].sum().reset_index()

            pie_chart = px.pie(pie_data, values=pie_data.values, names=pie_data.index, title='Pie Chart')
            bar_chart = px.bar(bar_data, x='Department_Name', y='Division', title='Bar Chart')

            pie_chart_title = pie_chart.layout.title.text
            pie_chart_layout = pie_chart.layout.to_plotly_json()

            bar_chart_title = bar_chart.layout.title.text
            bar_chart_layout = bar_chart.layout.to_plotly_json()

            # Combine pie and bar charts into one plot
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=[[{"type": "domain"}], [{"type": "bar"}]])

            fig.add_trace(go.Pie(labels=pie_data.index, values=pie_data.values, name='Pie Chart'), row=1, col=1)
            fig.add_trace(go.Bar(x=bar_data['Department_Name'], y=bar_data['Division'], name='Bar Chart'), row=2, col=1)

            fig.update_layout(title_text='Pie and Bar Charts', height=800, width=1000)

            chart_data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', df=df, chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import plotly.express as px
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import date
import plotly  

app = Flask(__name__)
app.secret_key = 'secret_key'  # Set a secret key for session

@app.route('/', methods=['GET', 'POST'])
def index():
    df = None
    pie_data = None
    bar_data = None
    chart_data = None

    # Cek tanggal hari ini
    today = date.today()

    if request.method == 'POST':
        files = request.files.getlist('files')
        
        # Periksa jumlah file yang diunggah
        if len(files) > 2:
            return redirect(url_for('register_page'))

        # Inisialisasi jumlah file yang diunggah hari ini
        if 'upload_count' not in session:
            session['upload_count'] = 0
            session['upload_date'] = today

        # Reset jumlah unggahan jika sudah melewati hari
        if session['upload_date'] != today:
            session['upload_count'] = 0
            session['upload_date'] = today

        data_frames = []
        for file in files:
            if file.filename == '':
                return 'No selected file'
            
            df = pd.read_csv(file)
            data_frames.append(df)
            session['upload_count'] += 1  # Tambahkan jumlah file yang diunggah

        # Gabungkan semua DataFrames jika ada lebih dari satu file yang diunggah
        if len(data_frames) > 0:
            df = pd.concat(data_frames)

        if df is not None:
            if 'Department_Name' not in df.columns:
                return 'Error: Department_Name column not found in CSV file'
            
            pie_data = df['Department_Name'].value_counts()
            bar_data = df.groupby('Department_Name')['Division'].sum().reset_index()

            pie_chart = px.pie(pie_data, values=pie_data.values, names=pie_data.index, title='Pie Chart')
            bar_chart = px.bar(bar_data, x='Department_Name', y='Division', title='Bar Chart')

            pie_chart_layout = pie_chart.layout.to_plotly_json()
            bar_chart_layout = bar_chart.layout.to_plotly_json()

            # Kombinasikan pie dan bar charts ke dalam satu plot
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=[[{"type": "domain"}], [{"type": "bar"}]])

            fig.add_trace(go.Pie(labels=pie_data.index, values=pie_data.values, name='Pie Chart'), row=1, col=1)
            fig.add_trace(go.Bar(x=bar_data['Department_Name'], y=bar_data['Division'], name='Bar Chart'), row=2, col=1)

            fig.update_layout(title_text='Pie and Bar Charts', height=800, width=1000)

            chart_data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Baca jumlah total file yang diunggah hari ini
    upload_count_today = session.get('upload_count', 0)

    return render_template('index.html', df=df, chart_data=chart_data, upload_count_today=upload_count_today)

@app.route('/register_page')
def register_page():
    return render_template('register.html', title='CekatanBiz - Register')

@app.route('/login_page')
def login_page():
    return render_template('login.html', title='CekatanBiz - Login')

@app.route('/forgetpass_page')
def forgetpass_page():
    return render_template('forgetpass.html', title='CekatanBiz - Forget Password')

if __name__ == '__main__':
    app.run(debug=True)

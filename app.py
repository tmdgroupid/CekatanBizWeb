from flask import Flask, render_template, request
from pyspark.sql import SparkSession
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')
def beranda():
    return render_template('index.html', title='CekatanBiz - Upload File Dataset')

@app.route('/uploadfile', methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            filename = file.filename
            file.save(filename)
            return render_template("result-analyst.html", title='CekatanBiz - Result Analyst', name=filename)
        else:
            return render_template("index.html", title='CekatanBiz - Upload File Dataset', error="File must be in CSV format.")
    
    return render_template("index.html", title='CekatanBiz - Upload File Dataset')

@app.route('/analyst/<filename>')
def analyst(filename):
    spark = SparkSession.builder.appName('Data Analyst').getOrCreate()
    df = spark.read.csv(filename, header=True, inferSchema=True)
    
    # Analisis data menggunakan PySpark
    pie_data = df.groupBy('category').count().toPandas()
    bar_data = df.groupBy('category').sum('value').toPandas()

    # Menggambar chart pie
    pie_data.plot.pie(y='count', labels=pie_data['category'], autopct='%1.1f%%', legend=False)
    plt.title('Pie Chart')
    pie_chart = io.BytesIO()
    plt.savefig(pie_chart, format='png')
    pie_chart = base64.b64encode(pie_chart.getvalue()).decode('utf-8')
    plt.close()

    # Menggambar chart bar
    bar_data.plot.bar(x='category', y='sum(value)', legend=False)
    plt.title('Bar Chart')
    bar_chart = io.BytesIO()
    plt.savefig(bar_chart, format='png')
    bar_chart = base64.b64encode(bar_chart.getvalue()).decode('utf-8')
    plt.close()

    return render_template("result-analyst.html", title='CekatanBiz - Analyst', filename=filename, pie_chart=pie_chart, bar_chart=bar_chart)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

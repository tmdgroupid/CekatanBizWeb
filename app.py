from flask import Flask, render_template, request
from pyspark.sql import SparkSession
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file.save(filename)

            # Inisialisasi Spark Session
            spark = SparkSession.builder \
                .appName('Tools Data Analyst and Business Analyst') \
                .getOrCreate()

            # Load file CSV menjadi DataFrame Spark
            df = spark.read.option('header', 'true').csv(filename)

            # Menghitung jumlah data kategorikal untuk chart Pie
            pie_data = df.groupBy('Category').count().collect()
            pie_data = [(row['Category'], row['count']) for row in pie_data]

            # Menghitung jumlah data numerikal untuk chart Bar
            bar_data = df.groupBy('Category').agg({'Value': 'sum'}).collect()
            bar_data = [(row['Category'], row['sum(Value)']) for row in bar_data]

            # Menghapus file CSV yang diunggah
            os.remove(filename)

            return render_template('index.html', pie_data=pie_data, bar_data=bar_data)

if __name__ == '__main__':
    app.run(debug=True)

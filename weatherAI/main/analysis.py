import numpy as np
import pandas as pd
import plotly.express as px
import datetime
import os
import pandas as pd
from django.conf import settings

def load_data():
    # بناء المسار الكامل للملف
    file_path = os.path.join(settings.BASE_DIR, 'main', 'data', 'cleaned_data.csv')

    # قراءة الملف
    df = pd.read_csv(file_path)
    return df

def analysis(start_date, end_date):
    df = load_data()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[(df['datetime'] >= pd.to_datetime(start_date)) & (df['datetime'] <= pd.to_datetime(end_date))]
    visualizations = {}

    # Temperature Visualizations
    fig = px.scatter(x=df['datetime'], y=df['tempmax'], title='Max Temperature in Mansoura')
    visualizations['tempmax'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['tempmin'], title="Min Temperature in Mansoura")
    visualizations['tempmin'] = fig.to_html(full_html=False)

    fig = px.line(df, x='datetime', y=['tempmax', 'tempmin', 'temp'], title='Temperature Distribution')
    visualizations['temp_dist'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['temp'], title='Average Temperature')
    visualizations['temp'] = fig.to_html(full_html=False)

    # Feels Like Temperature
    fig = px.scatter(x=df['datetime'], y=df['feelslikemax'], title='Feels Like Max Temperature')
    visualizations['feelslikemax'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['feelslikemin'], title='Feels Like Min Temperature')
    visualizations['feelslikemin'] = fig.to_html(full_html=False)

    # Other Weather Parameters
    fig = px.scatter(x=df['datetime'], y=df['humidity'], title='Humidity Over Time')
    visualizations['humidity'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['sealevelpressure'], title='Sea Level Pressure Over Time')
    visualizations['sealevelpressure'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['cloudcover'], title='Cloud Cover Over Time')
    visualizations['cloudcover'] = fig.to_html(full_html=False)

    fig = px.scatter(x=df['datetime'], y=df['moonphase'], title='Moon Phase Over Time')
    visualizations['moonphase'] = fig.to_html(full_html=False)

    # Precipitation Type (Pie Chart)
    precip_counts = df['preciptype'].value_counts().reset_index()
    precip_counts.columns = ['preciptype', 'count']
    fig = px.pie(precip_counts, names='preciptype', values='count', title='Precipitation Type Distribution')
    visualizations['preciptype'] = fig.to_html(full_html=False)

    return visualizations
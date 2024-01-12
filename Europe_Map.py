import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import streamlit as st
import pandas as pd
import geopandas as gpd
from functions import *
disease_to_variable = {
    'Cancer': 'ph006d10',
    'Alzheimer': 'ph006d16',
    'Parkinson': 'ph006d12',
    'Diabetes': 
    'ph006d5',
}
year_to_wave = {
    2004: 1,
    2006: 2,
    2008: 3,
    2011: 4,
    2013: 5,
    2015: 6,
    2017: 7,
    2019: 8
}

# title
st.title('Disease in Europe')
st.markdown('#### This app shows the prevalence of various diseases in Europe. The data is from the Survey of Health, Ageing and Retirement in Europe (SHARE).')
st.markdown('#### The map shows the prevalence of the disease in each country. The darker the color, the higher the prevalence.')
space(3)

# select disease and wave
st.markdown('#### Select disease and year:')
col1, col2 = st.columns(2)
with col1:
    disease = st.selectbox('Disease:', ['Cancer', 'Alzheimer', 'Parkinson', 'Diabetes'], key='disease')
    variable = disease_to_variable[disease]
with col2:
    year = st.selectbox('Year:', [2004, 2006, 2008, 2011, 2013, 2015, 2017, 2019], key='year')
    wave = year_to_wave[year]

# open datasets
world = gpd.read_file('data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')
try:
    df = open_dataset(disease, wave)
    df_geo = convert_to_geojson(world, df, disease)

    # select countries from user
    st.markdown('#### Select countries to display:')
    countries = st.multiselect('Countries:', df_geo['NAME'].unique())

    # create map
    plot_map(df_geo, wave, disease, countries)

    # plot raw data
    space(2)
    if st.checkbox('Show raw data'):
        df_to_display = df.copy()
        df_to_display[disease] = round(df_to_display[disease]*100,2)
        st.write(df_to_display.transpose())
except FileNotFoundError:
    st.error('Data not available for this specific year and disease.')
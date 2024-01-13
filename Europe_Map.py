try:

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import streamlit as st
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    from functions import *
    disease_to_variable = {
        'Cancer': 'ph006d10',
        'Alzheimer': 'ph006d16',
        'Parkinson': 'ph006d12',
        'Diabetes': 'ph006d5',
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
    st.markdown('''#### This app shows the prevalence of various diseases in Europe. The data is from the Survey of Health, Ageing and Retirement in Europe (SHARE) The map shows the prevalence of the disease in each country. The darker the color, the higher the prevalence.''')
    st.markdown('#### You can see the full code on the [GitHub repository](https://github.com/JosephBARBIERDARNAL/Viz-Europe-Map)')
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
        display_all = st.checkbox('Display all countries', key='display_all')
        if display_all:
            countries = np.sort(df_geo['NAME'].unique())
        else:
            countries = st.multiselect('Countries:', np.sort(df_geo['NAME'].unique()))

        # create map
        chart = plot_map(df_geo, wave, disease, countries)

        space(2)
        
        # plot raw data
        with open(f'{disease}_wave{wave}.png', "rb") as file:
            st.download_button(
                label='Download chart',
                data=file,
                file_name=f'{disease}_wave{wave}',
                mime='image/png'
            )

    # download chart button
        if st.checkbox('Show raw data'):
            df_to_display = df.copy()
            df_to_display[disease] = round(df_to_display[disease]*100,2).astype(str) + '%'
            st.write(df_to_display.transpose())
    except FileNotFoundError:
        st.error('Data not available for this specific year and disease.')


    # CIERI Analytics Streamlit footer
    space(5)
    st.write('---')
    st.markdown("This web page is the work of [CIERI Analytics](https://www.cieri-analytics.com/), a French organization that aims is to develop data science tools for social sciences.")
    st.markdown("If you found this tool useful, found a bug or have a suggestion, please contact us at joseph.barbierdarnal@gmail.com or open an issue on [GitHub](https://github.com/JosephBARBIERDARNAL/ChereDoc).")

except Exception as e:
    st.error('Something went wrong. Try again later or change the parameters.')
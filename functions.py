import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
import streamlit as st

code_to_name = {
    'ph006d10': 'Cancer',
    'ph006d16': 'Alzheimer',
    'ph006d12': 'Parkinson',
    'ph006d5': 'Diabetes',
}

wave_to_year = {
    1: 2004,
    2: 2006,
    3: 2008,
    4: 2011,
    5: 2013,
    6: 2015,
    7: 2017,
    8: 2019
}

cmap = cm.Reds
r_cmap = cm.Reds.reversed()
min_rate, max_rate = 2, 12
norm = mcolors.Normalize(vmin=min_rate, vmax=max_rate)
col = '#F7F2EF'

#@st.cache_data(show_spinner=False)
def open_dataset(disease, wave):
    df = pd.read_csv(f'data/{disease}_rates_wave{wave}.csv')
    return df

#@st.cache_data(show_spinner=False)
def get_rates(wave, variable, code_to_name=code_to_name, wave_to_year=wave_to_year):
    
    # open datasets
    path_ph = f'../SHARE/data/sharew{wave}_rel8-0-0_ALL_datasets_stata/sharew{wave}_rel8-0-0_ph.dta'
    path_dn = f'../SHARE/data/sharew{wave}_rel8-0-0_ALL_datasets_stata/sharew{wave}_rel8-0-0_dn.dta'
    ph = pd.read_stata(path_ph)
    dn = pd.read_stata(path_dn)
    dn.drop(['country'], axis=1, inplace=True)
    df = pd.merge(ph, dn, on='mergeid')
    columns = [variable, 'country', 'dn003_']
    df = df[columns]
    variable_name = code_to_name[variable]
    df.rename(columns={variable: variable_name,
                    'dn003_': 'YearOfBirth',
                    'country': 'Country'},
                    inplace=True)

    # deal with NaN
    values_to_replace = ["Don't know", "Refusal",
                     "Implausible value/suspected wrong", 
                     "Not codable", "Not answered",
                     "Not yet coded", "Not applicable"]
    df.replace(values_to_replace, float('NaN'), inplace=True)

    # create age variable and filter
    df['YearOfBirth'] = df['YearOfBirth'].astype(float)
    year = wave_to_year[wave]
    df["Age"] = year - df["YearOfBirth"]
    df = df.loc[df.Age >= 50,]

    # change cancer variable to binary
    df.dropna(subset=[variable_name], inplace=True)
    df[variable_name] = df[variable_name].replace({'Selected': 1, 'Not selected': 0})
    df[variable_name] = df[variable_name].astype(int)
    
    # compute cancer rates
    rates = df.groupby('Country', observed=True)[variable_name].mean()
    return rates

#@st.cache_data(show_spinner=False)
def convert_to_geojson(_world, rates, variable_name):
    europe = _world[_world['CONTINENT'] == 'Europe']
    europe = europe.merge(rates, how='left', left_on='NAME', right_on='Country')
    europe.dropna(subset=[variable_name], inplace=True)
    europe[variable_name] = round(europe[variable_name]*100,1)
    return europe

#@st.cache_data(show_spinner=False)
def plot_map(_data, wave, variable_name, countries_from_user, col=col, cmap=cmap, norm=norm):
    
    # axis properties
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    ax.set_xlim(-15, 35)
    ax.set_ylim(32, 72)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)

    # annotations
    year = wave_to_year[wave]
    fig.text(0.2, 0.8, f'{variable_name} Rates in Europe', fontsize=22, fontweight='bold', fontfamily='serif')
    fig.text(0.2, 0.71, f'Proportion of people over 50 with \n{variable_name.lower()} in Europe, according to the \nSHARE Survey data in {year}',
             fontsize=16, fontweight='light', fontfamily='serif')
    fig.text(0.26, 0.13, 'Data Source:', fontsize=10, fontweight='bold', fontfamily='serif')
    fig.text(0.33, 0.13, f'SHARE Survey, {wave}{get_suffix(wave)} wave', fontsize=10, fontweight='light', fontfamily='serif')
    fig.text(0.26, 0.11, 'Design:', fontsize=10, fontweight='bold', fontfamily='serif')
    fig.text(0.303, 0.11, 'Joseph Barbier', fontsize=10, fontweight='light', fontfamily='serif')
    
    # background
    ax.set_facecolor(col)
    fig.set_facecolor(col)
    
    # compute centroids for annotations
    data_projected = _data.to_crs(epsg=3035)
    data_projected['centroid'] = data_projected.geometry.centroid
    _data['centroid'] = data_projected['centroid'].to_crs(_data.crs)
    
    # get top countries
    n = 2
    sorted_rates = _data.sort_values(variable_name, ascending=False)
    top_countries = sorted_rates.head(n)['NAME'].values
    last_countries = sorted_rates.tail(n)['NAME'].values
    middle_countries = sorted_rates.iloc[5:-5]['NAME'].values
    countries_to_annotate = list(top_countries) + list(last_countries) + list(middle_countries)
    countries_to_annotate = countries_from_user
    adjustments = {
        'France': (9, 3),  
        'Italy': (-1, 0),
        'Lithuania': (0, -1),
        'Finland': (0, -2.5),
        'Romania': (0, -0.5),
        'Bulgaria': (0, -1),
        'Greece': (-1.2, -0.8),
        'Croatia': (0, -1),
        'Cyprus': (0, -1),
        'Ireland': (0, -1),
        'Malta': (0, -1),
        'Slovenia': (0, -1),
        'Slovakia': (-0.7, -0.8),
        'Estonia': (0, -1),
        'Latvia': (0, -1),
        'Belgium': (0, -0.7),
        'Austria': (0, -1),
        'Spain': (0, -1),
        'Portugal': (-0.5, -1),
        'Luxembourg': (0, -1),
        'Germany': (0, -1),
        'Hungary': (-0.3, -1),
        'Czechia': (0, -1),
        'Poland': (0, -1),
        'Sweden': (-1, -1),
        'Denmark': (0, -1),
        'Netherlands': (0, -1),
        'United Kingdom': (0, -1),
        'Switzerland': (0, -1),
    }

    # plot map
    _data.plot(column=variable_name, ax=ax, cmap=cmap)#, norm=norm)
    
    # annotate countries
    for country in countries_to_annotate:
        centroid = _data.loc[_data['NAME'] == country, 'centroid']
        try:
            centroid = centroid.values[0]
        except:
            continue
        x, y = centroid.coords[0]
        x += adjustments[country][0]
        y += adjustments[country][1]
        rate = _data.loc[_data['NAME'] == country, variable_name].values[0]
        ax.annotate(f'{country}\n{rate}%', (x, y), textcoords="offset points", xytext=(5,5),
                    ha='center', fontsize=8, fontfamily='DejaVu Sans', fontweight='bold', color='black')

    st.pyplot(fig)

#@st.cache_data(show_spinner=False)
def space(n):
    for _ in range(n):
        st.write('')

#@st.cache_data(show_spinner=False)
def get_suffix(n):
    if n == 1:
        return 'st'
    elif n == 2:
        return 'nd'
    elif n == 3:
        return 'rd'
    else:
        return 'th'
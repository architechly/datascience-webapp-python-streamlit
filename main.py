import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")
st.title("Motor Vehicle Collisions in NYC")
st.markdown("This application is using streamlit and python to create a dashboard")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase=lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    cols = data.columns
    cols = cols.map(lambda x: x.replace(' ', '_'))
    data.columns = cols
    data.rename(columns={'crash_data_crash_time': 'data/time'}, inplace=True)
    return data

def load_data1(nrows):
    data1=pd.read_csv(DATA_URL, nrows=nrows)
    return data1

data=load_data(100000)


st.subheader('Raw Data')

st.header("Where in NYC most people are injured?")
injured_people = st.slider("Number of persons injured", 0 ,19) ## add the number, you can just hard code the number like injured_people=10
st.map(data.query("number_of_persons_injured >= @injured_people")[['latitude','longitude']].dropna(how="any")) # plot the data on the map. use the query function to filter the data.


st.header("How many collisions occur during a given time of day?")
hour=st.selectbox("Hour to look at:",range(0,24),1)
data = data[data["crash_date_crash_time"].dt.hour ==hour]

st.markdown("Vehicle collisions between %i:00 and %i:00"% (hour, (hour+1)))

##coordinate for initial memoryview
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer", ## it can be any type, circularlayer, squarelayer or hexagonlayer
            data=data[['crash_date_crash_time','latitude','longitude']], ## the query as per you needs. Since visualizing the data in a region and in a specific time.
            get_position=['longitude','latitude'], ## As we move the graph, lat long get changeds, hence we need to get the corresponding data
            radius=100,  ## please refer the below parameters in the documentation.
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        )
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1)%24))
filtered = data[
    (data['crash_date_crash_time'].dt.hour >= hour) & (data['crash_date_crash_time'].dt.hour < (hour+1))
]
hist= np.histogram(filtered['crash_date_crash_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data=pd.DataFrame({'minute':range(60), 'crashes':hist})
fig=px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people",['Pedestrians','Cyclists','Motorists'])

if select =="Pedestrians":
    st.write(data.query("number_of_pedestrians_injured  >=1")[["on_street_name","number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any')[:5])
elif select =="Cyclists":
    st.write(data.query("number_of_cyclist_injured  >=1")[["on_street_name","number_of_cyclist_injured"]].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how='any')[:5])
else:
    st.write(data.query("number_of_motorist_injured  >=1")[["on_street_name","number_of_motorist_injured"]].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)



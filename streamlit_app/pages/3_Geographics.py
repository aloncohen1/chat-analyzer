import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_folium import st_folium
import folium
import numpy as np

from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, \
    get_locations_markers, local_css
from utils.graphs_utils import generate_piechart, generate_geo_chart

import json
import requests



def map_query(longitude: float, latitude: float) -> dict:
    '''Query OpenStreetMap for a long/lat coordinate and return relevant metadata.'''
    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1&namedetails=1'

    data = json.loads(requests.get(url).text)
    return data


def get_locations_details(locations_df):

    progress_text = "Resolving lat lng to address. Please wait."
    location_resolver_bar = st.progress(0, text=progress_text)

    address_list = []

    for index, item in enumerate(locations_df[['lat', 'lon']].values):
        lat, lng = item
        locations_details_df = map_query(longitude=lng, latitude=lat)
        address_list.append(locations_details_df.get('address') if locations_details_df else {})
        location_resolver_bar.progress(((index + 1) / len(locations_df)), text=progress_text)

    location_resolver_bar.empty()
    return locations_df.drop(["popup", 'geohash'], axis=1).join(pd.DataFrame(address_list))



def main():
    st.set_page_config(layout="wide")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date = add_filters()

        locations_df = get_locations_markers(filtered_df)

        # locations_details_df = get_locations_details(filtered_df)

        if not locations_df.empty:
            st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)

            top_freq_geohash = locations_df['geohash'].value_counts().index[0]

            m = folium.Map(location=locations_df[locations_df['geohash'] == top_freq_geohash][['lat', 'lon']].mean().values.tolist(),
                           zoom_start=15, tiles='cartodbpositron')

            sw = locations_df[locations_df['geohash'] == top_freq_geohash][['lat', 'lon']].min().values.tolist()
            ne = locations_df[locations_df['geohash'] == top_freq_geohash][['lat', 'lon']].max().values.tolist()

            m.fit_bounds([sw, ne])

            for i in locations_df.to_dict('records'):
                folium.Marker(location=[i['lat'], i['lon']], popup=i['popup'],
                              tooltip=i['username']+'<br>'+i['timestamp'].date().isoformat()).add_to(m)

            col1, col2 = st.columns((10, 6))
            col1.metric("Overall Locations", locations_df.shape[0])
            col2.metric("Overall Users", locations_df['username'].nunique())
            col2, col3 = st.columns((10, 6))
            with col2:
                st_folium(m, width=2000, height=500, returned_objects=[], use_container_width=True)
            with col3:

                if 'geo_data' not in st.session_state:
                    st.session_state['geo_data'] = get_locations_details(locations_df)
                elif len(locations_df) > len(st.session_state['geo_data']):
                    st.session_state['geo_data'] = get_locations_details(locations_df)

                st.plotly_chart(generate_geo_chart(st.session_state['geo_data'], "city"), use_container_width=True)

            st.write(st.session_state['geo_data'])
                # st.metric("Overall Locations", locations_df.shape[0])
        else:
            st.header('No Locations to show')
            # You can create a similar template for each section as the main app


# Run the app
if __name__ == "__main__":
    main()

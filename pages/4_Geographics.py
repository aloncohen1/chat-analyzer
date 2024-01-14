import pandas as pd
import streamlit as st
import json
import requests
import streamlit_analytics

from streamlit_folium import st_folium
import folium

from app_utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, \
    get_locations_markers, local_css, linkedin_link, form_link, buy_me_a_coffee_link
from app_utils.graphs_utils import generate_geo_barchart, generate_geo_piehart
from streamlit_extras.buy_me_a_coffee import button


def filter_locations_df(df, locations_df, min_date, max_date):

    filtered_locations_df = df[(df['timestamp'].dt.date.between(min_date, max_date)) &
                               df['username'].isin(locations_df['username'].unique())]

    return filtered_locations_df



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
        if locations_details_df.get('address'):
            address_list.append(locations_details_df.get('address'))
        location_resolver_bar.progress(((index + 1) / len(locations_df)), text=progress_text)

    location_resolver_bar.empty()

    return locations_df.drop(["popup", 'geohash'], axis=1).join(pd.DataFrame(address_list))



def main():
    st.set_page_config(layout="wide", page_title="Geographics", page_icon="🌎")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date, language = add_filters()

        locations_df = get_locations_markers(filtered_df)

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))

        header_text = {'en': 'Geographics', 'he': 'ניתוח גיאוגרפי'}
        st.subheader(header_text[language])

        if not locations_df.empty:
            st.markdown(local_css("add_ons/styles/metrics.css"), unsafe_allow_html=True)

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
            loc_lang_dict = {'en': "Overall Locations", "he": 'סה"כ מיקומים'}
            users_lang_dict = {'en': "Overall Users with Locations", "he": 'סה"כ משתמשים ששלחו מיקום'}
            col1.metric(loc_lang_dict[language], locations_df.shape[0])
            col2.metric(users_lang_dict[language], locations_df['username'].nunique())
            col2, col3 = st.columns((10, 6))

            with col2:
                st_folium(m, width=2000, height=500, returned_objects=[], use_container_width=True)

            with col3:
                if ('geo_data' not in st.session_state) or (len(locations_df) > len(st.session_state['geo_data'])):
                    st.session_state['geo_data'] = get_locations_details(locations_df)

                filtered_locations_df = filter_locations_df(st.session_state['geo_data'], locations_df, min_date, max_date)
                st.plotly_chart(generate_geo_piehart(filtered_locations_df, language), use_container_width=True)

            filtered_locations_df = filter_locations_df(st.session_state['geo_data'], locations_df, min_date, max_date)
            general_col, _ = st.columns((1000, 1))
            with general_col:
                road_city_lang_dict = {'en': 'Top Cities & Roads', 'he': 'התפלגות מיקומים על פני ערים ורחובות'}
                st.subheader(road_city_lang_dict[language])
                col4, col5 = st.columns((6, 8))
                col4.plotly_chart(generate_geo_barchart(filtered_locations_df, language, "city"), use_container_width=True)
                col5.plotly_chart(generate_geo_barchart(filtered_locations_df, language, "road"), use_container_width=True)

        else:
            no_loc_lang_dict = {"en": 'No Locations to show', "he": "הדאטא אינו מכיל מיקומים לניתוח"}
            st.header(no_loc_lang_dict[language])


if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    # button(username="bigalon1991", width=221)
    linkedin_link()
    form_link()
    buy_me_a_coffee_link()
    streamlit_analytics.stop_tracking(unsafe_password=st.secrets["tracking_pass"])

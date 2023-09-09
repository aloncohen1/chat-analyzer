import pandas as pd
import streamlit as st
import json
import requests
import streamlit_analytics


from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, \
    get_locations_markers, local_css
from utils.graphs_utils import generate_message_responses_flow, user_message_responses_heatmap
from utils.text_utils import get_lang_stop_words


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
    st.set_page_config(layout="wide", page_title="Users Interaction", page_icon="🔀")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date = add_filters()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))
        st.subheader('Users Interaction')


        st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)

        # col1, col2 = st.columns((6, 8))

        st.plotly_chart(generate_message_responses_flow(filtered_df,5), use_container_width=True)
        st.plotly_chart(user_message_responses_heatmap(filtered_df,10), use_container_width=True)

        st.write(get_lang_stop_words(filtered_df))





if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    streamlit_analytics.stop_tracking()

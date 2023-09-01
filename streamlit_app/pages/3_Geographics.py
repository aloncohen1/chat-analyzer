import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_folium import st_folium
import folium

from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, \
    get_locations_markers, local_css
from utils.graphs_utils import generate_piechart


def main():
    st.set_page_config(layout="wide")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date = add_filters()

        locations_df = get_locations_markers(filtered_df)

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
                st.plotly_chart(generate_piechart(locations_df, metric='Locations'), use_container_width=True)
                st.write('geohash', top_freq_geohash)
                # st.metric("Overall Locations", locations_df.shape[0])
        else:
            st.header('No Locations to show')
            # You can create a similar template for each section as the main app


# Run the app
if __name__ == "__main__":
    main()

import streamlit as st

from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters
from utils.graphs_utils import generate_message_responses_flow


def main():

    st.set_page_config(layout="wide")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:

        filtered_df = add_filters()
        col0, col1 = st.columns((6, 10))
        with col0:
            st.plotly_chart(generate_message_responses_flow(filtered_df),use_container_width=True)
            # You can create a similar template for each section as the main app


# Run the app
if __name__ == "__main__":
    main()

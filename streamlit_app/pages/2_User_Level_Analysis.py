import streamlit as st
from utils.general_utils import refer_to_load_data_section, set_background


def generate_graphs(df):
    return st.line_chart(df.groupby('month', as_index=False).agg(n_message=('username', 'count')),
                         x='month', y='n_message', color="#24d366")


def main():

    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        st.title("WhatsApp Group Chat Analyzer")

        st.header("Data Visualization")

        generate_graphs(st.session_state['data'])


# Run the app
if __name__ == "__main__":
    main()

import pandas as pd
import streamlit as st
from supabase import create_client


# ##### Supabase Connection
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


# ##### Main Application
def main():
    @st.experimental_memo
    def run_query():
        return supabase.table("game_events_stats").select("*").eq('Team', 'Borussia Dortmund').execute().data

    event_df = pd.DataFrame(run_query())
    st.dataframe(event_df)


if __name__ == '__main__':
    main()

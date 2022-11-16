import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from supabase import create_client
from PIL import Image
from page_scripts.game_page import game_events
from page_scripts.team_page import team_events
from page_scripts.player_page import player_events


# ##### Logo and App Info
buli_logo = Image.open('images/Bundesliga.png')

st.set_page_config(layout="wide",
                   page_title="Bundesliga Events App",
                   page_icon=buli_logo,
                   initial_sidebar_state="expanded")

season = "2022-2023"
buli_logo_col, text_col = st.columns([1, 10])
buli_container = st.container()
with buli_container:
    with buli_logo_col:
        st.image(buli_logo, use_column_width=True)
    with text_col:
        st.header("")
        st.markdown(f"<h1>Bundesliga Game Events <font color = #d20614>{season}</font></h1>", unsafe_allow_html=True)


# ##### Supabase Connection #####
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


# ##### Supabase Table Queries
@st.experimental_memo(ttl=600)
def info_query():
    """ Return Game Info """
    game_info_query = supabase.table('game_info_stats').select('*').execute().data
    game_info = pd.DataFrame(game_info_query)

    return game_info


@st.experimental_memo(ttl=600)
def event_query(team, match_day):
    """ Return Game Events """
    game_team_query = supabase.table('game_events_stats').select('*').\
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_team_df = pd.DataFrame(game_team_query)
    game_opp_query = supabase.table('game_events_stats').select('*').\
        eq('Opponent', team).eq('Match Day', match_day).execute().data
    game_opp_df = pd.DataFrame(game_opp_query)

    if game_team_df['Venue'].unique()[0] == 'Away':
        game_team_df['Start X'] = np.abs(game_team_df['Start X'] - 100)
        game_team_df['End X'] = np.abs(game_team_df['End X'] - 100)
        game_team_df['Start Y'] = np.abs(game_team_df['Start Y'] - 100)
        game_team_df['End Y'] = np.abs(game_team_df['End Y'] - 100)

    if game_opp_df['Venue'].unique()[0] == 'Away':
        game_opp_df['Start X'] = np.abs(game_opp_df['Start X'] - 100)
        game_opp_df['End X'] = np.abs(game_opp_df['End X'] - 100)
        game_opp_df['Start Y'] = np.abs(game_opp_df['Start Y'] - 100)
        game_opp_df['End Y'] = np.abs(game_opp_df['End Y'] - 100)

    game_event_df = pd.concat([game_team_df, game_opp_df], axis=0)

    return game_event_df


@st.experimental_memo(ttl=600)
def players_info_query(team, match_day):
    """ Return Player Game Info """
    game_player_query_team = supabase.table('game_player_info').select('*').\
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_player_team_df = pd.DataFrame(game_player_query_team)
    game_player_query_opp = supabase.table('game_player_info').select('*').\
        eq('Opponent', team).eq('Match Day', match_day).execute().data
    game_player_opp_df = pd.DataFrame(game_player_query_opp)

    game_players_df = pd.concat([game_player_team_df, game_player_opp_df], axis=0)
    # game_players_df.dropna(inplace=True)

    return game_players_df


# ##### Main App #####
def main():
    # Option Menu Bar
    statistics_type = ["Home", "Game", "Team", "Player"]
    with st.sidebar:
        st.subheader("Select Page")
        event_analysis = option_menu(menu_title=None,
                                     options=statistics_type,
                                     icons=["house-fill", "calendar2-event", "diagram-3-fill",
                                            "person-lines-fill"],
                                     styles={"nav-link": {"--hover-color": "#e5e5e6"}})

        # ##### Select Favourite Team
        buli_teams = ['1. FC Köln', '1. FC Union Berlin', '1. FSV Mainz 05', 'Bayer 04 Leverkusen', 'Borussia Dortmund',
                      'Borussia Mönchengladbach', 'Eintracht Frankfurt', 'FC Augsburg', 'FC Bayern München',
                      'FC Schalke 04', 'Hertha Berlin', 'RasenBallsport Leipzig', 'SV Werder Bremen',
                      'Sport-Club Freiburg', 'TSG 1899 Hoffenheim', 'VfB Stuttgart', 'VfL Bochum 1848', 'VfL Wolfsburg']

        favourite_team = st.sidebar.selectbox(label="Select Favourite Team",
                                              options=buli_teams,
                                              index=buli_teams.index("Borussia Dortmund"))

    if event_analysis == 'Home':
        st.subheader("")
        st.markdown(
            'A statistical application that allows the user to analyse Bundesliga Game Events on Team and Player '
            'level.<br> <br> <b>App Features</b>', unsafe_allow_html=True)

        """ 
        * Select your favourite team
        * Select your favourite Player
        * Types of Statistics:
            * Event Level Data per Match Day
            * Event Level Data per Team
            * Event Level Data per Player
    """
    elif event_analysis == 'Game':
        # ##### Filter by Team and Match Day
        info_df = info_query()
        max_match_day = info_df[info_df['Team'] == favourite_team]['Match Day'].max()
        match_day = st.sidebar.selectbox(label="Match Day",
                                         options=[i for i in range(1, max_match_day + 1)],
                                         index=int(max_match_day) - 1)

        # ##### Game Events Page
        game_event_df = event_query(team=favourite_team, match_day=match_day)
        info_players_df = players_info_query(team=favourite_team, match_day=match_day)
        game_events(data=game_event_df,
                    data_info=info_df,
                    data_players=info_players_df,
                    match_day=match_day)

    elif event_analysis == 'Team':
        team_events(team=favourite_team)

    elif event_analysis == 'Player':
        team_player = st.sidebar.selectbox("Select Player", buli_teams)
        player_events(player=team_player)
        st.sidebar.markdown("<b>Note</b>: Only players with at least <b><font color=#d20614>10%</font></b> of minutes "
                            "played", unsafe_allow_html=True)

    # ##### Footer Page
    ref_col, fan_club_name, fan_club_logo = st.columns([10, 1, 1])
    with fan_club_name:
        st.markdown(f"<p style='text-align: left;'p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: right;'p>Created By: ", unsafe_allow_html=True)
    with fan_club_logo:
        bvb_ro_logo = Image.open('images/BVB_Romania.png')
        st.image(bvb_ro_logo, width=50)
        st.markdown("@ <b><font color = #d20614 style='text-align: center;'>"
                    "<a href='mailto:omescu.mario.lucian@gmail.com' style='text-decoration: none; '>"
                    "Mario Omescu</a></font></b>", unsafe_allow_html=True)
    with ref_col:
        st.markdown(
            f"<b><font color=#d20614>Data Reference:</font></b><ul><li><a href='https://www.whoscored.com' "
            "style='text-decoration: none; '>Game Event Stats</a></li></ul>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()

import streamlit as st
from streamlit_option_menu import option_menu
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
        st.markdown(f"<h1>Bundesliga Game Events <font color = #d20614>{season}</font></h1>", unsafe_allow_html=True)


# ##### Supabase Connection
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


# ##### Main Application
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

        favourite_team = st.sidebar.selectbox("Select Favourite Team", buli_teams)

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
        game_events(team=favourite_team)

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



    # @st.experimental_memo
    # def run_query():
    #     return supabase.table("game_events_stats").select("*").eq('Team', 'Borussia Dortmund').execute().data
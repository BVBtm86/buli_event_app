import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from page_scripts.game_page import game_events
from page_scripts.team_page import team_events
from page_scripts.player_page import player_events

# ##### Logo and App Info
buli_logo = Image.open('images/Bundesliga.png')

st.set_page_config(layout="wide",
                   page_title="Bundesliga Events App",
                   page_icon=buli_logo,
                   initial_sidebar_state="expanded")

from page_scripts.stats_scripts.utilities import info_query, players_info_query, event_query, team_query, \
    team_players_query

# ##### Button Color
button_color = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #ffffff;
    color:#d20614;
    width: 100%;
    border-color: #ffffff;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #d20614;
    color:#ffffff;
    border-color: #ffffff;
    font-weight: bold;
    width: 100%;
    }
</style>""", unsafe_allow_html=True)

# ##### Main Page
season = "2022-2023"
buli_logo_col, text_col = st.columns([1, 10])
buli_container = st.container()
with buli_container:
    with buli_logo_col:
        st.image(buli_logo, use_column_width=True)
    with text_col:
        st.markdown("")
        st.markdown(f"<h1><font color = #d20614>Bundesliga</font> Game Events <font color = #d20614>{season}</font>"
                    f"</h1>", unsafe_allow_html=True)


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
        team_logo = Image.open(f'images/{favourite_team}.png')
        _, img_col, _ = st.sidebar.columns([1, 1, 1])
        with img_col:
            st.image(team_logo, width=100, use_column_width=True)

    # ##### Info Data
    info_df = info_query()

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
                * Starting 11
                * Game Events
                * Passing Network
                * Passing Direction
                * Passing Sequence
            * Event Level Data per Team
                * Game Events
                * Passing Network
                * Passing Direction
            * Event Level Data per Player
    """
    elif event_analysis == 'Game':
        # ##### Filter by Team and Match Day
        max_match_day = info_df[info_df['Team'] == favourite_team]['Match Day'].max()
        match_day = st.sidebar.selectbox(label="Match Day",
                                         options=[i for i in range(1, max_match_day + 1)],
                                         index=int(max_match_day) - 1)

        # ##### Game Events Page
        game_event_df = event_query(team=favourite_team, match_day=match_day)
        info_players_df = players_info_query(team=favourite_team, match_day=match_day)
        game_events(data=game_event_df,
                    data_players=info_players_df,
                    match_day=match_day)

    elif event_analysis == 'Team':

        # ##### Team Analysis Options
        st.sidebar.header("Analysis Options")
        team_event_menu = ["Game Events", "Passing Network", "Passing Direction"]
        analysis_option = st.sidebar.selectbox("Select Analysis", team_event_menu)

        # ##### Opponents vs Other Team Options
        if analysis_option != "Passing Network":
            team_event_menu = ["vs Opponents", "vs Team"]
            team_analysis = st.sidebar.selectbox(label="Select Analysis",
                                                 options=team_event_menu)
        else:
            team_analysis = "vs Opponents"

        if team_analysis == "vs Opponents":
            opponent_sql = favourite_team
        else:
            opponent_selection = [team for team in buli_teams if team != favourite_team]
            team_opponent = st.sidebar.selectbox(label="Select Team",
                                                 options=opponent_selection)
            opponent_sql = team_opponent

        # ##### Season Filter
        season_options = ["Entire Season", "1st Half of The Season", "2nd Half of The Season"]
        if info_df[info_df['Team'] == "Borussia Dortmund"]['Match Day'].max() < 18:
            season_options.remove("2nd Half of The Season")

        st.sidebar.header("Game Filter")
        season_filter = st.sidebar.selectbox(label="Season Filter",
                                             options=season_options)

        if season_filter == "1st Half of The Season":
            period_filter = [1, 17]
        elif season_filter == "2nd Half of The Season":
            period_filter = [18, 34]
        else:
            period_filter = [1, 34]

        # ##### Venue Filter
        all_venues = \
            info_df[(info_df['Team'] == favourite_team) &
                    (info_df['Match Day'] >= period_filter[0]) &
                    (info_df['Match Day'] <= period_filter[1])]['Venue'].unique()

        venue_options = ["All Games"]
        venue_options.extend([venue for venue in all_venues])
        venue_filter = st.sidebar.selectbox(label="Venue Filter",
                                            options=venue_options)

        # ##### Result Filter
        if venue_filter == "All Games":
            all_results = info_df[(info_df['Team'] == favourite_team) &
                                  (info_df['Match Day'] >= period_filter[0]) &
                                  (info_df['Match Day'] <= period_filter[1])]['Result'].unique()
        else:
            all_results = info_df[(info_df['Team'] == favourite_team) &
                                  (info_df['Match Day'] >= period_filter[0]) &
                                  (info_df['Match Day'] <= period_filter[1]) &
                                  (info_df['Venue'] == venue_filter)]['Result'].unique()

        result_options = ["All Results"]
        result_options.extend([result for result in all_results])
        result_filter = st.sidebar.selectbox(label="Result Filter",
                                             options=result_options)

        # ##### Final Event Data
        team_event_df = team_query(team_sql=favourite_team,
                                   opponent_sql=opponent_sql,
                                   period_sql=period_filter,
                                   venue_sql=venue_filter,
                                   result_sql=result_filter)

        # ##### Team Event Page
        event_match_days = team_event_df[team_event_df['Team'] == favourite_team]['Match Day'].unique()
        team_players_df = team_players_query(team=favourite_team,
                                             match_days=event_match_days)

        team_events(data=team_event_df,
                    players_data=team_players_df,
                    analysis_option=analysis_option,
                    analysis_team=team_analysis,
                    team_name=favourite_team,
                    opp_name=opponent_sql)

    elif event_analysis == 'Player':
        team_player = st.sidebar.selectbox("Select Player", buli_teams)
        player_events(player=team_player)
        st.sidebar.markdown("<b>Note</b>: Only players with at least <b><font color=#d20614>10%</font></b> of minutes "
                            "played", unsafe_allow_html=True)

    if event_analysis == 'Home':
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

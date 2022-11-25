import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from page_scripts.game_page import game_events
from page_scripts.team_page import team_events
from page_scripts.player_page import player_events
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ##### Logo and App Info
buli_logo = Image.open('images/Bundesliga.png')

st.set_page_config(layout="wide",
                   page_title="Bundesliga Events App",
                   page_icon=buli_logo,
                   initial_sidebar_state="expanded")

from page_scripts.stats_scripts.utilities import info_query, players_info_query, event_query, team_query, \
    team_players_query, avg_keep_players, games_player_played, players_query

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

# ##### Hide Streamlit info
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        st.markdown("")
        st.markdown(
            '<h5>A Statistical application that allows the user to analyse Bundesliga Game Events Data for '
            'Team and Players</h5>', unsafe_allow_html=True)

        st.header("")
        st.markdown("<b>App Features</b>", unsafe_allow_html=True)
        """ 
        * Select your favourite team
        * Select your favourite Player
        * Types of Analysis:
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
                * Game Events
                * Passing Network
                * Passing Direction
        """
        st.header("")

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
        team_event_menu = ["Game Events", "Passing Network", "Passing Distance"]
        team_analysis_option = st.sidebar.selectbox("Select Analysis", team_event_menu)

        # ##### Opponents vs Other Team Options
        if team_analysis_option != "Passing Network":
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
                    analysis_option=team_analysis_option,
                    analysis_team=team_analysis,
                    team_name=favourite_team,
                    opp_name=opponent_sql,
                    page_filter=[season_filter, venue_filter, result_filter])

    elif event_analysis == 'Player':
        max_match_day = info_df[info_df['Team'] == favourite_team]['Match Day'].max()
        team_players = avg_keep_players(team=favourite_team,
                                        current_match_day=max_match_day)

        final_player = st.sidebar.selectbox(label="Select Player",
                                            options=team_players)
        st.sidebar.markdown("<b>Note</b>: Only players with at least <b><font color=#d20614>10%</font></b> of minutes "
                            "played", unsafe_allow_html=True)

        # ##### Player Analysis Options
        st.sidebar.header("Analysis Options")
        player_analysis_option = st.sidebar.selectbox(label="Main Analysis",
                                                      options=["Individual", "vs Player"])

        player_event_menu = ["Game Events", "Passing Network", "Passing Distance"]
        player_analysis_type = st.sidebar.selectbox(label="Analysis Type",
                                                    options=player_event_menu)

        # ##### Season Filter
        st.sidebar.header("Game Filter")
        player_game_filter = st.sidebar.selectbox(label="Game Type Filter",
                                                  options=["By Game", "By Season"])

        player_games_df, player_days_options = \
            games_player_played(team=favourite_team,
                                player_name=final_player)

        if player_game_filter == "By Game":
            player_match_day = st.sidebar.selectbox(label="Select Match Day",
                                                    options=player_days_options,
                                                    index=list(player_days_options).index(player_days_options[-1]))
            player_period_filter = None
            player_venue_filter = None
            player_result_filter = None
        else:
            player_match_day = None
            if player_games_df['Match Day'].max() > 17:
                player_season_options = ["Entire Season", "1st Half of The Season", "2nd Half of The Season"]
            else:
                player_season_options = ["Entire Season", "1st Half of The Season"]
            player_season_filter = st.sidebar.selectbox(label="Season Filter",
                                                        options=player_season_options)

            if player_season_filter == "1st Half of The Season":
                player_period_filter = [1, 17]
            elif player_season_filter == "2nd Half of The Season":
                player_period_filter = [18, 34]
            else:
                player_period_filter = [1, 34]

            # ##### Venue Filter
            player_venue_options = \
                player_games_df[player_games_df['Match Day'].isin(player_days_options)]['Venue'].unique()

            venue_options = ["All Games"]
            if "Home" in player_venue_options:
                venue_options.append("Home")
            if "Away" in player_venue_options:
                venue_options.append("Away")
            player_venue_filter = st.sidebar.selectbox(label="Venue Filter",
                                                       options=venue_options)
            # ##### Result Filter
            if player_venue_filter == "All Games":
                player_result_options = \
                    player_games_df[player_games_df['Match Day'].isin(player_days_options)]['Result'].unique()
            else:
                player_result_options = \
                    player_games_df[player_games_df['Match Day'].isin(player_days_options) &
                                    (player_games_df['Venue'] == player_venue_filter)]['Result'].unique()

            result_options = ["All Results"]
            result_options.extend([result for result in player_result_options])
            player_result_filter = st.sidebar.selectbox(label="Result Filter",
                                                        options=result_options)

        # ##### Team Event Page
        main_player_event_df = players_query(team_sql=favourite_team,
                                             player_name_sql=final_player,
                                             player_option=player_game_filter,
                                             match_day_sql=player_match_day,
                                             period_sql=player_period_filter,
                                             venue_sql=player_venue_filter,
                                             result_sql=player_result_filter)

        if player_match_day is not None:
            player_teams_opponent = list(info_df[(info_df['Match Day'] == player_match_day) &
                                                 ((info_df['Team'] == favourite_team) |
                                                  (info_df['Opponent'] == favourite_team))]['Team'].unique())
        else:
            player_teams_opponent = buli_teams

        player_events(data=main_player_event_df,
                      analysis_option=player_analysis_option,
                      analysis_type=player_analysis_type,
                      team_player=favourite_team,
                      opponent_teams=player_teams_opponent,
                      player_name=final_player,
                      player_option_filter=player_game_filter,
                      match_day_filter=player_match_day,
                      period_filter=player_period_filter,
                      venue_filter=player_venue_filter,
                      result_filter=player_result_filter,
                      current_match_day=max_match_day)

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

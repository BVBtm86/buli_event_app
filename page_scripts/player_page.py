import streamlit as st
from PIL import Image
from page_scripts.stats_scripts.utilities import avg_keep_players_opponent, players_query


# ##### Event Options
event_options = ['Passes', 'Goals', 'Shots Saved', 'Shots Missed', 'Shots On Post', 'Penalties', 'Ball Touches',
                 'Dribbles', 'Corner Awarded', 'Ball Recoveries', 'Interceptions', 'Aerial Duels', 'Tackles',
                 'Dispossessions', 'Clearances', 'Challenges', 'Blocked Passes', 'Fouls', 'Offsides', 'Errors',
                 'Keeper Saves', 'Keeper Claims', 'Keeper Punches', 'Keeper Pickups', 'Keeper Sweeper']

event_options_sequence = ['Goal', 'Unsuccessful Pass', 'Shot Saved', 'Shot Missed', 'Shot On Post', 'Penalty',
                          'Unsuccessful Ball Touch', 'Unsuccessful Dribble', 'Corner Awarded', 'Ball Recovery',
                          'Interception', 'Unsuccessful Aerial Duel', 'Tackled', 'Dispossessed', 'Clearance',
                          'Challenged', 'Blocked Pass', 'Fouled', 'Offside', 'Error', 'Keeper Save',
                          'Keeper Claim', 'Keeper Punch', 'Keeper Pickup', 'Keeper Sweep']


def player_events(data, analysis_type, analysis_option, team_player, opponent_teams, player_name,
                  player_option_filter, match_day_filter, period_filter, venue_filter, result_filter,
                  current_match_day, game_day):
    """ Page Configuration """
    config = {'displayModeBar': False}

    player_data = data.copy()
    time_filter = [player_data['Minute'].min(),
                   player_data['Minute'].max()]

    ''' Add vs Player Data'''
    if game_day is None:
        page_season_type = f"Season"
        compare_player_filter = "By Season"
    else:
        page_season_type = f"Match Day {game_day}"
        compare_player_filter = "By Game"

    if analysis_type == "Individual":
        name_col, _ = st.columns([10, 2])
        with name_col:
            st.markdown(f"<h3><font color=#d20614>{player_name}</font> - "
                        f"{analysis_option} <font color=#d20614>{page_season_type}</font></h3>", unsafe_allow_html=True)
        menu_col, _, plot_col, legend_col = st.columns([2, 0.1, 8, 2])
        compare_player = None
    else:
        name_col, _ = st.columns([10, 2])
        menu_col, _, plot_col_1, plot_col_2, legend_col = st.columns([2, 0.1, 4, 4, 2])
        with legend_col:
            team_player_opponent = st.selectbox(label="Select Team",
                                                options=opponent_teams,
                                                index=opponent_teams.index(team_player))

            opponent_players = avg_keep_players_opponent(team=team_player_opponent,
                                                         current_match_day=current_match_day,
                                                         match_day=game_day,
                                                         player_name=player_name)
            compare_player = st.selectbox(label="Select Player",
                                          options=opponent_players)
        with name_col:
            st.markdown(f"<h3><font color=#392864>{player_name}</font> vs <h3><font color=#d20614>{compare_player} - "
                        f"</font>{analysis_option} <font color=#d20614>{page_season_type}</font></h3>",
                        unsafe_allow_html=True)

    """ Minutes Filter """
    st.sidebar.header("Time Filter")
    game_time = st.sidebar.selectbox(label="Game Phase",
                                     options=["Entire Game", "1st Half", "2nd Half"])

    if game_time == "Entire Game":
        min_minute = player_data['Minute'].min()
        max_minute = player_data['Minute'].max()

        time_filter = st.sidebar.select_slider(label="Select Period",
                                               options=[i for i in range(min_minute, max_minute + 1)],
                                               value=(min_minute, max_minute))
    elif game_time == "1st Half":
        time_option = st.sidebar.selectbox(label="Select Period",
                                           options=["Entire Period", "1-15", '16-30', '31-45+'])
        max_minute = player_data[player_data['Period'] == '1st Half']['Minute'].max()
        if time_option == "Entire Period":
            time_filter = [0, max_minute]
        elif time_option == "1-15":
            time_filter = [0, 15]
        elif time_option == "16-30":
            time_filter = [16, 30]
        elif time_option == "31-45+":
            time_filter = [31, max_minute]
    else:
        time_option = st.sidebar.selectbox(label="Select Period",
                                           options=["Entire Period", "46-60", '61-75', '76-90+'])
        max_minute = player_data[player_data['Period'] == '2nd Half']['Minute'].max()
        if time_option == "Entire Period":
            time_filter = [45, max_minute]
        elif time_option == "46-60":
            time_filter = [45, 60]
        elif time_option == "61-75":
            time_filter = [61, 75]
        elif time_option == "76-90+":
            time_filter = [76, max_minute]

    # ##### Final Data
    if compare_player is not None:
        player_data_opponent = players_query(team_sql=team_player_opponent,
                                             player_name_sql=compare_player,
                                             player_option=compare_player_filter,
                                             match_day_sql=match_day_filter,
                                             period_sql=period_filter,
                                             venue_sql=venue_filter,
                                             result_sql=result_filter)
    else:
        player_data_opponent = None

    st.sidebar.header(" ")

    """ Game Events Page """
    if analysis_option == "Game Events":
        page_container = st.empty()
        with page_container.container():
            pass

            """ Final Data """
            if game_time == "Entire Game":
                event_types = player_data[(player_data['Minute'] >= time_filter[0]) &
                                          (player_data['Minute'] <= time_filter[1])]['Event'].unique()
            else:
                event_types = player_data[(player_data['Period'] == game_time) &
                                          (player_data['Minute'] >= time_filter[0]) &
                                          (player_data['Minute'] <= time_filter[1])]['Event'].unique()

            final_event_types = [event for event in event_options if event in event_types]
            with menu_col:
                event_analysis = st.selectbox(label="Event Type",
                                              options=final_event_types)

                event_outcome_type = player_data[(player_data['Minute'] >= time_filter[0]) &
                                                 (player_data['Minute'] <= time_filter[1]) &
                                                 (player_data['Event'] == event_analysis)]['Outcome'].unique()
                if len(event_outcome_type) == 2:
                    event_outcome = st.selectbox(label="Event Outcome",
                                                 options=["Successful", "Unsuccessful"])
                    event_outcome_label = event_outcome
                else:
                    event_outcome = event_outcome_type[0]
                    event_outcome_label = ""

            """ Game Event Analysis """
            if game_time == "Entire Game":
                final_player_df = player_data[(player_data['Outcome'] == event_outcome) &
                                          (player_data['Minute'] >= time_filter[0]) &
                                          (player_data['Minute'] <= time_filter[1]) &
                                          (player_data['Event'] == event_analysis)]
            else:
                final_player_df = player_data[(player_data['Period'] == game_time) &
                                          (player_data['Outcome'] == event_outcome) &
                                          (player_data['Minute'] >= time_filter[0]) &
                                          (player_data['Minute'] <= time_filter[1]) &
                                          (player_data['Event'] == event_analysis)]

            player_min_events = final_player_df.shape[0]
            if player_min_events < 6:
                plot_type = "Position"
            else:
                with menu_col:
                    plot_type = st.selectbox(label="Plot Type",
                                             options=['Heatmap', 'Position'])

        st.sidebar.header(" ")

    elif analysis_option == "Passing Network":
        page_container = st.empty()
        with page_container.container():
            pass

        st.sidebar.header(" ")

    elif analysis_option == "Passing Direction":
        page_container = st.empty()
        with page_container.container():
            pass

        st.sidebar.header(" ")

    elif analysis_option == "Passing Sequence":
        page_container = st.empty()
        with page_container.container():
            pass

        st.sidebar.header(" ")

    else:
        pass



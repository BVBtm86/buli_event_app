import pandas as pd
import streamlit as st
from page_scripts.stats_scripts.utilities import avg_keep_players_opponent, players_query, players_jersey_query
from page_scripts.stats_scripts.player_stats import player_analysis, player_passing_network, player_passing_direction

# ##### Event Options
event_options = ['Ball Possession', 'Passes', 'Shots', 'Dribbles', 'Corner Awarded', 'Ball Recoveries', 'Interceptions',
                 'Aerial Duels', 'Tackles', 'Loss of Possession', 'Clearances', 'Challenges', 'Blocked Passes',
                 'Fouls', 'Offsides', 'Errors', 'Keeper Saves', 'Keeper Claims', 'Keeper Punches', 'Keeper Pickups',
                 'Keeper Sweeper']

event_shots_type = ["Goal", "Shot on Target", "Shot off Target", "Shot on Post", "Own Goal"]


def player_events(data, analysis_option, analysis_type, team_player, opponent_teams, player_name,
                  player_option_filter, match_day_filter, period_filter, venue_filter, result_filter,
                  current_match_day):
    """ Page Configuration """
    season_year = "2022-2023"
    config = {'displayModeBar': False}

    player_data = data.copy()
    time_filter = [player_data['Minute'].min(),
                   player_data['Minute'].max()]

    ''' Add vs Player Data'''
    if match_day_filter is None:
        page_season_type = f"Season"
        compare_player_filter = "By Season"
    else:
        page_season_type = f"Match Day {match_day_filter}"
        compare_player_filter = "By Game"

    if analysis_option == "Individual":
        name_col, _ = st.columns([10, 2])
        with name_col:
            st.markdown(f"<h3><font color=#d20614>{player_name}</font> - {page_season_type} <font color=#d20614>"
                        f"{analysis_type}</font></h3>", unsafe_allow_html=True)
        menu_col, _, plot_col_1, legend_col = st.columns([2, 0.1, 8, 0.5])
        team_player_opponent = None
        compare_player = None
        plot_col_2 = None
    else:
        name_col, _ = st.columns([10, 0.5])
        menu_col, _, plot_col_1, plot_col_2, legend_col = st.columns([2, 0.1, 4, 4, 2])
        with legend_col:
            team_player_opponent = st.selectbox(label="Select Team",
                                                options=opponent_teams,
                                                index=opponent_teams.index(team_player))

            opponent_players = avg_keep_players_opponent(team=team_player_opponent,
                                                         current_match_day=current_match_day,
                                                         match_day=match_day_filter,
                                                         player_name=player_name)
            compare_player = st.selectbox(label="Select Player",
                                          options=opponent_players)
        with name_col:
            st.markdown(f"<h3><font color=#d20614>{player_name}</font> vs <font color=#392864>{compare_player}</font>"
                        f" - {page_season_type} <font color=#d20614>{analysis_type}</font></h3>",
                        unsafe_allow_html=True)

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

    if analysis_option == "Individual":
        no_games = [player_data['Match Day'].nunique(),
                    None]
        no_events = [player_data.shape[0],
                     None]
    else:
        no_games = [player_data['Match Day'].nunique(),
                    player_data_opponent['Match Day'].nunique()]
        no_events = [player_data.shape[0],
                     player_data_opponent.shape[0]]

    st.sidebar.header(" ")

    ''' Insight Label '''
    if match_day_filter is not None:
        match_day_name = match_day_filter
        season_name = ""
        venue_name = ""
        result_name = ""
    else:
        if period_filter == [1, 34]:
            season_name = ""
        elif period_filter == [1, 17]:
            season_name = f"<font color=#d20614>1st Half of The Season</font> - "
        else:
            season_name = f"<font color=#d20614>2nd Half of The Season</font> - "
        if venue_filter == "All Games":
            venue_name = ""
        else:
            venue_name = f"<font color=#d20614>{venue_filter}</font> - "
        if result_filter == "All Results":
            result_name = ""
        else:
            result_name = f"<font color=#d20614>{result_filter}</font> - "
        match_day_name = ""

    """ Game Events Page """
    if analysis_type == "Game Events":
        page_container = st.empty()
        with page_container.container():

            """ Event Types """
            event_types = player_data['Event'].unique()
            final_event_types = ["Ball Possession"]
            final_event_types.extend(
                [event for event in event_options if event in event_types and event != "Ball Possession"])
            with menu_col:
                event_analysis = st.selectbox(label="Event Type",
                                              options=final_event_types)
                event_outcome_type = player_data[(player_data['Event'] == event_analysis)]['Outcome'].unique()
                event_stat = "Event"
                if event_analysis == "Shots":
                    event_stat = "Event"
                    final_outcome = ["All Shots"]
                    final_outcome.extend([shot for shot in event_shots_type if shot in event_outcome_type])
                    event_outcome = st.selectbox(label="Event Outcome",
                                                 options=final_outcome)
                    event_outcome_label = \
                        event_outcome.replace("All Shots", "Shot").replace("Shot", "Shots").replace("Goal", "Goals")
                    event_analysis_label = ""
                elif event_analysis == "Ball Possession":
                    event_stat = "Ball Possession"
                    event_analysis = True
                    event_outcome = "Successful"
                    event_outcome_label = ""
                    event_analysis_label = "Ball Possession"
                else:
                    if len(event_outcome_type) == 2:
                        event_outcome = st.selectbox(label="Event Outcome",
                                                     options=["Successful", "Unsuccessful"])
                        event_outcome_label = event_outcome
                    else:
                        event_outcome = event_outcome_type[0]
                        event_outcome_label = ""
                    event_analysis_label = event_analysis

            if event_stat == "Ball Possession":
                filter_event_outcome = ["Successful"]
                filter_event_outcome.extend(event_shots_type)
            else:
                if event_outcome == "All Shots":
                    filter_event_outcome = event_shots_type
                else:
                    filter_event_outcome = [event_outcome]

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

            st.sidebar.header(" ")

            """ Game Event Analysis """
            if game_time == "Entire Game":
                final_player_df = player_data[(player_data['Outcome'].isin(filter_event_outcome)) &
                                              (player_data['Minute'] >= time_filter[0]) &
                                              (player_data['Minute'] <= time_filter[1]) &
                                              (player_data[event_stat] == event_analysis)]
            else:
                final_player_df = player_data[(player_data['Period'] == game_time) &
                                              (player_data['Outcome'].isin(filter_event_outcome)) &
                                              (player_data['Minute'] >= time_filter[0]) &
                                              (player_data['Minute'] <= time_filter[1]) &
                                              (player_data[event_stat] == event_analysis)]

            if player_data_opponent is not None:
                if game_time == "Entire Game":
                    final_opponent_df = \
                        player_data_opponent[(player_data_opponent['Outcome'].isin(filter_event_outcome)) &
                                             (player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent[event_stat] == event_analysis)]
                else:
                    final_opponent_df = \
                        player_data_opponent[(player_data_opponent['Period'] == game_time) &
                                             (player_data_opponent['Outcome'].isin(filter_event_outcome)) &
                                             (player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent[event_stat] == event_analysis)]
            else:
                final_opponent_df = None

            if player_data_opponent is None:
                opponent_min_events = 6
            else:
                opponent_min_events = final_opponent_df.shape[0]
            player_min_events = final_player_df.shape[0]
            if player_min_events < 6 or opponent_min_events < 6:
                plot_type = "Position"
            else:
                with menu_col:
                    plot_type = st.selectbox(label="Plot Type",
                                             options=['Heatmap', 'Position'])

            if final_player_df.shape[0] == 0:
                event_analysis_label = "Events"
            player_fig, opponent_fig, player_stats, opponent_stats, position_plot, direction_plot, \
                position_stats, direction_stats = \
                player_analysis(data_player=final_player_df,
                                player_data_opponent=final_opponent_df,
                                player_options=player_option_filter,
                                analysis_option=analysis_option,
                                plot_type=plot_type,
                                no_games=no_games,
                                no_events=no_events,
                                event_outcome=event_outcome_label,
                                event_type=event_analysis_label,
                                player_names=[player_name,
                                              compare_player])

            with plot_col_1:
                st.markdown(
                    f"<b><font color=#d20614>{player_name}</font></b> <b>{event_outcome}</b> <b><font color=#d20614>"
                    f"{event_analysis_label}</font></b> Events between Minute <b>{time_filter[0]}</b> and Minute <b>"
                    f"{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(player_fig)
            with menu_col:
                if player_option_filter == "By Game":
                    st.table(player_stats.style.format(subset=['No Events'], formatter="{:.0f}").format(
                        subset=['% of Events'], formatter="{:.2%}").apply(
                        lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                   for i in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                                   for i in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#d20614'),
                                    ('color', '#ffffff')]}]))
                else:
                    st.table(player_stats.style.format(subset=['No Events'], formatter="{:.0f}").format(
                        subset=['Avg Events/G'], formatter="{:.2f}").apply(
                        lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                   for i in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                                   for i in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#d20614'),
                                    ('color', '#ffffff')]}]))
            if opponent_fig is not None:
                with plot_col_2:
                    st.markdown(
                        f"<b><font color=#392864>{compare_player}</font></b> <b>{event_outcome}</b> <b>"
                        f"<font color=#392864>{event_analysis_label}</font></b> Events between Minute <b>"
                        f"{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                    st.pyplot(opponent_fig)
                with legend_col:
                    if player_option_filter == "By Game":
                        st.table(opponent_stats.style.format(subset=['No Events'], formatter="{:.0f}").format(
                            subset=['% of Events'], formatter="{:.2%}").apply(
                            lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                       for i in range(len(x))], axis=0).apply(
                            lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #392864'
                                       for i in range(len(x))], axis=0).set_table_styles(
                            [{'selector': 'th',
                              'props': [('background-color', '#392864'),
                                        ('color', '#ffffff')]}]))
                    else:
                        st.table(opponent_stats.style.format(subset=['No Events'], formatter="{:.0f}").format(
                            subset=['Avg Events/G'], formatter="{:.2f}").apply(
                            lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                       for i in range(len(x))], axis=0).apply(
                            lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #392864'
                                       for i in range(len(x))], axis=0).set_table_styles(
                            [{'selector': 'th',
                              'props': [('background-color', '#392864'),
                                        ('color', '#ffffff')]}]))

            with menu_col:
                if match_day_name != "":
                    st.markdown(
                        f"<b>Match Day <font color=#d20614>{match_day_name}</font> vs <font color=#d20614>"
                        f"{player_data['Opponent'].unique()[0]}</font> Insights", unsafe_allow_html=True)
                else:
                    if season_name == "" and venue_name == "" and result_name == "":
                        st.markdown(f"<b>Season <font color=#d20614>{season_year}</font> Games Insights</b>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                    unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                    f"#d20614>{player_name}</font></b> had <b><font color=#d20614>{position_stats[1][0]:.2%}</font>"
                    f"</b> <b>{event_outcome_label}</b> <b>{event_analysis_label}</b> in <b>{position_stats[0][0]}"
                    f"</b> of the Pitch and <b><font color=#d20614>{direction_stats[1][0]:.2%}</font></b> in "
                    f" <b>{direction_stats[0][0]}</b> of the Pitch.", unsafe_allow_html=True)
                if analysis_option == "vs Player":
                    with legend_col:
                        if match_day_name != "":
                            st.markdown(f"<b>Match Day <font color=#392864>{match_day_name}</font> vs "
                                        f"<font color=#392864>{player_data_opponent['Opponent'].unique()[0]}"
                                        f"</font> Insights", unsafe_allow_html=True)
                        else:
                            if season_name == "" and venue_name == "" and result_name == "":
                                st.markdown(f"<b>Season <font color=#392864>{season_year}</font> Games Insights</b>",
                                            unsafe_allow_html=True)
                            else:
                                st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                            unsafe_allow_html=True)
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                            f"<font color=#392864>{compare_player}</font></b> had <b><font color=#392864>"
                            f"{position_stats[1][1]:.2%}</font></b> <b>{event_outcome_label}</b> <b>"
                            f"{event_analysis_label}</b> in <b>{position_stats[0][1]}</b> of the Pitch and <b>"
                            f"<font color=#392864>{direction_stats[1][1]:.2%}</font></b> in <b>{direction_stats[0][1]}"
                            f"</b> of the Pitch.", unsafe_allow_html=True)

            if position_plot is not None:
                with st.expander("Display Position and Direction Plots"):
                    info_col, pos_col, _, dir_col, _ = st.columns([2, 5, 0.5, 5, 0.5])
                    with info_col:
                        st.subheader("")
                        st.header("")
                        st.subheader("")
                        st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                        st.markdown(f"<b><font color=#d20614>{player_name}</font></b>", unsafe_allow_html=True)
                        if analysis_option == "vs Player":
                            st.markdown(f"<b><font color=#392864>{compare_player}</font></b>", unsafe_allow_html=True)
                    with pos_col:
                        st.plotly_chart(position_plot, config=config, use_container_width=True)
                    with dir_col:
                        st.plotly_chart(direction_plot, config=config, use_container_width=True)

        """ Passing Network Page """
    elif analysis_type == "Passing Network":
        page_container = st.empty()
        with page_container.container():

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

            st.sidebar.header(" ")

            """ Final Data """
            if game_time == "Entire Game":
                final_player_pass_df = player_data[(player_data['Outcome'] == 'Successful') &
                                                   (player_data['Minute'] >= time_filter[0]) &
                                                   (player_data['Minute'] <= time_filter[1]) &
                                                   (player_data['Event'] == "Passes")]
            else:
                final_player_pass_df = player_data[(player_data['Period'] == game_time) &
                                                   (player_data['Outcome'] == 'Successful') &
                                                   (player_data['Minute'] >= time_filter[0]) &
                                                   (player_data['Minute'] <= time_filter[1]) &
                                                   (player_data['Event'] == "Passes")]

            if player_data_opponent is not None:
                if game_time == "Entire Game":
                    final_opponent_pass_df = \
                        player_data_opponent[(player_data_opponent['Outcome'] == "Successful") &
                                             (player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent['Event'] == "Passes")]
                else:
                    final_opponent_pass_df = \
                        player_data_opponent[(player_data_opponent['Period'] == game_time) &
                                             (player_data_opponent['Outcome'] == "Successful") &
                                             (player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent['Event'] == "Passes")]
            else:
                final_opponent_pass_df = None

            jersey_team, jersey_opp = players_jersey_query(team=team_player,
                                                           team_opp=team_player_opponent)

            player_network_fig, opponent_network_fig, team_network_players, player_top_fig, \
                opponent_network_players, opponent_top_fig, player_tab, opponent_tab = \
                player_passing_network(data_player=final_player_pass_df,
                                       data_opponent=final_opponent_pass_df,
                                       analysis_option=analysis_option,
                                       players_jersey=jersey_team,
                                       opponent_jersey=jersey_opp,
                                       player_names=[player_name, compare_player])

            with plot_col_1:
                st.markdown(
                    f"<b><font color=#d20614>{player_name}</font></b> <b>Passing Network</b> between Minute <b>"
                    f"{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(player_network_fig)
            if analysis_option == "vs Player":
                with plot_col_2:
                    st.markdown(
                        f"<b><font color=#392864>{compare_player}</font></b> <b>Passing Network</b> between Minute <b>"
                        f"{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                    st.pyplot(opponent_network_fig)

            with menu_col:
                st.table(player_tab.style.format(subset=['No of Passes'], formatter="{:.0f}").apply(
                    lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                               for i in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                               for i in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))

                if team_network_players.shape[0] > 0:
                    st.markdown(f"<h4>Players</h4>", unsafe_allow_html=True)
                    for i in range(len(team_network_players) + 1):
                        if i == 0:
                            team_player_name = team_network_players.loc[i, 'Player Name_x']
                            jersey_player_no = team_network_players.loc[i, 'Jersey No_x']
                        else:
                            team_player_name = team_network_players.loc[i - 1, 'Player Name_y']
                            jersey_player_no = team_network_players.loc[i - 1, 'Jersey No_y']
                        if jersey_player_no < 10:
                            st.markdown(f"<b>0{int(jersey_player_no)}<b> - <font color=#d20614>{team_player_name}"
                                        f"</font>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<b>{int(jersey_player_no)}<b> - <font color=#d20614>{team_player_name}"
                                        f"</font>", unsafe_allow_html=True)
                    st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)

            if analysis_option == "vs Player":
                with legend_col:
                    st.table(opponent_tab.style.format(subset=['No of Passes'], formatter="{:.0f}").apply(
                        lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                   for i in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #392864'
                                   for i in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#392864'),
                                    ('color', '#ffffff')]}]))

                if opponent_network_players is not None:
                    with legend_col:
                        st.markdown(f"<h4>Players</h4>", unsafe_allow_html=True)
                        for i in range(len(opponent_network_players) + 1):
                            if i == 0:
                                team_opponent_name = opponent_network_players.loc[i, 'Player Name_x']
                                jersey_opponent_no = opponent_network_players.loc[i, 'Jersey No_x']
                            else:
                                team_opponent_name = opponent_network_players.loc[i - 1, 'Player Name_y']
                                jersey_opponent_no = opponent_network_players.loc[i - 1, 'Jersey No_y']
                            if jersey_opponent_no < 10:
                                st.markdown(
                                    f"<b>0{int(jersey_opponent_no)}<b> - <font color=#392864>"
                                    f"{team_opponent_name}</font>", unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    f"<b>{int(jersey_opponent_no)}<b> - <font color=#392864>"
                                    f"{team_opponent_name}</font>", unsafe_allow_html=True)
                        st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)

            if player_top_fig is not None or \
                    (player_top_fig is None and analysis_option == "vs Player" and opponent_top_fig is not None):
                with st.expander("Display Network Stats Plot"):
                    if analysis_option == "vs Player":
                        info_col, network_plot_1, _, network_plot_2, _ = st.columns([2, 5, 0.5, 5, 0.5])
                    else:
                        info_col, network_plot_1, _ = st.columns([2, 10, 1])
                    with info_col:
                        st.subheader("")
                        st.header("")
                        st.subheader("")
                        st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                        st.markdown(f"<b><font color=#d20614>{player_name}</font></b>", unsafe_allow_html=True)
                    with network_plot_1:
                        if player_top_fig is not None:
                            st.plotly_chart(player_top_fig, config=config, use_container_width=True)
                    if analysis_option == "vs Player":
                        with info_col:
                            st.markdown(f"<b><font color=#392864>{compare_player}</font></b>", unsafe_allow_html=True)
                        with network_plot_2:
                            if opponent_top_fig is not None:
                                st.plotly_chart(opponent_top_fig, config=config, use_container_width=True)

        st.sidebar.header(" ")

        """ Passing Direction Page """
    elif analysis_type == "Passing Distance":
        page_container = st.empty()
        with page_container.container():

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

            st.sidebar.header(" ")

            """ Final Data """
            if game_time == "Entire Game":
                final_player_pass_df = player_data[(player_data['Minute'] >= time_filter[0]) &
                                                   (player_data['Minute'] <= time_filter[1]) &
                                                   (player_data['Event'] == "Passes")]
            else:
                final_player_pass_df = player_data[(player_data['Period'] == game_time) &
                                                   (player_data['Minute'] >= time_filter[0]) &
                                                   (player_data['Minute'] <= time_filter[1]) &
                                                   (player_data['Event'] == "Passes")]

            if player_data_opponent is not None:
                if game_time == "Entire Game":
                    final_opponent_pass_df = \
                        player_data_opponent[(player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent['Event'] == "Passes")]
                else:
                    final_opponent_pass_df = \
                        player_data_opponent[(player_data_opponent['Period'] == game_time) &
                                             (player_data_opponent['Minute'] >= time_filter[0]) &
                                             (player_data_opponent['Minute'] <= time_filter[1]) &
                                             (player_data_opponent['Event'] == "Passes")]
            else:
                final_opponent_pass_df = pd.DataFrame()

            """ Pass Length """
            with menu_col:
                if match_day_filter is not None \
                        and (final_player_pass_df.shape[0] > 0 or final_opponent_pass_df.shape[0] > 0):
                    player_pass_length = st.selectbox(label="Length of Passes",
                                                      options=['All', "Short Passes", "Medium Passes", "Long Passes"])
                else:
                    player_pass_length = "All"

            player_pass_fig, opponent_pass_fig, player_insights, opponent_insights = \
                player_passing_direction(data_player=final_player_pass_df,
                                         data_opponent=final_opponent_pass_df,
                                         analysis_option=analysis_option,
                                         analysis_games=match_day_filter,
                                         pass_length=player_pass_length,
                                         player_names=[player_name, compare_player])
            with plot_col_1:
                if match_day_filter is not None:
                    st.markdown(
                        f"<b>{player_name}</b> <b><font color=#d20614>Passing Events</font></b> between Minute<b> "
                        f"{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                    st.pyplot(player_pass_fig)

            with menu_col:
                st.table(data=player_insights[0].style.format(subset=['% of Events'], formatter="{:.2%}").apply(
                    lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                               for i in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                               for i in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))
                st.markdown("<h4>Legend</h4>", unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614>-> <b>Successful</b></font> Passes", unsafe_allow_html=True)
                st.markdown(f"<font color=#392864>-> <b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Short</b></font> Passes = <b>0</b> - <b>10</b> meters",
                            unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Medium</b></font> Passes = <b>11</b> - <b>25</b> meters",
                            unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Long</b></font> Passes = <b>25+</b> meters",
                            unsafe_allow_html=True)
                if match_day_name != "":
                    st.markdown(f"-> <b>Attack</b> Direction", unsafe_allow_html=True)
                st.markdown("")
                if final_player_pass_df.shape[0] > 0:
                    if match_day_name != "":
                        st.markdown(
                            f"<b>Match Day <font color=#d20614>{match_day_name}</font> vs <font color=#d20614>"
                            f"{player_data['Opponent'].unique()[0]}</font> Insights", unsafe_allow_html=True)
                    else:
                        if season_name == "" and venue_name == "" and result_name == "":
                            st.markdown(f"<b>Season <font color=#d20614>{season_year}</font> Games Insights</b>",
                                        unsafe_allow_html=True)
                        else:
                            st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                        unsafe_allow_html=True)
                if player_insights[3] is not None and player_insights[4] is not None:
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                        f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{player_name}</b> "
                        f"where <b>{player_insights[3][0]}</b> and <b>{player_insights[3][1]}</b> while most of the "
                        f"<b><font color=#392864>Unsuccessful Passes</font></b> of <b>{player_name}</b> where "
                        f"<b>{player_insights[4][0]}</b> and <b>{player_insights[4][1]}</b>.",
                        unsafe_allow_html=True)
                elif player_insights[3] is None and player_insights[4] is not None:
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                        f"{player_name}</b> had <b>No</b> <b><font color=#d20614>Successful Passes</font></b> "
                        f"while most of the <b><font color=#392864>Unsuccessful Passes</font></b> of <b>"
                        f"{player_name}</b> where <b>{player_insights[4][0]}</b> and <b>{player_insights[4][1]}"
                        f"</b>.", unsafe_allow_html=True)
                elif player_insights[3] is not None and player_insights[4] is None:
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                        f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{player_name}</b> "
                        f"where <b>{player_insights[3][0]}</b> and <b>{player_insights[3][1]}</b> while there were "
                        f"<b>No</b> <b><font color=#392864>Unsuccessful Passes</font></b>.",
                        unsafe_allow_html=True)

            if analysis_option == "vs Player":
                with plot_col_2:
                    if match_day_filter is not None:
                        st.markdown(
                            f"<b>{compare_player}</b> <b><font color=#d20614>Passing Events</font></b> between Minute"
                            f"<b> {time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                        st.pyplot(opponent_pass_fig)
                    with legend_col:
                        st.table(data=opponent_insights[0].style.format(subset=['% of Events'],
                                                                        formatter="{:.2%}").apply(
                            lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                       for i in range(len(x))], axis=0).apply(
                            lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #392864'
                                       for i in range(len(x))], axis=0).set_table_styles(
                            [{'selector': 'th',
                              'props': [('background-color', '#392864'),
                                        ('color', '#ffffff')]}]))
                        st.markdown("")
                        if final_opponent_pass_df is not None and final_opponent_pass_df.shape[0] > 0:
                            if match_day_name != "":
                                st.markdown(f"<b>Match Day <font color=#392864>{match_day_name}</font> vs "
                                            f"<font color=#392864>{player_data_opponent['Opponent'].unique()[0]}"
                                            f"</font> Insights", unsafe_allow_html=True)
                            else:
                                if season_name == "" and venue_name == "" and result_name == "":
                                    st.markdown(f"<b>Season <font color=#d20614>{season_year}</font> Games Insights</b>"
                                                f"", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                                unsafe_allow_html=True)
                        if opponent_insights[3] is not None and opponent_insights[4] is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most "
                                f"of the <b><font color=#d20614>Successful Passes</font></b> of <b>{compare_player}"
                                f"</b> where <b>{opponent_insights[3][0]}</b> and <b>{opponent_insights[3][1]}</b> "
                                f"while most of the <b><font color=#392864>Unsuccessful Passes</font></b> of <b>"
                                f"{compare_player}</b> where <b>{opponent_insights[4][0]}</b> and <b>"
                                f"{opponent_insights[4][1]}</b>.", unsafe_allow_html=True)
                        elif opponent_insights[3] is None and opponent_insights[4] is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                                f"{compare_player}</b> had <b>No</b> <b><font color=#d20614>Successful Passes"
                                f"</font></b> while most of the <b><font color=#392864>Unsuccessful Passes</font>"
                                f"</b> of <b>{compare_player}</b> where <b>{opponent_insights[4][0]}</b> and <b>"
                                f"{opponent_insights[4][1]}</b>.", unsafe_allow_html=True)
                        elif opponent_insights[3] is not None and opponent_insights[4] is None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most"
                                f" of the <b><font color=#d20614>Successful Passes</font></b> of <b>"
                                f"{compare_player}</b> where <b>{opponent_insights[3][0]}</b> and <b>"
                                f"{opponent_insights[3][1]}</b> while there were <b>No</b> <b><font color=#392864>"
                                f"Unsuccessful Passes</font></b>.", unsafe_allow_html=True)

            if match_day_filter is not None:
                if player_insights[1] is not None or \
                        (player_insights[1] is None and analysis_option == "vs Player" and
                         opponent_insights[1] is not None):
                    with st.expander("Display Distance Plot"):
                        if analysis_option == "Individual":
                            info_col, player_col, _ = st.columns([2, 10, 0.5])
                        else:
                            info_col, player_col, _, opp_col, _ = st.columns([2, 5, 0.5, 5, 0.5])
                        with info_col:
                            st.subheader("")
                            st.header("")
                            st.subheader("")
                            st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                            st.markdown(
                                f"<font color=#d20614><b>Successful</b></font> Passes", unsafe_allow_html=True)
                            st.markdown(
                                f"<font color=#392864><b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
                        with player_col:
                            if player_insights[1] is not None:
                                st.plotly_chart(player_insights[1], config=config, use_container_width=True)
                                st.plotly_chart(player_insights[2], config=config, use_container_width=True)
                        if analysis_option == "vs Player":
                            with opp_col:
                                if opponent_insights[1] is not None:
                                    st.plotly_chart(opponent_insights[1], config=config, use_container_width=True)
                                    st.plotly_chart(opponent_insights[2], config=config, use_container_width=True)
            else:
                with plot_col_1:
                    if player_insights[1] is not None:
                        st.plotly_chart(player_insights[1], config=config, use_container_width=True)
                        st.plotly_chart(player_insights[2], config=config, use_container_width=True)
                if analysis_option == "vs Player":
                    with plot_col_2:
                        if opponent_insights[1] is not None:
                            st.plotly_chart(opponent_insights[1], config=config, use_container_width=True)
                            st.plotly_chart(opponent_insights[2], config=config, use_container_width=True)

        st.sidebar.header(" ")
    else:
        pass

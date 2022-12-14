import time
import pandas as pd
import streamlit as st
from page_scripts.stats_scripts.game_stats import game_staring_11, game_analysis, game_passing_network, \
    game_passing_direction, pass_sequence_creation, pass_sequence_df, game_pass_sequence
from PIL import Image

# ##### Event Options
event_options = ['Ball Possession', 'Passes', 'Shots', 'Dribbles', 'Corner Awarded', 'Ball Recoveries', 'Interceptions',
                 'Aerial Duels', 'Tackles', 'Loss of Possession', 'Clearances', 'Challenges', 'Blocked Passes',
                 'Fouls', 'Offsides', 'Errors', 'Keeper Saves', 'Keeper Claims', 'Keeper Punches', 'Keeper Pickups',
                 'Keeper Sweeper']


event_options_sequence = ['Goal', 'Unsuccessful Pass', 'Shot', 'Lost Possession', 'Unsuccessful Dribble',
                          'Corner Awarded', 'Ball Recovery', 'Interception', 'Unsuccessful Aerial Duel', 'Tackled',
                          'Dispossessed', 'Clearance', 'Challenged', 'Blocked Pass', 'Fouled', 'Offside', 'Error',
                          'Keeper Save', 'Keeper Claim', 'Keeper Punch', 'Keeper Pickup', 'Keeper Sweep']

event_shots_type = ["Goal", "Shot on Target", "Shot off Target", "Shot on Post", "Own Goal"]


def game_events(data, data_players, match_day):
    """ Plot Configuration """
    config = {'displayModeBar': False}

    # ##### Event Analysis Options
    st.sidebar.header("Analysis Options")
    game_event_menu = ["Starting 11", "Game Events", "Passing Network", "Passing Distance", "Passing Sequence"]
    event_analysis = st.sidebar.selectbox("Select Analysis", game_event_menu)

    """ Create Game Df """
    df_game = data.copy()
    starting_players = data_players.copy()

    """ Game Info """
    home_team = df_game[df_game['Venue'] == 'Home']['Team'].unique()[0]
    away_team = df_game[df_game['Venue'] == 'Away']['Team'].unique()[0]

    """ Starting 11 Page """
    if event_analysis == "Starting 11":
        page_container = st.empty()
        with page_container.container():
            st.markdown(
                f"<h3>Match Day <font color=#d20614>{match_day}</font> - Starting <font color=#d20614>11</font></h3>",
                unsafe_allow_html=True)
            h_players_col, plot_col, a_players_col = st.columns([2, 6, 2])

            starting_players.dropna(inplace=True)
            starting_11_plot = game_staring_11(data=starting_players,
                                               game_teams=[home_team,
                                                           away_team])

            with plot_col:
                st.pyplot(fig=starting_11_plot)
            with h_players_col:
                h_players = starting_players[starting_players['Team'] == home_team]
                st.markdown("")
                home_logo = Image.open(f'images/{home_team}.png')
                st.image(home_logo, width=100, use_column_width=False)
                st.markdown(f"<h4>Starting 11</h4>", unsafe_allow_html=True)
                for i in range(len(h_players)):
                    jersey_no = h_players.loc[i, 'Jersey No']
                    player_name = h_players.loc[i, 'Player Name']
                    if jersey_no < 10:
                        st.markdown(f"<b>0{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                st.markdown(f"-> <b>Attack</b> Direction", unsafe_allow_html=True)

            with a_players_col:
                a_players = starting_players[starting_players['Team'] == away_team]
                st.markdown("")
                away_logo = Image.open(f'images/{away_team}.png')
                st.image(away_logo, width=100, use_column_width=False)
                st.markdown(f"<h4>Starting 11</h4>", unsafe_allow_html=True)
                for i in range(len(h_players)):
                    jersey_no = a_players.loc[i, 'Jersey No']
                    player_name = a_players.loc[i, 'Player Name']
                    if jersey_no < 10:
                        st.markdown(f"<b>0{jersey_no}<b> - <font color=#392864>{player_name}</font>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{jersey_no}<b> - <font color=#392864>{player_name}</font>",
                                    unsafe_allow_html=True)
                st.markdown(f"<- <b>Attack</b> Direction", unsafe_allow_html=True)

            st.sidebar.header(" ")

        """ Game Events Page """
    elif event_analysis == "Game Events":
        page_container = st.empty()
        with page_container.container():
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>Game Events"
                        f"</font></h3>", unsafe_allow_html=True)

            """ Event Types """
            st.sidebar.header("Event Filter")
            event_types = df_game['Event'].unique()
            final_event_types = ["Ball Possession"]
            final_event_types.extend(
                [event for event in event_options if event in event_types and event != "Ball Possession"])
            event_analysis = st.sidebar.selectbox(label="Event Type",
                                                  options=final_event_types)
            event_outcome_type = df_game[(df_game['Event'] == event_analysis)]['Outcome'].unique()
            event_stat = "Event"
            if event_analysis == "Shots":
                event_stat = "Event"
                final_outcome = ["All Shots"]
                final_outcome.extend([shot for shot in event_shots_type if shot in event_outcome_type])
                event_outcome = st.sidebar.selectbox(label="Event Outcome",
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
                    event_outcome = st.sidebar.selectbox(label="Event Outcome",
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

            plot_type = st.sidebar.selectbox(label="Plot Type",
                                             options=['Position', 'Heatmap'])

            """ Minutes Filter """
            time_filter = [df_game['Minute'].min(), df_game['Minute'].max()]
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = df_game['Minute'].min()
                max_minute = df_game['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = df_game[df_game['Period'] == '1st Half']['Minute'].max()
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
                max_minute = df_game[df_game['Period'] == '2nd Half']['Minute'].max()
                if time_option == "Entire Period":
                    time_filter = [45, max_minute]
                elif time_option == "46-60":
                    time_filter = [45, 60]
                elif time_option == "61-75":
                    time_filter = [61, 75]
                elif time_option == "76-90+":
                    time_filter = [76, max_minute]

            """ Game Event Analysis """
            if game_time == "Entire Game":
                final_event_df = df_game[(df_game['Outcome'].isin(filter_event_outcome)) &
                                         (df_game['Minute'] >= time_filter[0]) &
                                         (df_game['Minute'] <= time_filter[1]) &
                                         (df_game[event_stat] == event_analysis)]
            else:
                final_event_df = df_game[(df_game['Period'] == game_time) &
                                         (df_game['Outcome'].isin(filter_event_outcome)) &
                                         (df_game['Minute'] >= time_filter[0]) &
                                         (df_game['Minute'] <= time_filter[1]) &
                                         (df_game[event_stat] == event_analysis)]

            final_period_df = df_game[(df_game['Outcome'].isin(filter_event_outcome)) &
                                      (df_game[event_stat] == event_analysis)]

            analysis_col, _, plot_col, legend_col = st.columns([3, 0.1, 8, 2])

            with legend_col:
                if plot_type == 'Position':
                    st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                    st.markdown(f"<b><font color=#d20614>{home_team}</font></b>", unsafe_allow_html=True)
                    st.markdown(f"<b><font color=#392864>{away_team}</font></b>", unsafe_allow_html=True)
                    st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)
                    heatmap_team = None
                else:
                    heatmap_team = st.selectbox(label='Select Team',
                                                options=[home_team, away_team])
                    if heatmap_team == home_team:
                        st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<- <b>Attack</b></font> Direction", unsafe_allow_html=True)

            no_home_events = df_game[df_game['Venue'] == 'Home'].shape[0]
            no_away_events = df_game[df_game['Venue'] == 'Away'].shape[0]
            no_total_events = [no_home_events, no_away_events]

            event_plot, position_plot, direction_plot, events_data, valid_heatmap, position_insight, \
                direction_insight, period_insight = \
                game_analysis(data=final_event_df,
                              data_period=final_period_df,
                              game_teams=[home_team,
                                          away_team],
                              plot_type=plot_type,
                              event_type=event_analysis_label,
                              event_outcome=event_outcome_label,
                              heat_team=heatmap_team,
                              no_events=no_total_events)

            with analysis_col:
                st.table(data=events_data.style.format(subset=['% of Total Events'],
                                                       formatter="{:.2%}").apply(
                    lambda x: ['background: #ffffff' if _ % 2 == 0 else 'background: #e7e7e7'
                               for _ in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if _ % 2 == 0 else 'color: #d20614'
                               for _ in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))

            with analysis_col:
                if position_plot is not None:
                    st.plotly_chart(position_plot, config=config, use_container_width=True)
                else:
                    st.markdown(f"<h5>The are 0 <font color=#d20614>{event_analysis_label}</font> Events between Minute"
                                f" <font color=#d20614>{time_filter[0]}</font> and Minute "
                                f"<font color=#d20614>{time_filter[1]}</font></h5>.", unsafe_allow_html=True)
                if direction_plot is not None:
                    st.plotly_chart(direction_plot, config=config, use_container_width=True)

            with plot_col:
                st.markdown(f"<b>{event_outcome}</b> <b><font color=#d20614>{event_analysis_label}</font></b> Events "
                            f"between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>",
                            unsafe_allow_html=True)
                if valid_heatmap:
                    st.pyplot(fig=event_plot)
                else:
                    st.markdown(f"<h3>At least <b><font color=#d20614>5</font></b> events are needed to create the "
                                f"Heatmap Plot</h3>", unsafe_allow_html=True)

            with legend_col:
                st.markdown("")
                st.markdown(f"<b>Match Day <font color=#d20614>{match_day}</font> Insights", unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                    f"#d20614>{home_team}</font></b> had <b><font color=#d20614>{position_insight[1][0]:.2%}</font>"
                    f"</b> <b>{event_outcome_label}</b> <b>{event_analysis_label}</b> in <b>{position_insight[0][0]}"
                    f"</b> of the Pitch and <b><font color=#d20614>{direction_insight[1][0]:.2%}</font></b> in "
                    f" <b>{direction_insight[0][0]}</b> of the Pitch.", unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                    f"#392864>{away_team}</font></b> had <b><font color=#392864>{position_insight[1][1]:.2%}</font>"
                    f"</b> <b>{event_outcome_label}</b> <b>{event_analysis_label}</b> in <b>{position_insight[0][1]}"
                    f"</b> of the Pitch and <b><font color=#392864>{direction_insight[1][1]:.2%}</font></b> in "
                    f"<b>{direction_insight[0][1]}</b> of the Pitch.", unsafe_allow_html=True)
                st.markdown(
                    f"<b><font color=#d20614>{home_team}</font></b> had <b><font color=#d20614>"
                    f"{period_insight[1][0]:.2%}</font></b> <b>{event_outcome_label}</b> <b>{event_analysis_label}</b> "
                    f"in the <b>{period_insight[0][0]}</b> of the Game while <b><font color=#392864>{away_team}"
                    f"</font></b> had <b><font color=#392864>{period_insight[1][1]:.2%}</font></b> <b>"
                    f"{event_outcome_label}</b> <b>{event_analysis_label}</b> in the <b>{period_insight[0][1]}</b> of "
                    f"the Game.", unsafe_allow_html=True)

            st.sidebar.header(" ")

        """ Passing Network Page """
    elif event_analysis == "Passing Network":
        page_container = st.empty()
        with page_container.container():
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Passing Network</font></h3>", unsafe_allow_html=True)

            """ Minutes Filter """
            time_filter = [df_game['Minute'].min(), df_game['Minute'].max()]
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = df_game['Minute'].min()
                max_minute = df_game['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = df_game[df_game['Period'] == '1st Half']['Minute'].max()
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
                max_minute = df_game[df_game['Period'] == '2nd Half']['Minute'].max()
                if time_option == "Entire Period":
                    time_filter = [45, max_minute]
                elif time_option == "46-60":
                    time_filter = [45, 60]
                elif time_option == "61-75":
                    time_filter = [61, 75]
                elif time_option == "76-90+":
                    time_filter = [76, max_minute]

            if game_time == "Entire Game":
                final_pass_df = df_game[(df_game['Outcome'] == 'Successful') &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == "Passes")]
            else:
                final_pass_df = df_game[(df_game['Period'] == game_time) &
                                        (df_game['Outcome'] == 'Successful') &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == "Passes")]

            starting_players.dropna(inplace=True)
            analysis_col, _, plot_col, legend_col = st.columns([4, 0.25, 8, 2])
            with legend_col:
                network_team = st.selectbox(label='Select Team',
                                            options=[home_team, away_team])

                legend_players = starting_players[starting_players['Team'] == network_team]
                st.markdown(f"<h4>Players</h4>", unsafe_allow_html=True)
                for i in range(len(legend_players)):
                    jersey_no = legend_players.loc[i, 'Jersey No']
                    player_name = legend_players.loc[i, 'Player Name']
                    if jersey_no < 10:
                        st.markdown(f"<b>0{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                if network_team == home_team:
                    st.markdown(f"-> <b>Attack</b> Direction", unsafe_allow_html=True)
                else:
                    st.markdown(f"<- <b>Attack</b> Direction", unsafe_allow_html=True)

            network_plot, top_plot, starting_insights, top_insights = \
                game_passing_network(data=final_pass_df,
                                     starting_players=starting_players,
                                     plot_team=network_team)
            with plot_col:
                with plot_col:
                    st.markdown(
                        f"<b>{network_team}</b> <b><font color=#d20614>Passing Network</font></b> between Minute<b>"
                        f" {time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(fig=network_plot)

            with analysis_col:
                if top_plot is None:
                    st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the "
                                f"Starting 11 Players of <b>{network_team}</b>, there were <b>"
                                f"<font color=#d20614>0</font></b> Successful Passes.", unsafe_allow_html=True)
                else:
                    st.plotly_chart(top_plot, config=config, use_container_width=True)
                    if starting_insights[0] is not None and starting_insights[1] is not None:
                        st.markdown(f"<b>Match Day <font color=#d20614>{match_day}</font> Insights",
                                    unsafe_allow_html=True)
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the "
                            f"Starting 11 Players of <b>{network_team}</b>, <b><font color=#d20614>"
                            f"{starting_insights[0]}</font></b> was involved in most of the <b>Passes</b> with <b>"
                            f"<font color=#d20614>{int(starting_insights[1])}</font></b>.", unsafe_allow_html=True)
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the Top "
                            f"<b>{top_insights[0]}</b> Successful Passes between Players of <b>{network_team}</b>, "
                            f"we see that <b><font color=#d20614>{top_insights[1]}</font></b> was involved in most of "
                            f"them with <b><font color=#d20614>{int(top_insights[2])}</font></b> out of <b>"
                            f"<font color=#d20614>{top_insights[0]}</font></b>  Successful Passes between Players.",
                            unsafe_allow_html=True)

            st.sidebar.header(" ")

        """ Passing Direction Page """
    elif event_analysis == "Passing Distance":
        page_container = st.empty()
        with page_container.container():
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>Passing Direction"
                        f"</font></h3>", unsafe_allow_html=True)

            """ Minutes Filter """
            time_filter = [df_game['Minute'].min(), df_game['Minute'].max()]
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = df_game['Minute'].min()
                max_minute = df_game['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = df_game[df_game['Period'] == '1st Half']['Minute'].max()
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
                max_minute = df_game[df_game['Period'] == '2nd Half']['Minute'].max()
                if time_option == "Entire Period":
                    time_filter = [45, max_minute]
                elif time_option == "46-60":
                    time_filter = [45, 60]
                elif time_option == "61-75":
                    time_filter = [61, 75]
                elif time_option == "76-90+":
                    time_filter = [76, max_minute]

            """ Final Df """
            if game_time == "Entire Game":
                final_pass_df = df_game[(df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == "Passes")]
            else:
                final_pass_df = df_game[(df_game['Period'] == game_time) &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == "Passes")]

            analysis_col, _, plot_col, legend_col = st.columns([4, 0.25, 8, 2])

            with legend_col:
                """ Team Selection """
                passing_team = st.selectbox(label='Select Team',
                                            options=[home_team, away_team])

                """ Pass Length """
                passing_length = st.selectbox(label="Length of Passes",
                                              options=['All', "Short Passes", "Medium Passes", "Long Passes"])
            passes_plot, passes_stats, length_plot, direction_plot, success_insight, unsuccess_insight = \
                game_passing_direction(data=final_pass_df,
                                       plot_team=passing_team,
                                       pass_length=passing_length)

            with plot_col:
                st.markdown(f"<b>{passing_team}</b> <b><font color=#d20614>Passing Events</font></b> between Minute<b>"
                            f" {time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(fig=passes_plot)

            with legend_col:
                st.markdown("<h4>Legend</h4>", unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614>-> <b>Successful</b></font> Passes", unsafe_allow_html=True)
                st.markdown(f"<font color=#392864>-> <b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Short</b></font> Passes = <b>0</b> - <b>10</b> meters",
                            unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Medium</b></font> Passes = <b>11</b> - <b>25</b> meters",
                            unsafe_allow_html=True)
                st.markdown(f"<font color=#d20614><b>Long</b></font> Passes = <b>25+</b> meters",
                            unsafe_allow_html=True)
                if passing_team == home_team:
                    st.markdown(f"-> <b>Attack</b> Direction", unsafe_allow_html=True)
                else:
                    st.markdown(f"<- <b>Attack</b> Direction", unsafe_allow_html=True)

            with analysis_col:
                if passes_stats is not None:
                    st.table(data=passes_stats.style.format(subset=['% of Events'],
                                                            formatter="{:.2%}").apply(
                        lambda x: ['background: #ffffff' if _ % 2 == 0 else 'background: #e7e7e7'
                                   for _ in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if _ % 2 == 0 else 'color: #d20614'
                                   for _ in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#d20614'),
                                    ('color', '#ffffff')]}]))

                    st.plotly_chart(length_plot, config=config, use_container_width=True)
                    st.plotly_chart(direction_plot, config=config, use_container_width=True)

                    with legend_col:
                        st.markdown(f"<b>Match Day <font color=#d20614>{match_day}</font> Insights",
                                    unsafe_allow_html=True)
                        if success_insight is not None and unsuccess_insight is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                                f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{passing_team}</b> "
                                f"where <b>{success_insight[0]}</b> and <b>{success_insight[1]}</b> while most of the "
                                f"<b><font color=#392864>Unsuccessful Passes</font></b> of <b>{passing_team}</b> where "
                                f"<b>{unsuccess_insight[0]}</b> and <b>{unsuccess_insight[1]}</b>.",
                                unsafe_allow_html=True)
                        elif success_insight is None and unsuccess_insight is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                                f"{passing_team}</b> had <b>No</b> <b><font color=#d20614>Successful Passes</font></b> "
                                f"while most of the <b><font color=#392864>Unsuccessful Passes</font></b> of <b>"
                                f"{passing_team}</b> where <b>{unsuccess_insight[0]}</b> and <b>{unsuccess_insight[1]}"
                                f"</b>.", unsafe_allow_html=True)
                        elif success_insight is not None and unsuccess_insight is None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                                f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{passing_team}</b> "
                                f"where <b>{success_insight[0]}</b> and <b>{success_insight[1]}</b> while there were "
                                f"<b>No</b> <b><font color=#392864>Unsuccessful Passes</font></b>.",
                                unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<h4>No <font color=#d20614>Pass</font> Events between Minute <font color=#d20614>"
                        f"{time_filter[0]}</font></b> and Minute <font color=#d20614>{time_filter[1]}</font></b>."
                        f"</h4>", unsafe_allow_html=True)

            st.sidebar.header(" ")

        """ Passing Sequence Page """
    elif event_analysis == "Passing Sequence":
        st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                    f"Passing Sequence</font></h3>", unsafe_allow_html=True)

        legend_col, _, plot_col, button_col, _ = st.columns([2, 0.25, 8, 2, 1])

        with button_col:
            sequence_team = st.selectbox(label='Select Team',
                                         options=[home_team, away_team])

        """ Final Df """
        sequence_df, total_stats = pass_sequence_creation(data=df_game,
                                                          sequence_team=sequence_team)
        valid_sequence_options = sequence_df['Sequence End'].unique()
        close_sequence_options = [stat for stat in event_options_sequence if stat in valid_sequence_options]

        with button_col:
            close_event = st.selectbox(label="Pass Sequence End",
                                       options=close_sequence_options)
        no_event_sequence = len(sequence_df[sequence_df['Sequence End'] == close_event]['Sequence No'].unique())
        with button_col:
            no_close_event = st.selectbox(label="Pass Sequence No",
                                          options=[i for i in range(1, no_event_sequence + 1)])

        """ Passing Sequence Analysis """
        if sequence_team == home_team:
            sequence_team_type = "Home"
        else:
            sequence_team_type = "Away"

        final_pass_seq_df, legend_players, event_stats = pass_sequence_df(data=sequence_df,
                                                                          team_sequence=sequence_team_type,
                                                                          close_sequence=close_event,
                                                                          no_sequence=no_close_event,
                                                                          players_info=data_players)
        sequence_stats = pd.concat([total_stats, event_stats])

        start_sequence = st.sidebar.button("Start Sequence")
        if start_sequence:
            with legend_col:
                sequence_logo = Image.open(f'images/{sequence_team}.png')
                st.image(sequence_logo, width=100, use_column_width=False)
                st.markdown(f"<h4>Players</h4>", unsafe_allow_html=True)
                for i in range(len(legend_players)):
                    jersey_no = legend_players.loc[i, 'Jersey No']
                    player_name = legend_players.loc[i, 'Player Name']
                    if jersey_no < 10:
                        st.markdown(f"<b>0{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                if sequence_team == home_team:
                    st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)
                else:
                    st.markdown(f"<- <b>Attack</b></font> Direction", unsafe_allow_html=True)

            with button_col:
                st.table(data=sequence_stats.style.format(subset=['#'], formatter="{:.2f}").apply(
                    lambda x: ['background: #ffffff' if _ % 2 == 0 else 'background: #e7e7e7'
                               for _ in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if _ % 2 == 0 else 'color: #d20614'
                               for _ in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))

            with plot_col:
                plot_container = st.empty()
                for i in range(1, len(final_pass_seq_df) + 1):
                    with plot_container.container():
                        fig_pass_sequence, game_minute = game_pass_sequence(data=final_pass_seq_df,
                                                                            players_info=data_players,
                                                                            event_no=i)
                        st.markdown(f"<b><font color=#d20614>{sequence_team}</font> <b>Sequence Pass No:</b> <b>"
                                    f"<font color=#d20614>{no_close_event}</font></b> with Event Outcome <b>"
                                    f"<font color=#d20614>{close_event}</font></b> - Minute = <b><font color=#d20614>"
                                    f"{game_minute:.0f}</font></b>", unsafe_allow_html=True)
                        st.pyplot(fig_pass_sequence)
                        time.sleep(0.01)

        st.sidebar.header(" ")

    else:
        pass

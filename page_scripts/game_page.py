import time
import math
import streamlit as st
from PIL import Image
from page_scripts.stats_scripts.game_stats import game_staring_11, game_analysis, \
    game_passing_network, game_passing_direction, game_event_sequence


event_options = ['Passes', 'Goals', 'Shots Saved', 'Shots Missed', 'Shots On Post', 'Penalties', 'Ball Touches',
                 'Dribbles', 'Corner Awarded', 'Ball Recoveries', 'Interceptions', 'Aerial Duels', 'Tackles',
                 'Dispossessions', 'Clearances', 'Challenges', 'Blocked Passes', 'Fouls', 'Offsides', 'Errors',
                 'Keeper Saves', 'Keeper Claims', 'Keeper Punches', 'Keeper Pickups', 'Keeper Sweeper']


def game_events(data, data_info, data_players, match_day):
    """ Plot Configuration """
    config = {'displayModeBar': False}

    # ##### Event Analysis Options
    st.sidebar.header("Analysis Options")
    game_event_menu = ["Starting 11", "Game Events", "Passing Network", "Passing Direction", "Event Sequence"]
    event_analysis = st.sidebar.selectbox("Select Analysis", game_event_menu)

    """ Create Game Df """
    df_game = data.copy()
    game_info = data_info.copy()

    """ Game Info """
    home_team = df_game[df_game['Venue'] == 'Home']['Team'].unique()[0]
    away_team = df_game[df_game['Venue'] == 'Away']['Team'].unique()[0]

    home_score = game_info[(game_info['Team'] == home_team) &
                           (game_info['Match Day'] == match_day)]['FT Score'].values[0]
    away_score = game_info[(game_info['Team'] == away_team) &
                           (game_info['Match Day'] == match_day)]['FT Score'].values[0]

    """ Page Configuration """
    if event_analysis == "Event Sequence":
        tab_col, _, home_col, hscore_col, sep_col, ascore_col, away_col, _ = st.columns([4.75, 2.5, 2, 2, 2, 1.5, 2, 6])
    elif event_analysis != "Starting 11":
        tab_col, _, home_col, hscore_col, sep_col, ascore_col, away_col, _ = st.columns([8.5, 2.5, 2, 2, 2, 1, 2, 6.5])
    else:
        tab_col, _, home_col, hscore_col, sep_col, ascore_col, away_col, _ = st.columns([4.75, 2.5, 2, 2, 2, 1.5, 2, 6])

    with home_col:
        home_logo = Image.open(f'images/{home_team}.png')
        st.image(home_logo, width=100)
    with hscore_col:
        st.markdown("")
        st.title(home_score)

    with sep_col:
        st.markdown("")
        st.title(":")

    with away_col:
        away_logo = Image.open(f'images/{away_team}.png')
        st.image(away_logo, width=100)

    with ascore_col:
        st.markdown("")
        st.title(away_score)

    """ Minutes Filter """
    if event_analysis != "Starting 11":
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

        """ Starting 11 Page """
    if event_analysis == "Starting 11":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - Starting <font color=#d20614>11</font>"
                        f"</h3>", unsafe_allow_html=True)
        h_players_col, plot_col, a_players_col = st.columns([2, 6, 2])

        starting_11_plot = game_staring_11(data=data_players,
                                           game_teams=[home_team,
                                                       away_team])

        with plot_col:
            st.pyplot(fig=starting_11_plot)
        with h_players_col:
            h_players = data_players[data_players['Team'] == home_team]
            st.header("")
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

        with a_players_col:
            a_players = data_players[data_players['Team'] == away_team]
            st.header("")
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
        st.sidebar.header(" ")

        """ Game Events Page """
    elif event_analysis == "Game Events":

        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Game Events</font></h3>", unsafe_allow_html=True)

        """ Event Types """
        st.sidebar.header("Event Filter")
        if game_time == "Entire Game":
            event_types = df_game[(df_game['Minute'] >= time_filter[0]) &
                                  (df_game['Minute'] <= time_filter[1])]['Event'].unique()
        else:
            event_types = df_game[(df_game['Period'] == game_time) &
                                  (df_game['Minute'] >= time_filter[0]) &
                                  (df_game['Minute'] <= time_filter[1])]['Event'].unique()

        final_event_types = [event for event in event_options if event in event_types]
        event_analysis = st.sidebar.selectbox(label="Event Type",
                                              options=final_event_types)

        event_outcome_type = df_game[(df_game['Minute'] >= time_filter[0]) &
                                     (df_game['Minute'] <= time_filter[1]) &
                                     (df_game['Event'] == event_analysis)]['Outcome'].unique()
        if len(event_outcome_type) == 2:
            event_outcome = st.sidebar.selectbox(label="Event Outcome",
                                                 options=["Successful", "Unsuccessful"])
            event_outcome_label = event_outcome
        else:
            event_outcome = event_outcome_type[0]
            event_outcome_label = ""

        plot_type = st.sidebar.selectbox(label="Plot Type",
                                         options=['Position', 'Heatmap'])

        """ Game Event Analysis """
        if game_time == "Entire Game":
            final_event_df = df_game[(df_game['Outcome'] == event_outcome) &
                                     (df_game['Minute'] >= time_filter[0]) &
                                     (df_game['Minute'] <= time_filter[1]) &
                                     (df_game['Event'] == event_analysis)]
        else:
            final_event_df = df_game[(df_game['Period'] == game_time) &
                                     (df_game['Outcome'] == event_outcome) &
                                     (df_game['Minute'] >= time_filter[0]) &
                                     (df_game['Minute'] <= time_filter[1]) &
                                     (df_game['Event'] == event_analysis)]

        final_period_df = df_game[(df_game['Outcome'] == event_outcome) &
                                  (df_game['Event'] == event_analysis)]

        analysis_col, plot_col, legend_col = st.columns([4, 8, 2])

        with legend_col:
            if plot_type == 'Position':
                st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                st.markdown(f"<b><font color=#d20614>{home_team}</font></b>", unsafe_allow_html=True)
                st.markdown(f"<b><font color=#392864>{away_team}</font></b>", unsafe_allow_html=True)
                heatmap_team = None
            else:
                heatmap_team = st.selectbox(label='Select Team',
                                            options=[home_team, away_team])

        no_home_events = df_game[df_game['Venue'] == 'Home'].shape[0]
        no_away_events = df_game[df_game['Venue'] == 'Away'].shape[0]
        no_total_events = [no_home_events, no_away_events]

        event_plot, position_plot, direction_plot, events_data, valid_heatmap, \
            position_insight, direction_insight, period_insight = game_analysis(data=final_event_df,
                                                                                data_period=final_period_df,
                                                                                game_teams=[home_team,
                                                                                            away_team],
                                                                                plot_type=plot_type,
                                                                                event_type=event_analysis,
                                                                                event_outcome=event_outcome_label,
                                                                                heat_team=heatmap_team,
                                                                                no_events=no_total_events)

        with analysis_col:
            st.table(data=events_data.style.format(subset=['% of Total Events'],
                                                   formatter="{:.2%}").apply(
                lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                           for i in range(len(x))], axis=0).apply(
                lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                           for i in range(len(x))], axis=0).set_table_styles(
                [{'selector': 'th',
                  'props': [('background-color', '#d20614'),
                            ('color', '#ffffff')]}]))

        with analysis_col:
            st.plotly_chart(position_plot, config=config, use_container_width=True)
            st.plotly_chart(direction_plot, config=config, use_container_width=True)

        with plot_col:
            st.markdown(f"<b>{event_outcome}</b> <b><font color=#d20614>{event_analysis}</font></b> Events between "
                        f"Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
            if valid_heatmap:
                st.pyplot(fig=event_plot)
            else:
                st.markdown(f"<h3>At least <b><font color=#d20614>5</font></b> events are needed to create the Heatmap "
                            f"Plot</h3>", unsafe_allow_html=True)

        with legend_col:
            st.subheader("")
            st.header("")
            st.subheader("")
            st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                        f"#d20614>{home_team}</font></b> had <b><font color=#d20614>{position_insight[1][0]:.2%}</font>"
                        f"</b> <b>{event_outcome_label}</b> <b>{event_analysis}</b> in the <b>{position_insight[0][0]}"
                        f"</b> of the Pitch and <b><font color=#d20614>{direction_insight[1][0]:.2%}</font></b> in the"
                        f" <b>{direction_insight[0][0]}</b> of the Pitch.", unsafe_allow_html=True)
            st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                        f"#392864>{away_team}</font></b> had <b><font color=#392864>{position_insight[1][1]:.2%}</font>"
                        f"</b> <b>{event_outcome_label}</b> <b>{event_analysis}</b> in the <b>{position_insight[0][1]}"
                        f"</b> of the Pitch and <b><font color=#392864>{direction_insight[1][1]:.2%}</font></b> in the "
                        f"<b>{direction_insight[0][1]}</b> of the Pitch.", unsafe_allow_html=True)
            st.markdown(f"<b><font color=#d20614>{home_team}</font></b> had <b><font color=#d20614>"
                        f"{period_insight[1][0]:.2%}</font></b> <b>{event_outcome_label}</b> <b>{event_analysis}</b> in"
                        f" the <b>{period_insight[0][0]}</b> of the Game while <b><font color=#d20614>{away_team}"
                        f"</font></b> had <b><font color=#d20614>{period_insight[1][1]:.2%}</font></b> <b>"
                        f"{event_outcome_label}</b> <b>{event_analysis}</b> in the <b>{period_insight[0][1]}</b> of the"
                        f" Game.", unsafe_allow_html=True)

        st.sidebar.header(" ")

        """ Passing Network Page """
    elif event_analysis == "Passing Network":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Passing Network</font></h3>", unsafe_allow_html=True)
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

        analysis_col, plot_col, legend_col = st.columns([4, 8, 2])
        with legend_col:
            network_team = st.selectbox(label='Select Team',
                                        options=[home_team, away_team])

            legend_players = data_players[data_players['Team'] == network_team]
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

        network_plot, top_plot, starting_insights, top_insights = game_passing_network(data=final_pass_df,
                                                                                       starting_players=data_players,
                                                                                       plot_team=network_team)
        with plot_col:
            with plot_col:
                st.markdown(f"<b>{network_team}</b> <b><font color=#d20614>Passing Network</font></b> between Minute<b>"
                            f" {time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>", unsafe_allow_html=True)
            st.pyplot(fig=network_plot)

        with analysis_col:
            if top_plot is None:
                st.markdown("")
                st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the "
                            f"Starting 11 Players of <b>{network_team}</b>, there were less then <b>"
                            f"<font color=#d20614>2</font></b> Successful Passes.", unsafe_allow_html=True)
            else:
                st.plotly_chart(top_plot, config=config, use_container_width=True)

                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the Starting "
                    f"11 Players of <b>{network_team}</b>, <b><font color=#d20614>{starting_insights[0]}</font></b>"
                    f" was involved in most of the <b>Passes</b> with <b><font color=#d20614>"
                    f"{int(starting_insights[1])}</font></b>.", unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the Top "
                    f"<b>{top_insights[0]}</b> Successful Passes between Players of <b>{network_team}</b>, we see that "
                    f"<b><font color=#d20614>{top_insights[1]}</font></b> was involved in most of them with <b>"
                    f"<font color=#d20614>{int(top_insights[2])}</font></b> out of <b><font color=#d20614>"
                    f"{top_insights[0]}</font></b>  Successful Passes between Players.", unsafe_allow_html=True)

        st.sidebar.header(" ")

        """ Passing Direction Page """
    elif event_analysis == "Passing Direction":

        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Passing Direction</font></h3>", unsafe_allow_html=True)

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

        analysis_col, plot_col, legend_col = st.columns([4, 8, 2])

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
            st.markdown(f"<font color=#d20614><b>Long</b></font> Passes = <b>25+</b> meters", unsafe_allow_html=True)

        with analysis_col:
            if passes_stats is not None:
                st.table(data=passes_stats.style.format(subset=['% of Events'],
                                                        formatter="{:.2%}").apply(
                    lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                               for i in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                               for i in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))

                st.plotly_chart(length_plot, config=config, use_container_width=True)
                st.plotly_chart(direction_plot, config=config, use_container_width=True)

                with legend_col:
                    st.subheader("")
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of the "
                        f"<b><font color=#d20614>Successful Passes</font></b> of <b>{passing_team}</b> where "
                        f"<b>{success_insight[0]}</b> and <b>{success_insight[1]}</b> while most of the "
                        f"<b><font color=#d20614>Unsuccessful Passes</font></b> of <b>{passing_team}</b> where "
                        f"<b>{success_insight[0]}</b> and <b>{success_insight[1]}</b>.", unsafe_allow_html=True)
            else:
                st.markdown(f"<h4>No <font color=#d20614>Pass</font> Events between Minute <font color=#d20614>"
                            f"{time_filter[0]}</font></b> and Minute <font color=#d20614>{time_filter[1]}</font></b>."
                            f"</h4>", unsafe_allow_html=True)

        st.sidebar.header(" ")

        """ Event Sequence Page """
    elif event_analysis == "Event Sequence":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Game Event Sequence</font></h3>", unsafe_allow_html=True)

        legend_col, plot_col, button_col = st.columns([3, 10, 3])
        """ Event Types """
        if game_time == "Entire Game":
            sequence_events = df_game[(df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1])]['Event'].unique()
        else:
            sequence_events = df_game[(df_game['Period'] == game_time) &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1])]['Event'].unique()

        final_sequence_events = [event for event in event_options if event in sequence_events]

        """ Event Filter """
        st.sidebar.header("Event Filter")

        sequence_event = st.sidebar.selectbox(label="Event Type",
                                              options=final_sequence_events)

        sequence_outcome_types = df_game[(df_game['Minute'] >= time_filter[0]) &
                                         (df_game['Minute'] <= time_filter[1]) &
                                         (df_game['Event'] == sequence_event)]['Outcome'].unique()
        if len(sequence_outcome_types) == 2:
            sequence_outcome = st.sidebar.selectbox(label="Event Outcome",
                                                    options=["Successful", "Unsuccessful"])
        else:
            sequence_outcome = sequence_outcome_types[0]

        """ Game Sequence Analysis """
        if game_time == "Entire Game":
            final_sequence_df = df_game[(df_game['Outcome'] == sequence_outcome) &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == sequence_event)].reset_index(drop=True)
        else:
            final_sequence_df = df_game[(df_game['Period'] == game_time) &
                                        (df_game['Outcome'] == sequence_outcome) &
                                        (df_game['Minute'] >= time_filter[0]) &
                                        (df_game['Minute'] <= time_filter[1]) &
                                        (df_game['Event'] == sequence_event)].reset_index(drop=True)

        if final_sequence_df.shape[0] > 5:
            plot_type = st.sidebar.selectbox(label="Plot Type",
                                             options=['Position', "Heatmap"])
        else:
            plot_type = "Position"

        if plot_type == "Heatmap":
            with legend_col:
                sequence_team = st.selectbox(label='Select Team',
                                             options=[home_team, away_team])
                team_logo = Image.open(f'images/{sequence_team}.png')
                st.image(team_logo, width=100)
                event_length = final_sequence_df[final_sequence_df['Team'] == sequence_team].shape[0]
        else:
            sequence_team = None
            event_length = final_sequence_df.shape[0]

        with button_col:
            start_sequence = st.button("Start Sequence")
        if start_sequence:
            with legend_col:
                if plot_type == "Position":
                    st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                    st.markdown(f"<b><font color=#d20614>{home_team}</font></b>", unsafe_allow_html=True)
                    st.markdown(f"<b><font color=#392864>{away_team}</font></b>", unsafe_allow_html=True)
            with plot_col:
                placeholder = st.empty()
                for i in range(0, event_length + 1):
                    with placeholder.container():
                        fig_sequence, game_minute = game_event_sequence(data=final_sequence_df,
                                                                        event_filter=i,
                                                                        team_plot=sequence_team,
                                                                        type_plot=plot_type,
                                                                        event_teams=[home_team,
                                                                                     away_team])
                        if math.isnan(game_minute):
                            game_minute = min_minute

                        print(min_minute, game_minute)
                        st.markdown(f"Game Minute <b><font color=#d20614>{game_minute}</font></b>",
                                    unsafe_allow_html=True)
                        st.pyplot(fig_sequence, clear_figure=True)
                        if sequence_event == "Passes":
                            time.sleep(0.01)
                        else:
                            time.sleep(1)

            with button_col:
                st.success("All Events have been plotted!")

    else:
        pass

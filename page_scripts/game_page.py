import streamlit as st
from PIL import Image
from page_scripts.stats_scripts.game_stats import game_staring_11, game_analysis, \
    game_passing_network, game_passing_direction


def game_events(data, data_info, data_players, match_day):
    """ Plot Configuration """
    config = {'displayModeBar': False}

    # ##### Algo Options
    st.sidebar.header("Analysis Options")
    game_event_menu = ["Starting 11", "Game Events", "Passing Network", "Passing Direction"]
    game_event_analysis = st.sidebar.selectbox("Select Analysis", game_event_menu)

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
    if game_event_analysis != "Starting 11":
        tab_col, _, home_col, hscore_col, sep_col, ascore_col, away_col, _ = st.columns([7, 2.5, 2, 2, 2, 1, 2, 6])
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

    if game_event_analysis == "Starting 11":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - Starting <font color=#d20614>11</font>"
                        f"</h3>", unsafe_allow_html=True)
        h_players_col, plot_col, a_players_col = st.columns([2, 10, 2])

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

    elif game_event_analysis == "Game Events":

        """ Minutes Filter """
        st.sidebar.header("Event Options")
        min_minute = df_game['Minute'].min()
        max_minute = df_game['Minute'].max()
        time_filter = st.sidebar.select_slider(label="Select Time Period",
                                               options=[i for i in range(min_minute, max_minute + 1)],
                                               value=(min_minute, max_minute))

        """ Event Options """
        event_outcome = st.sidebar.selectbox(label="Event Outcome",
                                             options=["Successful", "Unsuccessful"])
        event_types = df_game[(df_game['Minute'] >= time_filter[0])
                              & (df_game['Minute'] <= time_filter[1])
                              & (df_game['Outcome'] == event_outcome)]['Event'].unique()
        event_types.sort()
        event_analysis = st.sidebar.selectbox(label="Event Type",
                                              options=event_types)
        plot_type = st.sidebar.selectbox(label="Plot Type",
                                         options=['Position', 'Heatmap'])

        """ Game Event Analysis """
        final_event_df = df_game[(df_game['Outcome'] == event_outcome) &
                                 (df_game['Minute'] >= time_filter[0]) &
                                 (df_game['Minute'] <= time_filter[1]) &
                                 (df_game['Event'] == event_analysis)]

        final_period_df = df_game[(df_game['Outcome'] == event_outcome) &
                                  (df_game['Event'] == event_analysis)]

        analysis_col, plot_col, legend_col = st.columns([4, 10, 2])

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
                                                                                event_outcome=event_outcome,
                                                                                event_type=event_analysis,
                                                                                heat_team=heatmap_team,
                                                                                no_events=no_total_events)

        with tab_col:
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
                st.markdown(f"<h3>At least <b><font color=#d20614>5</font></b> events are needed to create the HeatMap "
                            f"Plot</h3>", unsafe_allow_html=True)

        with legend_col:
            st.subheader("")
            st.header("")
            st.subheader("")
            st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                        f"#d20614>{home_team}</font></b> had <b><font color=#d20614>{position_insight[1][0]:.2%}</font>"
                        f"</b> <b>{event_outcome}</b> <b>{event_analysis}</b> in <b>{position_insight[0][0]}</b> of "
                        f"the Pitch and <b><font color=#d20614>{direction_insight[1][0]:.2%}</font></b> in <b>"
                        f"{direction_insight[0][0]}</b> of the Pitch.", unsafe_allow_html=True)
            st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                        f"#392864>{away_team}</font></b> had <b><font color=#392864>{position_insight[1][1]:.2%}</font>"
                        f"</b> <b>{event_outcome}</b> <b>{event_analysis}</b> in <b>{position_insight[0][1]}</b> of "
                        f"the Pitch and <b><font color=#392864>{direction_insight[1][1]:.2%}</font></b> in <b>"
                        f"{direction_insight[0][1]}</b> of the Pitch.", unsafe_allow_html=True)
            st.markdown(f"<b><font color=#d20614>{home_team}</font></b> had <b><font color=#d20614>"
                        f"{period_insight[1][0]:.2%}</font></b> <b>"
                        f"{event_outcome}</b> <b>{event_analysis}</b> in <b>{period_insight[0][0]}</b> of the Game "
                        f"while <b><font color=#d20614>{away_team}</font></b> had <b><font color=#d20614>"
                        f"{period_insight[1][1]:.2%}</font></b> <b>"
                        f"{event_outcome}</b> <b>{event_analysis}</b> in <b>{period_insight[0][1]}</b> of the Game.",
                        unsafe_allow_html=True)

            st.sidebar.header(" ")
    elif game_event_analysis == "Passing Network":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Passing Network</font></h3>", unsafe_allow_html=True)

        """ Minutes Filter """
        st.sidebar.header("Event Options")
        min_minute = df_game['Minute'].min()
        max_minute = df_game['Minute'].max()
        time_filter = st.sidebar.select_slider(label="Select Time Period",
                                               options=[i for i in range(min_minute, max_minute + 1)],
                                               value=(min_minute, max_minute))

        final_pass_df = df_game[(df_game['Outcome'] == 'Successful') &
                                (df_game['Minute'] >= time_filter[0]) &
                                (df_game['Minute'] <= time_filter[1]) &
                                (df_game['Event'] == "Pass")]

        analysis_col, plot_col, legend_col = st.columns([4, 10, 2])
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
            st.pyplot(fig=network_plot)

        with analysis_col:
            if top_plot is None:
                st.markdown("")
                st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the "
                            f"Starting 11 Players of <b>{network_team}</b>, there were less then <b>"
                            f"<font color=#d20614>2</font></b> Successfull Passes.", unsafe_allow_html=True)
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
    elif game_event_analysis == "Passing Direction":
        with tab_col:
            st.subheader("")
            st.markdown(f"<h3>Match Day <font color=#d20614>{match_day}</font> - <font color=#d20614>"
                        f"Passing Direction</font></h3>", unsafe_allow_html=True)

        """ Minutes Filter """
        st.sidebar.header("Event Options")
        min_minute = df_game['Minute'].min()
        max_minute = df_game['Minute'].max()
        time_filter = st.sidebar.select_slider(label="Select Time Period",
                                               options=[i for i in range(min_minute, max_minute + 1)],
                                               value=(min_minute, max_minute))

        """ Final Df """
        final_pass_df = df_game[(df_game['Minute'] >= time_filter[0]) &
                                (df_game['Minute'] <= time_filter[1]) &
                                (df_game['Event'] == "Pass")]

        analysis_col, plot_col, legend_col = st.columns([4, 10, 2])

        with legend_col:
            """ Team Selection """
            passing_team = st.selectbox(label='Select Team',
                                        options=[home_team, away_team])

            """ Pass Length """
            passing_length = st.selectbox(label="Length of Passes",
                                          options=['All', "Short Pass", "Medium Pass", "Long Pass"])
        passes_plot = game_passing_direction(data=final_pass_df,
                                             plot_team=passing_team,
                                             pass_length=passing_length)

        with plot_col:
            st.pyplot(fig=passes_plot)

        with legend_col:
            st.markdown("<h4>Legend</h4>", unsafe_allow_html=True)
            st.markdown(f"<font color=#d20614>-> <b>Successful</b></font> Passes", unsafe_allow_html=True)
            st.markdown(f"<font color=#392864>-> <b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
            st.markdown(f"<font color=#d20614><b>Short</b></font> Pass = <b>0</b> - <b>10</b> meters",
                        unsafe_allow_html=True)
            st.markdown(f"<font color=#d20614><b>Medium</b></font> Pass = <b>11</b> - <b>25</b> meters",
                        unsafe_allow_html=True)
            st.markdown(f"<font color=#d20614><b>Long</b></font> Pass = <b>25+</b> meters", unsafe_allow_html=True)
        st.sidebar.header(" ")
    else:
        pass

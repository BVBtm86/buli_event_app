import streamlit as st
from PIL import Image
from page_scripts.stats_scripts.team_stats import team_events_analysis, team_passing_network, team_passing_direction

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


def team_events(data, players_data, analysis_option, analysis_team, team_name, opp_name, page_filter):
    """ Page Configuration """
    config = {'displayModeBar': False}

    team_data = data.copy()
    player_data = players_data.copy()
    match_days_filter = team_data['Match Day'].unique()
    time_filter = [team_data['Minute'].min(),
                   team_data['Minute'].max()]

    if analysis_option == "vs Opponents":
        no_games = [team_data[team_data['Team'] == team_name]['Match Day'].nunique(),
                    team_data[team_data['Team'] == team_name]['Match Day'].nunique()]
    else:
        no_games = [team_data[team_data['Team'] == team_name]['Match Day'].nunique(),
                    team_data[team_data['Team'] == opp_name]['Match Day'].nunique()]

    name_col, _ = st.columns([10, 2])

    """ Page Label """
    if team_name == opp_name:
        opp_label = "All Opponents"
    else:
        opp_label = opp_name
    with name_col:
        st.markdown(f"<h3><font color=#d20614>{team_name}</font> vs <font color=#392864>{opp_label}</font> - "
                    f"{analysis_option}</h3>", unsafe_allow_html=True)

    if page_filter[0] == "Entire Season":
        season_name = ""
    else:
        season_name = f"<font color=#d20614>{page_filter[0]}</font> - "
    if page_filter[1] == "All Games":
        venue_name = ""
    else:
        venue_name = f"<font color=#d20614>{page_filter[1]}</font> - "
    if page_filter[2] == "All Results":
        result_name = ""
    else:
        result_name = f"<font color=#d20614>{page_filter[2]}</font> - "

    """ Game Events Page """
    if analysis_option == "Game Events":
        page_container = st.empty()
        with page_container.container():
            menu_col, _, plot_1, _, plot_2, _ = st.columns([3, 0.5, 6, 0.5, 6, 0.5])

            """ Event Types """
            event_types = team_data[(team_data['Minute'] >= time_filter[0]) &
                                    (team_data['Minute'] <= time_filter[1])]['Event'].unique()

            final_event_types = [event for event in event_options if event in event_types]
            with menu_col:
                event_analysis = st.selectbox(label="Event Type",
                                              options=final_event_types)

                event_outcome_type = team_data[(team_data['Minute'] >= time_filter[0]) &
                                               (team_data['Minute'] <= time_filter[1]) &
                                               (team_data['Event'] == event_analysis)]['Outcome'].unique()
                if len(event_outcome_type) == 2:
                    event_outcome = st.selectbox(label="Event Outcome",
                                                 options=["Successful", "Unsuccessful"])
                    event_outcome_label = event_outcome
                else:
                    event_outcome = event_outcome_type[0]
                    event_outcome_label = ""

            """ Minutes Filter """
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = team_data['Minute'].min()
                max_minute = team_data['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = team_data[team_data['Period'] == '1st Half']['Minute'].max()
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
                max_minute = team_data[team_data['Period'] == '2nd Half']['Minute'].max()
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
                final_team_df = team_data[(team_data['Outcome'] == event_outcome) &
                                          (team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == event_analysis)]
            else:
                final_team_df = team_data[(team_data['Period'] == game_time) &
                                          (team_data['Outcome'] == event_outcome) &
                                          (team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == event_analysis)]

            team_min_events = final_team_df[final_team_df['Team'] == team_name].shape[0]
            if analysis_team == "vs Opponents":
                opp_min_events = final_team_df[final_team_df['Opponent'] == team_name].shape[0]
            else:
                opp_min_events = final_team_df[final_team_df['Team'] == opp_name].shape[0]

            if team_min_events < 6 or opp_min_events < 6:
                plot_type = "Position"
            else:
                with menu_col:
                    plot_type = st.selectbox(label="Plot Type",
                                             options=['Heatmap', 'Position'])

            event_fig_team, event_fig_opp, event_insights, position_plot, direction_plot, \
                position_stats, direction_stats \
                = team_events_analysis(data=final_team_df,
                                       analysis_type=analysis_team,
                                       event_teams=[team_name,
                                                    opp_name],
                                       plot_type=plot_type,
                                       no_games=no_games,
                                       event_outcome=event_outcome_label,
                                       event_type=event_analysis)

            with plot_1:
                st.markdown(
                    f"<b><font color=#d20614>{team_name}</font></b> <b>{event_outcome}</b> <b><font color=#d20614>"
                    f"{event_analysis}</font></b> Events between Minute <b>{time_filter[0]}</b> and Minute <b>"
                    f"{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(event_fig_team)
            with plot_2:
                st.markdown(
                    f"<b><font color=#392864>{opp_label}</font></b> <b>{event_outcome}</b> <b><font color=#392864>"
                    f"{event_analysis}</font></b> Events between Minute <b>{time_filter[0]}</b> and Minute <b>"
                    f"{time_filter[1]}</b>", unsafe_allow_html=True)
                st.pyplot(event_fig_opp)

            with menu_col:
                st.table(data=event_insights.style.format(subset=['No Events'], formatter="{:.0f}").format(
                    subset=['Avg Events/G'], formatter="{:.2f}").apply(
                    lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                               for i in range(len(x))], axis=0).apply(
                    lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                               for i in range(len(x))], axis=0).set_table_styles(
                    [{'selector': 'th',
                      'props': [('background-color', '#d20614'),
                                ('color', '#ffffff')]}]))
                st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)
                st.subheader("")
                if season_name == "" and venue_name == "" and result_name == "":
                    st.markdown(f"<b>Season <font color=#d20614>2022-2023</font> Games Insights</b>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                    f"#d20614>{team_name}</font></b> had <b><font color=#d20614>{position_stats[1][0]:.2%}</font>"
                    f"</b> <b>{event_outcome_label}</b> <b>{event_analysis}</b> in <b>{position_stats[0][0]}"
                    f"</b> of the Pitch and <b><font color=#d20614>{direction_stats[1][0]:.2%}</font></b> in "
                    f" <b>{direction_stats[0][0]}</b> of the Pitch.", unsafe_allow_html=True)
                st.markdown(
                    f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b><font color="
                    f"#392864>{opp_label}</font></b> had <b><font color=#392864>{position_stats[1][1]:.2%}</font>"
                    f"</b> <b>{event_outcome_label}</b> <b>{event_analysis}</b> in <b>{position_stats[0][1]}"
                    f"</b> of the Pitch and <b><font color=#392864>{direction_stats[1][1]:.2%}</font></b> in "
                    f"<b>{direction_stats[0][1]}</b> of the Pitch.", unsafe_allow_html=True)

            if position_plot is not None:
                with st.expander("Display Position and Direction Plots"):
                    legen_col, pos_col, _, dir_col, _ = st.columns([2, 5, 0.5, 5, 0.5])
                    with legen_col:
                        st.subheader("")
                        st.header("")
                        st.subheader("")
                        st.markdown(f"<h4>Legend</h4>", unsafe_allow_html=True)
                        st.markdown(f"<b><font color=#d20614>{team_name}</font></b>", unsafe_allow_html=True)
                        st.markdown(f"<b><font color=#392864>{opp_label}</font></b>", unsafe_allow_html=True)
                    with pos_col:
                        st.plotly_chart(position_plot, config=config, use_container_width=True)
                    with dir_col:
                        st.plotly_chart(direction_plot, config=config, use_container_width=True)

        """ Passing Network Page """
    elif analysis_option == "Passing Network":
        page_container = st.empty()
        with page_container.container():

            """ Minutes Filter """
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = team_data['Minute'].min()
                max_minute = team_data['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = team_data[team_data['Period'] == '1st Half']['Minute'].max()
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
                max_minute = team_data[team_data['Period'] == '2nd Half']['Minute'].max()
                if time_option == "Entire Period":
                    time_filter = [45, max_minute]
                elif time_option == "46-60":
                    time_filter = [45, 60]
                elif time_option == "61-75":
                    time_filter = [61, 75]
                elif time_option == "76-90+":
                    time_filter = [76, max_minute]

            st.sidebar.header(" ")

            analysis_col, _, plot_col, legend_col, _ = st.columns([4, 0.25, 8, 2, 0.1])
            """ Final Data """
            if game_time == "Entire Game":
                final_pass_df = team_data[(team_data['Team'] == team_name) &
                                          (team_data['Outcome'] == 'Successful') &
                                          (team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == "Passes")]
            else:
                final_pass_df = team_data[(team_data['Team'] == team_name) &
                                          (team_data['Period'] == game_time) &
                                          (team_data['Outcome'] == 'Successful') &
                                          (team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == "Passes")]

            final_players_df = player_data[players_data['Match Day'].isin(match_days_filter)].reset_index(drop=True)
            network_players = \
                final_players_df.groupby(
                    ['Player Name', 'Jersey No'])['Minutes Played'].sum().nlargest(11).reset_index()

            network_plot, top_plot, starting_insights, top_insights = \
                team_passing_network(data=final_pass_df,
                                     network_players=network_players)

            with plot_col:
                st.markdown(
                    f"<b><font color=#d20614>{team_name}</font></b> <b>Passing Network</b> between Minute <b>"
                    f"{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> for the <b><font color=#d20614>11</font>"
                    f"</b> Players with most minutes played", unsafe_allow_html=True)
                st.pyplot(fig=network_plot)

            with legend_col:
                st.markdown(f"<h4>Players</h4>", unsafe_allow_html=True)
                for i in range(len(network_players)):
                    jersey_no = network_players.loc[i, 'Jersey No']
                    player_name = network_players.loc[i, 'Player Name']
                    if jersey_no < 10:
                        st.markdown(f"<b>0{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{jersey_no}<b> - <font color=#d20614>{player_name}</font>",
                                    unsafe_allow_html=True)
                st.markdown(f"-> <b>Attack</b></font> Direction", unsafe_allow_html=True)

            with analysis_col:
                if top_plot is None:
                    st.markdown("")
                    st.markdown(f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the "
                                f"Starting 11 Players of <b>{team_name}</b>, there were <b><font color=#d20614>0</font>"
                                f"</b> Successful Passes.", unsafe_allow_html=True)
                else:
                    st.plotly_chart(top_plot, config=config, use_container_width=True)
                    if season_name == "" and venue_name == "" and result_name == "":
                        st.markdown(f"<b>Season <font color=#d20614>2022-2023</font> Games Insights</b>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                    unsafe_allow_html=True)
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the Starting "
                        f"11 Players of <b>{team_name}</b>, <b><font color=#d20614>{starting_insights[0]}</font></b>"
                        f" was involved in most of the <b>Passes</b> with <b><font color=#d20614>"
                        f"{int(starting_insights[1])}</font></b>.", unsafe_allow_html=True)
                    st.markdown(
                        f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b> from the Top "
                        f"<b>{top_insights[0]}</b> Successful Passes between Players of <b>{team_name}</b>, we see that"
                        f" <b><font color=#d20614>{top_insights[1]}</font></b> was involved in most of them with <b>"
                        f"<font color=#d20614>{int(top_insights[2])}</font></b> out of <b><font color=#d20614>"
                        f"{top_insights[0]}</font></b>  Successful Passes between Players.", unsafe_allow_html=True)

    elif analysis_option == "Passing Distance":
        page_container = st.empty()
        with page_container.container():

            """ Minutes Filter """
            st.sidebar.header("Time Filter")
            game_time = st.sidebar.selectbox(label="Game Phase",
                                             options=["Entire Game", "1st Half", "2nd Half"])

            if game_time == "Entire Game":
                min_minute = team_data['Minute'].min()
                max_minute = team_data['Minute'].max()

                time_filter = st.sidebar.select_slider(label="Select Period",
                                                       options=[i for i in range(min_minute, max_minute + 1)],
                                                       value=(min_minute, max_minute))
            elif game_time == "1st Half":
                time_option = st.sidebar.selectbox(label="Select Period",
                                                   options=["Entire Period", "1-15", '16-30', '31-45+'])
                max_minute = team_data[team_data['Period'] == '1st Half']['Minute'].max()
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
                max_minute = team_data[team_data['Period'] == '2nd Half']['Minute'].max()
                if time_option == "Entire Period":
                    time_filter = [45, max_minute]
                elif time_option == "46-60":
                    time_filter = [45, 60]
                elif time_option == "61-75":
                    time_filter = [61, 75]
                elif time_option == "76-90+":
                    time_filter = [76, max_minute]

            st.sidebar.header(" ")

            info_team, plot_team, _, info_opp, plot_opp, _ = st.columns([3, 3, 0.5, 3, 3, 1])

            """ Final Data """
            if game_time == "Entire Game":
                final_pass_df = team_data[(team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == "Passes")]
            else:
                final_pass_df = team_data[(team_data['Period'] == game_time) &
                                          (team_data['Minute'] >= time_filter[0]) &
                                          (team_data['Minute'] <= time_filter[1]) &
                                          (team_data['Event'] == "Passes")]

            team_data, opp_data = team_passing_direction(data=final_pass_df,
                                                         analysis_type=analysis_team,
                                                         passing_teams=[team_name,
                                                                        opp_name])
            if team_data[0] is not None:
                with info_team:
                    team_logo = Image.open(f'images/{team_name}.png')
                    st.image(team_logo, width=100)
                    st.table(data=team_data[0].style.format(subset=['% of Events'],
                                                            formatter="{:.2%}").apply(
                        lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                   for i in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                                   for i in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#d20614'),
                                    ('color', '#ffffff')]}]))

                with plot_team:
                    st.plotly_chart(team_data[1], config=config, use_container_width=True)
                    st.plotly_chart(team_data[2], config=config, use_container_width=True)

                with info_team:
                    st.markdown("<h4>Legend</h4>", unsafe_allow_html=True)
                    st.markdown(f"- <font color=#d20614><b>Successful</b></font> Passes", unsafe_allow_html=True)
                    st.markdown(f"- <font color=#392864><b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
                    st.markdown("")
                    if season_name == "" and venue_name == "" and result_name == "":
                        st.markdown(f"<b>Season <font color=#d20614>2022-2023</font> Games Insights</b>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                    unsafe_allow_html=True)

                    if team_data[3] is not None and team_data[4] is not None:
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                            f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{team_name}</b> "
                            f"where <b>{team_data[3][0]}</b> and <b>{team_data[3][1]}</b> while most of the "
                            f"<b><font color=#d20614>Unsuccessful Passes</font></b> of <b>{team_name}</b> where "
                            f"<b>{team_data[4][0]}</b> and <b>{team_data[4][1]}</b>.",
                            unsafe_allow_html=True)
                    elif team_data[3] is None and team_data[4] is not None:
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                            f"{team_name}</b> had <b>No</b> <b><font color=#d20614>Successful Passes</font></b> "
                            f"while most of the <b><font color=#d20614>Unsuccessful Passes</font></b> of <b>"
                            f"{team_name}</b> where <b>{team_data[4][0]}</b> and <b>{team_data[4][1]}"
                            f"</b>.", unsafe_allow_html=True)
                    elif team_data[3] is not None and team_data[4] is None:
                        st.markdown(
                            f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                            f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{team_name}</b> "
                            f"where <b>{team_data[3][0]}</b> and <b>{team_data[3][1]}</b> while there were "
                            f"<b>No</b> <b><font color=#d20614>Unsuccessful Passes</font></b>.",
                            unsafe_allow_html=True)
            else:
                with info_team:
                    st.markdown(
                        f"<h4>No <font color=#d20614>Pass</font> Events between Minute <font color=#d20614>"
                        f"{time_filter[0]}</font></b> and Minute <font color=#d20614>{time_filter[1]}</font></b>."
                        f"</h4>", unsafe_allow_html=True)

            if opp_label == "All Opponents":
                opp_image = "Bundesliga"
            else:
                opp_image = opp_label
            if opp_data[0] is not None:

                with info_opp:
                    opp_logo = Image.open(f'images/{opp_image}.png')
                    st.image(opp_logo, width=100)
                    st.table(data=opp_data[0].style.format(subset=['% of Events'],
                                                           formatter="{:.2%}").apply(
                        lambda x: ['background: #ffffff' if i % 2 == 0 else 'background: #e7e7e7'
                                   for i in range(len(x))], axis=0).apply(
                        lambda x: ['color: #1e1e1e' if i % 2 == 0 else 'color: #d20614'
                                   for i in range(len(x))], axis=0).set_table_styles(
                        [{'selector': 'th',
                          'props': [('background-color', '#d20614'),
                                    ('color', '#ffffff')]}]))

                    with plot_opp:
                        st.plotly_chart(opp_data[1], config=config, use_container_width=True)
                        st.plotly_chart(opp_data[2], config=config, use_container_width=True)

                    with info_opp:
                        st.markdown("<h4>Legend</h4>", unsafe_allow_html=True)
                        st.markdown(f"- <font color=#d20614><b>Successful</b></font> Passes", unsafe_allow_html=True)
                        st.markdown(f"- <font color=#392864><b>Unsuccessful</b></font> Passes", unsafe_allow_html=True)
                        st.markdown("")
                        if season_name == "" and venue_name == "" and result_name == "":
                            st.markdown(f"<b>Season <font color=#d20614>2022-2023</font> Games Insights</b>",
                                        unsafe_allow_html=True)
                        else:
                            st.markdown(f"<b>{season_name} {venue_name} {result_name} Games Insights</b>",
                                        unsafe_allow_html=True)
                        if opp_data[3] is not None and opp_data[4] is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                                f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{opp_label}</b> "
                                f"where <b>{opp_data[3][0]}</b> and <b>{opp_data[3][1]}</b> while most of the "
                                f"<b><font color=#d20614>Unsuccessful Passes</font></b> of <b>{opp_label}</b> where "
                                f"<b>{opp_data[4][0]}</b> and <b>{opp_data[4][1]}</b>.",
                                unsafe_allow_html=True)
                        elif opp_data[3] is None and opp_data[4] is not None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, <b>"
                                f"{opp_label}</b> had <b>No</b> <b><font color=#d20614>Successful Passes</font></b> "
                                f"while most of the <b><font color=#d20614>Unsuccessful Passes</font></b> of <b>"
                                f"{opp_label}</b> where <b>{opp_data[4][0]}</b> and <b>{opp_data[4][1]}"
                                f"</b>.", unsafe_allow_html=True)
                        elif opp_data[3] is not None and opp_data[4] is None:
                            st.markdown(
                                f"Between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>, most of "
                                f"the <b><font color=#d20614>Successful Passes</font></b> of <b>{opp_label}</b> "
                                f"where <b>{opp_data[3][0]}</b> and <b>{opp_data[3][1]}</b> while there were "
                                f"<b>No</b> <b><font color=#d20614>Unsuccessful Passes</font></b>.",
                                unsafe_allow_html=True)
            else:
                with info_opp:
                    st.markdown(f"<h4>No <font color=#d20614>Pass</font> Events between Minute <font color=#d20614>"
                                f"{time_filter[0]}</font></b> and Minute <font color=#d20614>{time_filter[1]}</font>"
                                f"</b>.</h4>", unsafe_allow_html=True)
    else:
        pass

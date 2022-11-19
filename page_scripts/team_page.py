import streamlit as st
from PIL import Image
from page_scripts.stats_scripts.team_stats import team_analysis

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


def team_events(data, players_data, analysis_option, analysis_team, team_name, opp_name):
    """ Page Configuration """
    config = {'displayModeBar': False}

    team_data = data.copy()
    player_data = players_data.copy()

    if analysis_team == "vs Opponents":
        name_col, team_col, _ = st.columns([8.25, 6, 1])
        with team_col:
            team_logo = Image.open(f'images/{team_name}.png')
            st.image(team_logo, width=100)
        no_games = [team_data[team_data['Team'] == team_name]['Match Day'].nunique(),
                    team_data[team_data['Team'] == team_name]['Match Day'].nunique()]
    else:
        name_col, team_col, opp_col, _ = st.columns([4.6, 5, 3, 0.5])
        with team_col:
            team_logo = Image.open(f'images/{team_name}.png')
            st.image(team_logo, width=100)
        with opp_col:
            opp_logo = Image.open(f'images/{opp_name}.png')
            st.image(opp_logo, width=100)
        no_games = [team_data[team_data['Team'] == team_name]['Match Day'].nunique(),
                    team_data[team_data['Team'] == opp_name]['Match Day'].nunique()]

    """ Page Label """
    if team_name == opp_name:
        opp_label = "All Opponents"
    else:
        opp_label = opp_name
    with name_col:
        st.markdown("")
        st.markdown(f"<h3>{team_name} <font color=#d20614>{analysis_option}</font> vs {opp_label}</h3>",
                    unsafe_allow_html=True)

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

    menu_col, _, plot_1, _, plot_2, _ = st.columns([3, 0.5, 6, 0.5, 6, 1])
    st.sidebar.header(" ")

    """ Game Events Page """
    if analysis_option == "Game Events":

        if game_time == "Entire Game":
            event_types = team_data[(team_data['Minute'] >= time_filter[0]) &
                                    (team_data['Minute'] <= time_filter[1])]['Event'].unique()
        else:
            event_types = team_data[(team_data['Period'] == game_time) &
                                    (team_data['Minute'] >= time_filter[0]) &
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

        team_min_events = final_team_df[final_team_df['Team'] == team_name].value_counts().min()
        if analysis_team == "vs Opponents":
            opp_min_events = final_team_df[final_team_df['Opponent'] == team_name].value_counts().min()
        else:
            opp_min_events = final_team_df[final_team_df['Team'] == opp_name].value_counts().min()

        if team_min_events < 6 and opp_min_events < 6:
            plot_type = "Position"
        else:
            with menu_col:
                plot_type = st.selectbox(label="Plot Type",
                                         options=['Heatmap', 'Position'])

        event_fig_team, event_fig_opp, event_insights, position_plot, direction_plot, position_stats, direction_stats \
            = team_analysis(data=final_team_df,
                            analysis_type=analysis_team,
                            event_teams=[team_name,
                                         opp_name],
                            plot_type=plot_type,
                            no_games=no_games,
                            event_outcome=event_outcome_label,
                            event_type=event_analysis)

        with plot_1:
            st.markdown(f"{team_name} <b>{event_outcome}</b> <b><font color=#d20614>{event_analysis}</font></b> Events"
                        f" between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>",
                        unsafe_allow_html=True)
            st.pyplot(event_fig_team)
        with plot_2:
            st.markdown(f"{opp_label} <b>{event_outcome}</b> <b><font color=#d20614>{event_analysis}</font></b> Events"
                        f" between Minute <b>{time_filter[0]}</b> and Minute <b>{time_filter[1]}</b>",
                        unsafe_allow_html=True)
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

            st.subheader("")
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
        pass
    elif analysis_option == "Passing Direction":
        pass

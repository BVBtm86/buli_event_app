import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from page_scripts.stats_scripts.game_stats import game_staring_11, game_analysis


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
        _, plot_col, _ = st.columns([2, 10, 2])

        starting_11_plot = game_staring_11(data=data_players,
                                           game_teams=[home_team,
                                                       away_team])

        with plot_col:
            st.pyplot(fig=starting_11_plot)

    elif game_event_analysis == "Game Events":

        """ Minutes Filter """
        st.sidebar.title("Event Options")
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
    elif game_event_analysis == "Passing Network":
        pass
    elif game_event_analysis == "Passing Direction":
        pass
    else:
        pass

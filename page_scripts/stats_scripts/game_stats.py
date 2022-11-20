import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from matplotlib.colors import to_rgba
from mplsoccer import Pitch
import math
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})

team_colors = ["#d20614", "#392864"]

original_event_name = ['Passes', 'Goals', 'Shots Saved', 'Shots Missed', 'Shots On Post', 'Penalties', 'Ball Touches',
                       'Dribbles', 'Corner Awarded', 'Ball Recoveries', 'Interceptions', 'Aerial Duels', 'Tackles',
                       'Dispossessions', 'Clearances', 'Challenges', 'Blocked Passes', 'Fouls', 'Offsides', 'Errors',
                       'Keeper Saves', 'Keeper Claims', 'Keeper Punches', 'Keeper Pickups', 'Keeper Sweeper']

sequence_event_name = ['Unsuccessful Pass', 'Goal', 'Shot Saved', 'Shot Missed', 'Shot On Post', 'Penalty',
                       'Unsuccessful Ball Touch', 'Unsuccessful Dribble', 'Corner Awarded', 'Ball Recovery',
                       'Interception', 'Unsuccessful Aerial Duel', 'Tackled', 'Dispossessed', 'Clearance',
                       'Challenged', 'Blocked Pass', 'Fouled', 'Offside', 'Error', 'Keeper Save',
                       'Keeper Claim', 'Keeper Punch', 'Keeper Pickup', 'Keeper Sweep']


def calculate_distance(x_start, y_start, x_end, y_end):
    pass_distance = math.sqrt((x_end * 1.05 - x_start * 1.05) ** 2 + (y_end * 0.68 - y_start * 0.68) ** 2)
    return pass_distance


@st.cache(show_spinner=False)
def empty_pitch():
    """ Create Pitch """
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    return pitch_fig


def game_staring_11(data, game_teams):
    """ Create Starting 11 Df """
    df_starting_11 = data.copy()

    """ Plot Events """
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(10, 10))
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    df_starting_11['Team'] = pd.Categorical(df_starting_11['Team'], game_teams)
    df_starting_11 = df_starting_11.sort_values(by='Team')
    ax = sns.scatterplot(data=df_starting_11,
                         x="X",
                         y="Y",
                         s=250,
                         hue='Team',
                         palette={game_teams[0]: team_colors[0],
                                  game_teams[1]: team_colors[1]},
                         alpha=0.75,
                         legend=False)

    text_plot = pd.concat({'x': df_starting_11['X'],
                           'y': df_starting_11['Y'],
                           'no': df_starting_11['Jersey No']}, axis=1)
    for i, point in text_plot.iterrows():
        ax.text(x=point['x'],
                y=point['y'] - 1,
                s=str(point['no'].astype(int)),
                ha='center',
                color="#ffffff",
                font={'weight': 'bold',
                      'size': 10})

    return pitch_fig


def game_analysis(data, data_period, game_teams, plot_type, event_type, event_outcome, heat_team, no_events):
    """ Create Event Df """
    event_df = data.copy()
    period_df = data_period.copy()
    if plot_type == "Heatmap":
        final_df = event_df[event_df['Team'] == heat_team].reset_index(drop=True)
    else:
        final_df = event_df.copy()

    """ Plot Events """
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(10, 10))
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    if plot_type == "Position":
        sns.scatterplot(data=final_df,
                        x="Start X",
                        y="Start Y",
                        s=75,
                        hue='Team',
                        palette={game_teams[0]: team_colors[0],
                                 game_teams[1]: team_colors[1]},
                        alpha=0.75,
                        legend=False)
        plot_heatmap = True
    else:
        if final_df.shape[0] >= 5:
            sns.kdeplot(x=final_df['Start X'],
                        y=final_df['Start Y'],
                        shade=True,
                        shade_lowest=False,
                        alpha=0.25,
                        n_levels=10,
                        cmap='plasma')
            plot_heatmap = True
        else:
            plot_heatmap = False

    """ Analysis Data """
    home_stats = event_df[event_df['Venue'] == 'Home'].reset_index(drop=True)
    away_stats = event_df[event_df['Venue'] == 'Away'].reset_index(drop=True)

    """ Analysis by Field Position """
    home_stats['Position'] = home_stats['Start X'].apply(lambda x: 'Def Third' if x < 34 else (
        'Mid Third' if 34 <= x < 68 else 'Att Third'))
    away_stats['Position'] = away_stats['Start X'].apply(lambda x: 'Att Third' if x < 34 else (
        'Mid Third' if 34 <= x < 68 else 'Def Third'))

    """ Analysis by Direction """
    home_stats['Direction'] = home_stats['Start Y'].apply(lambda x: 'Right Side' if x < 30 else (
        'Mid Side' if 30 <= x < 70 else 'Left Side'))
    away_stats['Direction'] = away_stats['Start Y'].apply(lambda x: 'Left Side' if x < 30 else (
        'Mid Side' if 30 <= x < 70 else 'Right Side'))

    """ Analysis Plots """
    analysis_events = pd.concat([home_stats, away_stats], axis=0)
    position_stats = pd.DataFrame(analysis_events.groupby('Team')['Position'].value_counts(normalize=True))
    position_stats.columns = ['%']
    position_stats.reset_index(inplace=True)
    position_stats['Team'] = pd.Categorical(position_stats['Team'], game_teams)
    position_stats['Position'] = pd.Categorical(position_stats['Position'], ['Def Third', 'Mid Third', 'Att Third'])
    position_stats = position_stats.sort_values(by=['Team', 'Position'])

    direction_stats = pd.DataFrame(analysis_events.groupby('Team')['Direction'].value_counts(normalize=True))
    direction_stats.columns = ['%']
    direction_stats.reset_index(inplace=True)
    direction_stats['Team'] = pd.Categorical(direction_stats['Team'], game_teams)
    direction_stats['Direction'] = pd.Categorical(direction_stats['Direction'], ['Right Side', 'Mid Side', 'Left Side'])
    direction_stats = direction_stats.sort_values(by=['Team', 'Direction'])

    position_fig = px.bar(position_stats,
                          x='Position',
                          y='%',
                          color='Team',
                          color_discrete_map={game_teams[0]: team_colors[0],
                                              game_teams[1]: team_colors[1]},
                          height=350,
                          barmode='group',
                          title=f"{event_outcome} <b>{event_type}</b> by Pitch Position",
                          hover_data={'%': ':.2%'})
    position_fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)"},
        showlegend=False)
    position_fig.layout.yaxis.tickformat = ',.0%'

    direction_fig = px.bar(direction_stats,
                           x='Direction',
                           y='%',
                           color='Team',
                           color_discrete_map={game_teams[0]: team_colors[0],
                                               game_teams[1]: team_colors[1]},
                           height=350,
                           barmode='group',
                           title=f"{event_outcome} <b>{event_type}</b> by Pitch Direction",
                           hover_data={'%': ':.2%'})
    direction_fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)"},
        showlegend=False)
    direction_fig.layout.yaxis.tickformat = ',.0%'

    """ No Events Plots """
    no_home_type = home_stats.shape[0]
    no_away_type = away_stats.shape[0]
    events_tab = [game_teams,
                  [no_home_type, no_away_type],
                  [no_home_type / no_events[0], no_away_type / no_events[1]]]
    events_df = pd.DataFrame(events_tab).T
    events_df.columns = ['Team', 'No of Events', '% of Total Events']
    events_df.set_index('Team', inplace=True)

    """ Analysis Insights """
    if home_stats.shape[0]:
        home_position_name = f"the {home_stats['Position'].value_counts(normalize=True).index[0]}"
        home_position_count = home_stats['Position'].value_counts(normalize=True).values[0]
        home_direction_name = f"the {home_stats['Direction'].value_counts(normalize=True).index[0]}"
        home_direction_count = home_stats['Direction'].value_counts(normalize=True).values[0]
    else:
        home_position_name = "Any Position"
        home_position_count = 0
        home_direction_name = "Any Direction"
        home_direction_count = 0
    if away_stats.shape[0]:
        away_position_name = f"the {away_stats['Position'].value_counts(normalize=True).index[0]}"
        away_position_count = away_stats['Position'].value_counts(normalize=True).values[0]
        away_direction_name = f"the {away_stats['Direction'].value_counts(normalize=True).index[0]}"
        away_direction_count = away_stats['Direction'].value_counts(normalize=True).values[0]
    else:
        away_position_name = "Any Position"
        away_position_count = 0
        away_direction_name = "Any Direction"
        away_direction_count = 0

    home_period = period_df[period_df['Venue'] == 'Home'].reset_index(drop=True)
    away_period = period_df[period_df['Venue'] == 'Away'].reset_index(drop=True)
    if home_period.shape[0]:
        home_period_name = home_period['Period'].value_counts(normalize=True).index[0]
        home_period_count = home_period['Period'].value_counts(normalize=True).values[0]
    else:
        home_period_name = "Any Period"
        home_period_count = 0
    if away_period.shape[0]:
        away_period_name = away_period['Period'].value_counts(normalize=True).index[0]
        away_period_count = away_period['Period'].value_counts(normalize=True).values[0]
    else:
        away_period_name = "Any Period"
        away_period_count = 0

    position_insight = [[home_position_name, away_position_name], [home_position_count, away_position_count]]
    direction_insight = [[home_direction_name, away_direction_name], [home_direction_count, away_direction_count]]
    period_insight = [[home_period_name, away_period_name], [home_period_count, away_period_count]]

    return pitch_fig, position_fig, direction_fig, events_df, plot_heatmap, \
        position_insight, direction_insight, period_insight


def game_passing_network(data, starting_players, plot_team):
    """ Create Pass Df """
    pass_df = data.copy()
    pass_df = pass_df[pass_df['Team'] == plot_team].reset_index(drop=True)
    pass_df = pass_df[pass_df['Player Name'] != pass_df['Player Name Receiver']].reset_index(drop=True)

    starting_df = starting_players.copy()
    starting_df = starting_df[starting_df['Team'] == plot_team].reset_index(drop=True)

    pass_df['Keep Player'] = \
        pass_df['Player Name'].isin(list(starting_df['Player Name'].values)) * 1 + \
        pass_df['Player Name Receiver'].isin(list(starting_df['Player Name'].values)) * 1
    pass_df = pass_df[pass_df['Keep Player'] == 2].reset_index(drop=True)

    """ Create Network Data """
    pass_df['Pass Pair'] = pass_df['Player Name'] + " - " + pass_df['Player Name Receiver']
    network_df = pass_df.groupby(['Pass Pair'])['Event'].count().reset_index()
    network_df['Player Name'] = network_df['Pass Pair'].apply(lambda x: x.split(" - ")[0])
    network_df['Player Name Receiver'] = network_df['Pass Pair'].apply(lambda x: x.split(" - ")[1])

    avg_df = pass_df.groupby(['Player Name'])[['Start X', 'Start Y']].agg(
        {'Start X': ['mean'], 'Start Y': ['mean', 'count']}).reset_index()
    avg_df.columns = ['Player Name', 'Start X', 'Start Y', 'No Passes']

    network_df = pd.merge(left=network_df,
                          right=avg_df.drop(columns=['No Passes']),
                          left_on=['Player Name'],
                          right_on=['Player Name'],
                          how='left')
    network_df = pd.merge(left=network_df,
                          right=avg_df.rename(columns={'Player Name': 'Player Name Receiver'}).drop(
                              columns=['No Passes']),
                          left_on=['Player Name Receiver'],
                          right_on=['Player Name Receiver'],
                          how='left')
    network_df.iloc[:, -4:] = np.round(network_df.iloc[:, -4:], 2)
    network_df.rename(columns={'Start X_x': 'Start X', 'Start Y_x': 'Start Y',
                               'Start X_y': 'End X', 'Start Y_y': 'End Y'}, inplace=True)

    avg_df = pd.merge(left=avg_df,
                      right=starting_df[['Player Name', 'Jersey No']],
                      left_on=['Player Name'],
                      right_on=['Player Name'],
                      how='left')

    """ Plot Network Data """
    max_line_width = 10
    max_marker_size = 2000
    network_df['Pass Width'] = (network_df['Event'] / network_df['Event'].max() * max_line_width)
    avg_df['Size'] = (avg_df['No Passes'] / avg_df['No Passes'].max() * max_marker_size)

    min_transparency = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(network_df), 1))
    c_transparency = network_df['Event'] / network_df['Event'].max()
    c_transparency = (c_transparency * (1 - min_transparency)) + min_transparency
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    if pass_df.shape[0] > 1:
        pitch.lines(network_df['Start X'], network_df['Start Y'],
                    network_df['End X'], network_df['End Y'],
                    lw=network_df['Pass Width'],
                    color=color,
                    zorder=1,
                    ax=pitch_ax)
        pitch.scatter(avg_df['Start X'], avg_df['Start Y'],
                      s=avg_df['Size'],
                      color='#d20614',
                      edgecolors='black',
                      linewidth=1,
                      alpha=0.5,
                      ax=pitch_ax)
        for index, row in avg_df.iterrows():
            pitch.annotate(row['Jersey No'], xy=(row['Start X'], row['Start Y']), c='#ffffff', va='center',
                           ha='center', size=16, weight='bold', ax=pitch_ax)

    """ Analysis Network Data """
    top_passes_df = network_df.nlargest(10, 'Event')
    top_passes_df = pd.merge(left=top_passes_df,
                             right=starting_df[['Player Name', 'Jersey No']],
                             left_on=['Player Name'],
                             right_on=['Player Name'],
                             how='left')
    top_passes_df = pd.merge(left=top_passes_df,
                             right=starting_df.rename(
                                 columns={
                                     'Player Name': 'Player Name Receiver'})[['Player Name Receiver', 'Jersey No']],
                             left_on=['Player Name Receiver'],
                             right_on=['Player Name Receiver'],
                             how='left')
    top_passes_df['Player Combo'] = \
        top_passes_df['Jersey No_x'].astype(str) + " - " + top_passes_df['Jersey No_y'].astype(str)

    top_passes_df = top_passes_df.sort_values(by='Event', ascending=True)
    top_passes_df.rename(columns={"Event": "No of Passes"}, inplace=True)
    if pass_df.shape[0] > 1:
        top_fig = px.bar(top_passes_df,
                         x='No of Passes',
                         y='Player Combo',
                         height=600,
                         title=f"Top {top_passes_df.shape[0]} <b>Successful Passes</b> between Players")
        top_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)

        top_fig.update_traces(marker_color='#d20614')
    else:
        top_fig = None

    """ Network Insights """
    if pass_df.shape[0] > 1:
        top_player_df = \
            pd.DataFrame(top_passes_df.groupby('Player Name')['Player Name'].count() +
                         top_passes_df.groupby('Player Name Receiver')['Player Name Receiver'].count(), columns=["No"])
        top_most = \
            [top_passes_df.shape[0],
             top_player_df.nlargest(1, 'No').index.values[0],
             top_player_df.nlargest(1, 'No')['No'].values[0]]

        all_most_df = \
            pd.DataFrame(network_df.groupby('Player Name')['Event'].sum() +
                         network_df.groupby('Player Name Receiver')['Event'].sum())
        all_most = \
            [all_most_df.nlargest(1, 'Event').index.values[0],
             all_most_df.nlargest(1, 'Event')['Event'].values[0]]
    else:
        all_most = [None, None]
        top_most = [None, None, None]

    return pitch_fig, top_fig, all_most, top_most


def game_passing_direction(data, plot_team, pass_length):
    """ Create Pass Df """
    pass_df = data.copy()
    pass_df = pass_df[pass_df['Team'] == plot_team].reset_index(drop=True)
    if pass_df.shape[0] > 0:
        pass_df['Distance'] = \
            pass_df.apply(lambda x: calculate_distance(x['Start X'], x['Start Y'], x['End X'], x['End Y']), axis=1)
        pass_df['Distance Length'] = pass_df['Distance'].apply(lambda x: 'Short Passes' if x <= 10 else (
            'Medium Passes' if 10 < x <= 25 else 'Long Passes'))
        pass_df['Direction'] = pass_df['End X'] - pass_df['Start X']
        pass_df['Direction Type'] = \
            pass_df['Direction'].apply(lambda x: "Forward Passes" if x > 0 else "Backward Passes")

    if pass_length != "All":
        pass_successful = pass_df[(pass_df['Outcome'] == "Successful") &
                                  (pass_df['Distance Length'] == pass_length)].reset_index(drop=True)
        pass_unsuccessful = pass_df[(pass_df['Outcome'] == "Unsuccessful") &
                                    (pass_df['Distance Length'] == pass_length)].reset_index(drop=True)
    else:
        pass_successful = pass_df[(pass_df['Outcome'] == "Successful")].reset_index(drop=True)
        pass_unsuccessful = pass_df[(pass_df['Outcome'] == "Unsuccessful")].reset_index(drop=True)

    """ Plot Passing Data """
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    """ Plot the Successful Passes """
    pitch.arrows(pass_successful['Start X'], pass_successful['Start Y'],
                 pass_successful['End X'], pass_successful['End Y'],
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#d20614',
                 alpha=0.75,
                 ax=pitch_ax)

    """ Plot the Unsuccessful Passes """
    pitch.arrows(pass_unsuccessful['Start X'], pass_unsuccessful['Start Y'],
                 pass_unsuccessful['End X'], pass_unsuccessful['End Y'],
                 width=1,
                 headwidth=5,
                 headlength=5,
                 color='#392864',
                 alpha=0.75,
                 ax=pitch_ax)

    """ Direction Insights """
    if pass_df.shape[0] > 0:
        pass_outcome_count = pd.DataFrame(pass_df['Outcome'].value_counts())
        pass_outcome_perc = pd.DataFrame(pass_df['Outcome'].value_counts(normalize=True))
        pass_outcome = pd.concat([pass_outcome_count, pass_outcome_perc], axis=1)
        pass_outcome.columns = ['No of Events', '% of Events']

        pass_length = pd.DataFrame(pass_df.groupby("Outcome")['Distance Length'].value_counts(normalize=True))
        pass_length.columns = ['%']
        pass_length.reset_index(inplace=True)
        pass_direction = pd.DataFrame(pass_df.groupby("Outcome")['Direction Type'].value_counts(normalize=True))
        pass_direction.columns = ['%']
        pass_direction.reset_index(inplace=True)

        """ Length Plot """
        length_fig = px.bar(pass_length,
                            x='Distance Length',
                            y='%',
                            color='Outcome',
                            color_discrete_map={"Successful": team_colors[0],
                                                "Unsuccessful": team_colors[1]},
                            height=350,
                            barmode='group',
                            title=f"Length of Passes by Outcome",
                            hover_data={'%': ':.2%'})
        length_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        length_fig.layout.yaxis.tickformat = ',.0%'

        """ Direction Plot """
        direction_fig = px.bar(pass_direction,
                               x='Direction Type',
                               y='%',
                               color='Outcome',
                               color_discrete_map={"Successful": team_colors[0],
                                                   "Unsuccessful": team_colors[1]},
                               height=350,
                               barmode='group',
                               title=f"Direction of Passes by Outcome",
                               hover_data={'%': ':.2%'})
        direction_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        direction_fig.layout.yaxis.tickformat = ',.0%'

        if 'Successful' in pass_outcome.index:
            successful_insight = [pass_length[pass_length['Outcome'] == "Successful"]['Distance Length'].values[0],
                                  pass_direction[pass_direction['Outcome'] == "Successful"]['Direction Type'].values[0]]
        else:
            successful_insight = None
        if 'Unsuccessful' in pass_outcome.index:
            unsuccessful_insight = [pass_length[pass_length['Outcome'] == "Unsuccessful"]['Distance Length'].values[0],
                                    pass_direction[pass_direction['Outcome'] == "Unsuccessful"][
                                        'Direction Type'].values[0]]
        else:
            unsuccessful_insight = None
    else:
        pass_outcome = None
        length_fig = None
        direction_fig = None
        successful_insight = None
        unsuccessful_insight = None

    return pitch_fig, pass_outcome, length_fig, direction_fig, successful_insight, unsuccessful_insight


@st.cache
def pass_sequence_creation(data, sequence_team):
    """ Create Pass Sequence Df """
    final_pass_df = data.copy()
    final_pass_df = final_pass_df.sort_values(by=["Final Minute", "Second"]).reset_index(drop=True)

    """ Create Sequence """
    period_index = final_pass_df[final_pass_df['Period'] == '2nd Half'].index[0]
    team_pos = final_pass_df.columns.get_loc("Team")
    event_pos = final_pass_df.columns.get_loc("Event")
    outcome_pos = final_pass_df.columns.get_loc("Outcome")
    sequence_passes = []
    sequence_passes_end = []
    sequence_pass_count = 0
    current_seq = "Successful"
    for i in range(final_pass_df.shape[0]):
        current_team_name = final_pass_df.iloc[i, team_pos]
        event_name = final_pass_df.iloc[i, event_pos]
        outcome_name = final_pass_df.iloc[i, outcome_pos]
        if i == 0:
            if event_name == "Passes" and outcome_name == "Successful":
                sequence_pass_count += 1
                sequence_passes.append(sequence_pass_count)
                current_seq = "Successful"
        elif i == period_index:
            if event_name == "Passes" and outcome_name == "Successful":
                sequence_pass_count += 1
                sequence_passes.append(sequence_pass_count)
                current_seq = "Successful"
        else:
            previous_team_name = final_pass_df.iloc[i - 1, team_pos]
            if current_team_name == previous_team_name and event_name == "Passes" and outcome_name == "Successful":
                if current_seq == "Unsuccessful":
                    sequence_pass_count += 1
                sequence_passes.append(sequence_pass_count)
                current_seq = "Successful"
            else:
                sequence_pass_count += 1
                sequence_passes.append(sequence_pass_count)
                if event_name == "Passes" and outcome_name == "Successful":
                    current_seq = "Successful"
                else:
                    current_seq = "Unsuccessful"
        if event_name == "Passes" and outcome_name == "Successful":
            if i == period_index - 1:
                sequence_passes_end.append(event_name)
            else:
                sequence_passes_end.append(None)
        else:
            sequence_passes_end.append(event_name)

    final_pass_df['Sequence No'] = sequence_passes
    final_pass_df['Sequence End'] = sequence_passes_end
    final_pass_df['Sequence End'].fillna(method='bfill', inplace=True)
    final_pass_df = final_pass_df[
        (final_pass_df['Event'] == "Passes") & (final_pass_df['Outcome'] == "Successful")].reset_index(drop=True)
    final_pass_df['Sequence End'] = final_pass_df['Sequence End'].map(dict(zip(original_event_name,
                                                                               sequence_event_name)))

    sequence_team_df = final_pass_df[final_pass_df['Team'] == sequence_team].reset_index(drop=True)

    """ Sequence Stats """
    no_sequences = sequence_team_df['Sequence No'].nunique()
    avg_sequence = sequence_team_df.groupby(['Sequence No'])['Id'].count().mean()
    total_sequence_stats = pd.DataFrame([no_sequences, avg_sequence], index=("Total Seq Passes", "Total Avg Passes"),
                                        columns=['#'])
    return sequence_team_df, total_sequence_stats


def pass_sequence_df(data, team_sequence, close_sequence, no_sequence, players_info):
    """ Create Sequence Df """
    sequence_df = data.copy()
    event_df = sequence_df[sequence_df['Sequence End'] == close_sequence].reset_index(drop=True)

    """ New Order Sequence """
    no_event = 1
    new_order = [1]
    for i in range(1, event_df.shape[0]):
        if event_df.iloc[i, -2] == event_df.iloc[i - 1, -2]:
            new_order.append(no_event)
        else:
            no_event = no_event + 1
            new_order.append(no_event)

    event_df['Sequence No'] = new_order
    pass_df = event_df[event_df['Sequence No'] == no_sequence].reset_index(drop=True)

    start_x_loc = pass_df.columns.get_loc("Start X")
    start_y_loc = pass_df.columns.get_loc("Start Y")
    end_x_loc = pass_df.columns.get_loc("End X")
    end_y_loc = pass_df.columns.get_loc("End Y")

    for i in range(1, len(pass_df))[::-1]:
        pass_df.iloc[i - 1, end_x_loc] = pass_df.iloc[i, start_x_loc]
        pass_df.iloc[i - 1, end_y_loc] = pass_df.iloc[i, start_y_loc]

    """ Create Final Data """
    player_name_loc = pass_df.columns.get_loc("Player Name Receiver")
    event_id = list(pass_df['Id'].values)
    start_x = list(pass_df['Start X'].values)
    start_y = list(pass_df['Start Y'].values)
    end_x = list(pass_df['End X'].values)
    end_y = list(pass_df['End Y'].values)
    player_name = list(pass_df['Player Name'].values)
    game_minute = list(pass_df['Minute'].values)
    event_id.append(event_id[-1] + 1)
    start_x.append(end_x[-1])
    start_y.append(end_y[-1])
    game_minute.append(game_minute[-1])
    player_name.append(pass_df.iloc[-1, player_name_loc])
    if close_sequence in ['Goal', 'Shot Saved', 'Shot Missed', 'Shot On Post', 'Penalty']:
        if team_sequence == "Home":
            end_x.append(100)
            end_y.append(50)
        else:
            end_x.append(0)
            end_y.append(50)

    final_sequence_df = pd.DataFrame([event_id, game_minute, player_name, start_x, start_y, end_x, end_y]).T
    final_sequence_df.columns = ["Id", "Minute", "Player Name", "Start X", "Start Y", "End X", "End Y"]
    for col in ["Id", "Minute", "Start X", "Start Y", "End X", "End Y"]:
        final_sequence_df[col] = final_sequence_df[col].astype(float)

    player_names_unique = pd.DataFrame(final_sequence_df['Player Name'].unique(), columns=['Player Name'])
    player_legend_df = pd.merge(left=player_names_unique,
                                right=players_info[['Player Name', 'Jersey No']],
                                left_on="Player Name",
                                right_on="Player Name",
                                how="left")

    """ Sequence Stats """
    no_sequences = event_df['Sequence No'].nunique()
    avg_sequence = event_df.groupby(['Sequence No'])['Id'].count().mean()
    event_sequence_stats = pd.DataFrame([no_sequences, avg_sequence], index=("Event Seq Passes", "Event Avg Passes"),
                                        columns=['#'])

    return final_sequence_df, player_legend_df, event_sequence_stats


def game_pass_sequence(data, players_info, event_no):
    """ Create Final Df """
    pass_df = data.copy()
    players_df = players_info.copy()
    pass_df = pass_df.iloc[:event_no, :].copy()

    pass_df = pd.merge(left=pass_df,
                       right=players_df[['Player Name', 'Jersey No']],
                       left_on=['Player Name'],
                       right_on=['Player Name'],
                       how='left')

    """ Create Passing Plot """
    current_game_minute = pass_df['Minute'].max()
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    pitch.arrows(0, 102,
                 15, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(100, 102,
                 85, 102,
                 width=2,
                 headwidth=5,
                 headlength=5,
                 color='#ffffff',
                 alpha=1,
                 ax=pitch_ax)

    pitch.arrows(pass_df['Start X'], pass_df['Start Y'],
                 pass_df['End X'], pass_df['End Y'],
                 width=3,
                 headwidth=5,
                 headlength=5,
                 color='#d20614',
                 alpha=0.5,
                 ax=pitch_ax)

    pitch.scatter(pass_df['Start X'], pass_df['Start Y'],
                  s=1000,
                  color='#d20614',
                  edgecolors='black',
                  linewidth=1,
                  alpha=0.5,
                  ax=pitch_ax)

    for index, row in pass_df.iterrows():
        pitch.annotate(row['Jersey No'], xy=(row['Start X'], row['Start Y']), c='#ffffff', va='center',
                       ha='center', size=16, weight='bold', ax=pitch_ax)

    return pitch_fig, current_game_minute

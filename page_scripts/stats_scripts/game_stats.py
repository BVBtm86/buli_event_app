import pandas as pd
import numpy as np
from mplsoccer import Pitch
import seaborn as sns
import plotly.express as px
from matplotlib.colors import to_rgba


def game_staring_11(data, game_teams):
    """ Create Starting 11 Df """
    df_starting_11 = data.copy()

    """ Plot Events """
    team_colors = ["#d20614", "#392864"]
    sns.set_palette(sns.color_palette(team_colors))
    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(10, 10))

    df_starting_11['Team'] = pd.Categorical(df_starting_11['Team'], game_teams)
    df_starting_11 = df_starting_11.sort_values(by='Team')
    ax = sns.scatterplot(data=df_starting_11,
                         x="X",
                         y="Y",
                         s=500,
                         hue='Team',
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


def game_analysis(data, data_period, game_teams, plot_type, event_outcome, event_type, heat_team, no_events):
    """ Create Event Df """
    event_df = data.copy()
    period_df = data_period.copy()

    """ Plot Events """
    team_colors = ["#d20614", "#392864"]
    sns.set_palette(sns.color_palette(team_colors))

    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.draw(figsize=(10, 10))
    event_df = event_df.sort_values(by=['Venue'], ascending=False)
    if plot_type == "Position":
        sns.scatterplot(data=event_df,
                        x="Start X",
                        y="Start Y",
                        s=75,
                        hue='Team',
                        alpha=0.75,
                        legend=False)
        plot_heatmap = True
    else:
        heat_df = event_df.copy()
        heat_df = heat_df[heat_df['Team'] == heat_team].reset_index(drop=True)
        if heat_df.shape[0] >= 5:
            if heat_df.shape[0] < 10:
                level_plot = heat_df.shape[0]
            else:
                level_plot = 10
            sns.kdeplot(x=heat_df['Start X'],
                        y=heat_df['Start Y'],
                        shade=True,
                        shade_lowest=False,
                        alpha=0.25,
                        n_levels=level_plot,
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
                          height=450,
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
                           height=450,
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
        away_position_name = f"{away_stats['Position'].value_counts(normalize=True).index[0]}"
        away_position_count = away_stats['Position'].value_counts(normalize=True).values[0]
        away_direction_name = f"{away_stats['Direction'].value_counts(normalize=True).index[0]}"
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
    max_marker_size = 2500
    network_df['Pass Width'] = (network_df['Event'] / network_df['Event'].max() * max_line_width)
    avg_df['Size'] = (avg_df['No Passes'] / avg_df['No Passes'].max() * max_marker_size)

    min_transparency = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(network_df), 1))
    c_transparency = network_df['Event'] / network_df['Event'].max()
    c_transparency = (c_transparency * (1 - min_transparency)) + min_transparency
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, ax = pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    if pass_df.shape[0] > 1:
        pass_lines = pitch.lines(network_df['Start X'], network_df['Start Y'],
                                 network_df['End X'], network_df['End Y'],
                                 lw=network_df['Pass Width'],
                                 color=color,
                                 zorder=1,
                                 ax=ax)
        pass_nodes = pitch.scatter(avg_df['Start X'], avg_df['Start Y'],
                                   s=avg_df['Size'],
                                   color='#d20614',
                                   edgecolors='black',
                                   linewidth=1,
                                   alpha=0.5,
                                   ax=ax)
        for index, row in avg_df.iterrows():
            pitch.annotate(row['Jersey No'], xy=(row['Start X'], row['Start Y']), c='white', va='center',
                           ha='center', size=16, weight='bold', ax=ax)

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

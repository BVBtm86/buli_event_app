import pandas as pd
import numpy as np
from mplsoccer import Pitch
import seaborn as sns
import plotly.express as px
from matplotlib.colors import to_rgba


def game_staring_11(data, game_teams):
    """ Create Starting 11 Df """
    df_starting_11 = data.copy()
    print(df_starting_11)

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
                y=point['y']-1,
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


def game_passing_network(data, game_teams, starting_players, plot_team):
    """ Create Pass Df """
    pass_df = data.copy()
    starting_df = starting_players
    starting_df['Team_Player'] = starting_df['Team'] + "_" + starting_df['Player Name']
    final_df = pd.merge(left=pass_df,
                        right=starting_df[['Team', 'Opponent', 'Player Name', 'Starting 11']],
                        left_on=['Team', 'Opponent', 'Player Name'],
                        right_on=['Team', 'Opponent', 'Player Name'],
                        how='left')
    final_df.dropna(subset=['Starting 11'], inplace=True)
    final_df.drop(columns=['Starting 11'], inplace=True)
    final_df['Team_Player'] = final_df['Team'] + "_" + final_df['Player Name Receiver']
    final_df = pd.merge(left=final_df,
                        right=starting_df[['Team_Player', 'Starting 11']],
                        left_on=['Team_Player'],
                        right_on=['Team_Player'],
                        how='left')
    final_df.dropna(subset=['Starting 11'], inplace=True)

    """ Create Network Data """
    final_df['Pass Pair'] = final_df['Player Name'] + " - " + final_df['Player Name Receiver']
    home_passes = final_df[final_df['Team'] == game_teams[0]]
    away_passes = final_df[final_df['Team'] == game_teams[1]]

    home_pass_count = home_passes.groupby(['Pass Pair'])['Event'].count().reset_index()
    away_pass_count = away_passes.groupby(['Pass Pair'])['Event'].count().reset_index()

    avg_home_pos = home_passes.groupby(['Player Name'])[['Start X', 'Start Y']].mean().reset_index()
    avg_away_pos = away_passes.groupby(['Player Name'])[['Start X', 'Start Y']].mean().reset_index()

    ''' Final Home Data '''
    final_home_passes = home_passes[['Player Name', 'Player Name Receiver', 'Pass Pair']]
    final_home_passes = pd.merge(left=final_home_passes,
                                 right=home_pass_count,
                                 left_on='Pass Pair',
                                 right_on='Pass Pair',
                                 how='left')
    final_home_passes = pd.merge(left=final_home_passes,
                                 right=avg_home_pos,
                                 left_on=['Player Name'],
                                 right_on=['Player Name'],
                                 how='left')
    avg_home_pos.rename(columns={'Player Name': 'Player Name Receiver'}, inplace=True)
    final_home_passes = pd.merge(left=final_home_passes,
                                 right=avg_home_pos,
                                 left_on=['Player Name Receiver'],
                                 right_on=['Player Name Receiver'],
                                 how='left')
    final_home_passes.rename(columns={'Start X_x': 'Start X', 'Start Y_x': 'Start Y',
                                      'Start X_y': 'End X', 'Start Y_y': 'End Y'}, inplace=True)
    final_home_passes = final_home_passes.sort_values(by='Player Name')

    ''' Final Away Data '''
    final_away_passes = away_passes[['Player Name', 'Player Name Receiver', 'Pass Pair']]
    final_away_passes = pd.merge(left=final_away_passes,
                                 right=away_pass_count,
                                 left_on='Pass Pair',
                                 right_on='Pass Pair',
                                 how='left')
    final_away_passes = pd.merge(left=final_away_passes,
                                 right=avg_away_pos,
                                 left_on=['Player Name'],
                                 right_on=['Player Name'],
                                 how='left')
    avg_away_pos.rename(columns={'Player Name': 'Player Name Receiver'}, inplace=True)
    final_away_passes = pd.merge(left=final_away_passes,
                                 right=avg_away_pos,
                                 left_on=['Player Name Receiver'],
                                 right_on=['Player Name Receiver'],
                                 how='left')
    final_away_passes.rename(columns={'Start X_x': 'Start X', 'Start Y_x': 'Start Y',
                                      'Start X_y': 'End X', 'Start Y_y': 'End Y'}, inplace=True)
    final_away_passes = final_away_passes.sort_values(by='Player Name')

    """ Plot Network Data """
    if plot_team == game_teams[0]:
        final_network_df = final_home_passes.copy()
    else:
        final_network_df = final_away_passes.copy()

    final_network_df['First Name'] = final_network_df['Player Name'].apply(lambda x: x.split()[0][0]) + ". "
    final_network_df['Last Name'] = final_network_df['Player Name'].apply(lambda x: x.split()[1:])
    final_network_df['Last Name'] = final_network_df['Last Name'].apply(lambda x: str(x).replace("[", "").
                                                                        replace("]", "").replace(",", "").
                                                                        replace("'", ""))
    final_network_df['Name'] = final_network_df['First Name'] + final_network_df['Last Name']

    max_line_width = 20
    max_marker_size = 3000
    final_network_df['Pass Width'] = (final_away_passes['Event'] / final_away_passes['Event'].max() * max_line_width)

    min_transparency = 0.3
    color = np.array(to_rgba('white'))
    c_transparency = final_network_df['Event'] / final_network_df['Event'].max()
    c_transparency = (c_transparency * (1 - min_transparency)) + min_transparency
    # color[:, 3] = c_transparency
    print(c_transparency)

    pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig, pitch_ax = pitch.grid(title_height=0.01,axis=False, )

    pass_lines = pitch.lines(final_network_df['Start X'], final_network_df['Start Y'],
                             final_network_df['End X'], final_network_df['End Y'], lw=final_network_df['Pass Width'],
                             color=color, zorder=10, ax=pitch_ax['pitch'])

    pass_nodes = pitch.scatter(final_network_df['Start X'], final_network_df['Start Y'],
                               color='#d20614', edgecolors='black', linewidth=0.1, alpha=0.5, ax=pitch_ax['pitch'],
                               s=200)
    for index, row in final_network_df.iterrows():
        pitch.annotate(row['Name'], xy=(row['Start X'] - 1, row['Start Y'] - 3), c='white', va='center',
                       ha='center', size=10, ax=pitch_ax['pitch'])

    return pitch_fig

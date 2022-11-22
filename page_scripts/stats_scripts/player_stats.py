from mplsoccer import VerticalPitch, Pitch
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
from matplotlib.colors import to_rgba
import math

team_colors = ["#d20614", "#392864"]


def calculate_distance(x_start, y_start, x_end, y_end):
    pass_distance = math.sqrt((x_end * 1.05 - x_start * 1.05) ** 2 + (y_end * 0.68 - y_start * 0.68) ** 2)
    return pass_distance


def player_analysis(data_player, player_data_opponent, player_options, analysis_type,
                    no_games, no_events, plot_type, event_outcome, event_type, player_names):
    """ Final Player Data """
    final_df_player = data_player.copy()
    if analysis_type == "vs Player":
        final_df_opponent = player_data_opponent.copy()
        color_plotly = {player_names[0]: team_colors[0], player_names[1]: team_colors[1]}
    else:
        final_df_opponent = None
        color_plotly = {player_names[0]: team_colors[0]}

    """ Plot Events """
    if analysis_type == "Individual":
        pitch_player_team = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        x_arrows = [0, 102]
        y_arrows = [15, 102]
        x_pitch = "Start X"
        y_pitch = "Start Y"
    else:
        pitch_player_team = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        x_arrows = [0, 102]
        y_arrows = [30, 102]
        x_pitch = "Start Y"
        y_pitch = "Start X"

    pitch_fig_player_team, pitch_ax_player_team = pitch_player_team.draw(figsize=(10, 10))
    pitch_player_team.arrows(x_arrows[0], x_arrows[1],
                             y_arrows[0], y_arrows[1],
                             width=2,
                             headwidth=5,
                             headlength=5,
                             color="#ffffff",
                             alpha=1,
                             ax=pitch_ax_player_team)

    if plot_type == "Position":
        sns.scatterplot(data=final_df_player,
                        x=x_pitch,
                        y=y_pitch,
                        s=75,
                        color=team_colors[0],
                        alpha=0.75,
                        legend=False)
    else:
        sns.kdeplot(x=final_df_player[x_pitch],
                    y=final_df_player[y_pitch],
                    shade=True,
                    shade_lowest=False,
                    alpha=0.25,
                    n_levels=10,
                    cmap='plasma')

    if analysis_type == "vs Player":
        pitch_player_opp = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        pitch_fig_player_opp, pitch_ax_opp = pitch_player_opp.draw(figsize=(10, 10))
        pitch_player_opp.arrows(0, 102,
                                30, 102,
                                width=2,
                                headwidth=5,
                                headlength=5,
                                color="#ffffff",
                                alpha=1,
                                ax=pitch_ax_opp)

        if plot_type == "Position":
            sns.scatterplot(data=final_df_opponent,
                            x="Start Y",
                            y="Start X",
                            s=75,
                            color=team_colors[1],
                            alpha=0.75,
                            legend=False)
        else:
            sns.kdeplot(x=final_df_opponent['Start Y'],
                        y=final_df_opponent['Start X'],
                        shade=True,
                        shade_lowest=False,
                        alpha=0.25,
                        n_levels=10,
                        cmap='plasma')
    else:
        pitch_fig_player_opp = None

    """ Event Stats """
    if player_options == "By Game":
        player_stats = pd.DataFrame([player_names[0],
                                     final_df_player.shape[0],
                                     final_df_player.shape[0] / no_events[0]]).T
        player_stats.columns = ['Player Name', 'No Events', '% of Events']
    else:
        player_stats = pd.DataFrame([player_names[0],
                                     final_df_player.shape[0],
                                     final_df_player.shape[0] / no_games[0]]).T
        player_stats.columns = ['Player Name', 'No Events', 'Avg Events/G']
    player_stats.set_index("Player Name", inplace=True)

    if analysis_type == "vs Player":
        if player_options == "By Game":
            opponent_stats = pd.DataFrame([player_names[1],
                                           final_df_opponent.shape[0],
                                           final_df_opponent.shape[0] / no_events[1]]).T
            opponent_stats.columns = ['Player Name', 'No Events', '% of Events']
        else:
            opponent_stats = pd.DataFrame([player_names[1],
                                           final_df_opponent.shape[0],
                                           final_df_opponent.shape[0] / no_games[1]]).T
            opponent_stats.columns = ['Player Name', 'No Events', 'Avg Events/G']
        opponent_stats.set_index("Player Name", inplace=True)
    else:
        opponent_stats = None

    """ Analysis by Field and Direction Position """
    final_df_player['Position'] = final_df_player['Start X'].apply(lambda x: 'Def Third' if x < 34 else (
        'Mid Third' if 34 <= x < 68 else 'Att Third'))
    final_df_player['Direction'] = final_df_player['Start Y'].apply(lambda x: 'Right Side' if x < 30 else (
        'Mid Side' if 30 <= x < 70 else 'Left Side'))

    if analysis_type == "vs Player":
        final_df_opponent['Position'] = final_df_opponent['Start X'].apply(lambda x: 'Def Third' if x < 34 else (
            'Mid Third' if 34 <= x < 68 else 'Att Third'))
        final_df_opponent['Direction'] = final_df_opponent['Start Y'].apply(lambda x: 'Right Side' if x < 30 else (
            'Mid Side' if 30 <= x < 70 else 'Left Side'))

    """ Analysis Plots """
    if analysis_type == "vs Player":
        analysis_events = \
            pd.concat([final_df_player[['Player Name', 'Position', 'Direction']],
                       final_df_opponent[['Player Name', 'Position', 'Direction']]], axis=0)
    else:
        analysis_events = final_df_player[['Player Name', 'Position', 'Direction']].copy()

    position_stats = pd.DataFrame(analysis_events.groupby('Player Name')['Position'].value_counts(normalize=True))
    position_stats.columns = ['%']
    position_stats.reset_index(inplace=True)
    if analysis_type == "vs Player":
        position_stats['Player Name'] = \
            pd.Categorical(position_stats['Player Name'], [player_names[0], player_names[1]])
    position_stats['Position'] = pd.Categorical(position_stats['Position'], ['Def Third', 'Mid Third', 'Att Third'])
    position_stats = position_stats.sort_values(by=['Player Name', 'Position'])

    direction_stats = pd.DataFrame(analysis_events.groupby('Player Name')['Direction'].value_counts(normalize=True))
    direction_stats.columns = ['%']
    direction_stats.reset_index(inplace=True)
    if analysis_type == "vs Player":
        direction_stats['Player Name'] = \
            pd.Categorical(direction_stats['Player Name'], [player_names[0], player_names[1]])
    direction_stats['Direction'] = pd.Categorical(direction_stats['Direction'], ['Right Side', 'Mid Side', 'Left Side'])
    direction_stats = direction_stats.sort_values(by=['Player Name', 'Direction'])

    """ Insight Plot """
    players_position_fig = px.bar(position_stats,
                                  x='Position',
                                  y='%',
                                  color='Player Name',
                                  color_discrete_map=color_plotly,
                                  height=500,
                                  barmode='group',
                                  title=f"{event_outcome} <b>{event_type}</b> by Pitch Position",
                                  hover_data={'%': ':.2%'})
    players_position_fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)"},
        showlegend=False)
    players_position_fig.layout.yaxis.tickformat = ',.0%'

    players_direction_fig = px.bar(direction_stats,
                                   x='Direction',
                                   y='%',
                                   color='Player Name',
                                   color_discrete_map=color_plotly,
                                   height=500,
                                   barmode='group',
                                   title=f"{event_outcome} <b>{event_type}</b> by Pitch Direction",
                                   hover_data={'%': ':.2%'})
    players_direction_fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)"},
        showlegend=False)
    players_direction_fig.layout.yaxis.tickformat = ',.0%'

    """ Event Insights """
    """ Analysis Insights """
    if final_df_player.shape[0]:
        player_position_name = f"the {final_df_player['Position'].value_counts(normalize=True).index[0]}"
        player_position_count = final_df_player['Position'].value_counts(normalize=True).values[0]
        player_direction_name = f"the {final_df_player['Direction'].value_counts(normalize=True).index[0]}"
        player_direction_count = final_df_player['Direction'].value_counts(normalize=True).values[0]
    else:
        player_position_name = "Any Position"
        player_position_count = 0
        player_direction_name = "Any Direction"
        player_direction_count = 0
    if final_df_opponent is not None:
        if final_df_opponent.shape[0]:
            opp_position_name = f"the {final_df_opponent['Position'].value_counts(normalize=True).index[0]}"
            opp_position_count = final_df_opponent['Position'].value_counts(normalize=True).values[0]
            opp_direction_name = f"the {final_df_opponent['Direction'].value_counts(normalize=True).index[0]}"
            opp_direction_count = final_df_opponent['Direction'].value_counts(normalize=True).values[0]
        else:
            opp_position_name = "Any Position"
            opp_position_count = 0
            opp_direction_name = "Any Direction"
            opp_direction_count = 0
    else:
        opp_position_name = None
        opp_position_count = None
        opp_direction_name = None
        opp_direction_count = None

    position_insight = [[player_position_name, opp_position_name], [player_position_count, opp_position_count]]
    direction_insight = [[player_direction_name, opp_direction_name], [player_direction_count, opp_direction_count]]

    return pitch_fig_player_team, pitch_fig_player_opp, player_stats, opponent_stats, \
           players_position_fig, players_direction_fig, position_insight, direction_insight


def player_passing_network(data_player, data_opponent, analysis_type, players_jersey, opponent_jersey):
    """ Create Pass Df """
    pass_player_df = data_player.copy()
    jersey_player_df = players_jersey.copy()
    pass_player_df = \
        pass_player_df[pass_player_df['Player Name'] != pass_player_df['Player Name Receiver']].reset_index(drop=True)

    if analysis_type == "vs Player":
        pass_opponent_df = data_opponent.copy()
        pass_opponent_df = \
            pass_opponent_df[pass_opponent_df['Player Name'] != pass_opponent_df['Player Name Receiver']].reset_index(
                drop=True)
    else:
        pass_opponent_df = None

    """ Create Player Network Data """
    ''' Average Data '''
    player_avg_df = pass_player_df.groupby(['Player Name'])[['Start X', 'Start Y']].agg(
        {'Start X': ['mean'], 'Start Y': ['mean', 'count']}).reset_index()
    player_avg_df.columns = ['Player Name', 'Start X', 'Start Y', 'No Passes']
    player_avg_receiver_df = pass_player_df.groupby(['Player Name Receiver'])[['End X', 'End Y']].agg(
        {'End X': ['mean'], 'End Y': ['mean', 'count']}).reset_index()
    player_avg_receiver_df.columns = ['Player Name Receiver', 'Start X', 'Start Y', 'No Passes']
    player_avg_df = pd.concat([player_avg_df,
                               player_avg_receiver_df.rename(columns={"Player Name Receiver": "Player Name"})])
    player_avg_df = pd.merge(left=player_avg_df,
                             right=jersey_player_df,
                             left_on=['Player Name'],
                             right_on=['Player Name'],
                             how='left')
    player_avg_df = player_avg_df.dropna(subset=['Jersey No'])
    player_avg_df = player_avg_df.nlargest(11, 'No Passes').reset_index(drop=True)
    if player_avg_df.shape[0] > 1:
        player_avg_df.iloc[0, 3] = player_avg_df.iloc[1:, 3].max() + 5
    pass_player_df['Keep'] = \
        pass_player_df['Player Name Receiver'].apply(lambda x: True if x in player_avg_df['Player Name'].values else False)
    pass_player_df = pass_player_df[pass_player_df['Keep'] == 1].reset_index(drop=True)
    pass_player_df['Pass Pair'] = pass_player_df['Player Name'] + " - " + pass_player_df['Player Name Receiver']
    player_network_df = pass_player_df.groupby(['Pass Pair'])['Event'].count().reset_index()
    player_network_df['Player Name'] = player_network_df['Pass Pair'].apply(lambda x: x.split(" - ")[0])
    player_network_df['Player Name Receiver'] = player_network_df['Pass Pair'].apply(lambda x: x.split(" - ")[1])
    player_network_df = pd.merge(left=player_network_df,
                                 right=player_avg_df.drop(columns=['No Passes']),
                                 left_on=['Player Name'],
                                 right_on=['Player Name'],
                                 how='left')
    player_network_df = pd.merge(left=player_network_df,
                                 right=player_avg_receiver_df,
                                 left_on=['Player Name Receiver'],
                                 right_on=['Player Name Receiver'],
                                 how='left')
    player_network_df.iloc[:, -4:] = np.round(player_network_df.iloc[:, -4:], 2)
    player_network_df.rename(columns={'Start X_x': 'Start X', 'Start Y_x': 'Start Y',
                                      'Start X_y': 'End X', 'Start Y_y': 'End Y'}, inplace=True)

    """ Plot Network Data """
    max_line_width = 10
    max_marker_size = 2000
    player_network_df['Pass Width'] = (player_network_df['Event'] / player_network_df['Event'].max() * max_line_width)
    player_avg_df['Size'] = (player_avg_df['No Passes'] / player_avg_df['No Passes'].max() * max_marker_size)

    min_transparency = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(player_network_df), 1))
    c_transparency = player_network_df['Event'] / player_network_df['Event'].max()
    c_transparency = (c_transparency * (1 - min_transparency)) + min_transparency
    color[:, 3] = c_transparency
    if analysis_type == "Individual":
        player_pitch = Pitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        x_arrows = [0, 102]
        y_arrows = [15, 102]
    else:
        player_pitch = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        x_arrows = [0, 102]
        y_arrows = [30, 102]
    player_pitch_fig, player_pitch_ax = player_pitch.draw(figsize=(15, 15), constrained_layout=True, tight_layout=False)
    player_pitch.arrows(x_arrows[0], x_arrows[1],
                        y_arrows[0], y_arrows[1],
                        width=2,
                        headwidth=5,
                        headlength=5,
                        color='#ffffff',
                        alpha=1,
                        ax=player_pitch_ax)

    if pass_player_df.shape[0] > 0:
        player_pitch.lines(player_network_df['Start X'], player_network_df['Start Y'],
                           player_network_df['End X'], player_network_df['End Y'],
                           lw=player_network_df['Pass Width'],
                           color=color,
                           zorder=1,
                           ax=player_pitch_ax)
        player_pitch.scatter(player_avg_df['Start X'], player_avg_df['Start Y'],
                             s=player_avg_df['Size'],
                             color='#d20614',
                             edgecolors='black',
                             linewidth=1,
                             alpha=0.5,
                             ax=player_pitch_ax)
        for index, row in player_avg_df.iterrows():
            player_pitch.annotate(int(row['Jersey No']), xy=(row['Start X'], row['Start Y']), c='#ffffff', va='center',
                                  ha='center', size=16, weight='bold', ax=player_pitch_ax)

    """ Analysis Network Data """
    top_passes_player_df = pd.merge(left=player_network_df,
                                    right=player_avg_df[['Player Name', 'Jersey No']],
                                    left_on=['Player Name Receiver'],
                                    right_on=['Player Name'],
                                    how='left')
    top_passes_player_df['Player Combo'] = \
        top_passes_player_df['Jersey No_x'].astype(str) + " - " + top_passes_player_df['Jersey No_y'].astype(str)
    top_passes_player_df['Player Combo'] = top_passes_player_df['Player Combo'].str.replace(".0", "")
    top_passes_player_df = top_passes_player_df.sort_values(by='Event', ascending=True)
    top_passes_player_df.rename(columns={"Event": "No of Passes"}, inplace=True)
    if top_passes_player_df.shape[0] > 0:
        player_top_fig = px.bar(top_passes_player_df,
                                x='No of Passes',
                                y='Player Combo',
                                height=600,
                                title=f"Top {top_passes_player_df.shape[0]} <b>Successful Passes</b> between "
                                      f"<b>{pass_player_df['Player Name'].unique()[0]}</b> and Teammates")
        player_top_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)

        player_top_fig.update_traces(marker_color='#d20614')
    else:
        player_top_fig = None

    """ Create Opponent Network Data """
    ''' Average Data '''
    if pass_opponent_df is not None:
        opponent_avg_df = pass_opponent_df.groupby(['Player Name'])[['Start X', 'Start Y']].agg(
            {'Start X': ['mean'], 'Start Y': ['mean', 'count']}).reset_index()
        opponent_avg_df.columns = ['Player Name', 'Start X', 'Start Y', 'No Passes']
        opponent_avg_receiver_df = pass_opponent_df.groupby(['Player Name Receiver'])[['End X', 'End Y']].agg(
            {'End X': ['mean'], 'End Y': ['mean', 'count']}).reset_index()
        opponent_avg_receiver_df.columns = ['Player Name Receiver', 'Start X', 'Start Y', 'No Passes']
        opponent_avg_df = pd.concat([opponent_avg_df,
                                     opponent_avg_receiver_df.rename(columns={"Player Name Receiver": "Player Name"})])
        opponent_avg_df = pd.merge(left=opponent_avg_df,
                                   right=opponent_jersey,
                                   left_on=['Player Name'],
                                   right_on=['Player Name'],
                                   how='left')
        opponent_avg_df = opponent_avg_df.dropna(subset=['Jersey No'])
        opponent_avg_df = opponent_avg_df.nlargest(11, 'No Passes').reset_index(drop=True)
        if opponent_avg_df.shape[0] > 1:
            opponent_avg_df.iloc[0, 3] = opponent_avg_df.iloc[1:, 3].max() + 5

        pass_opponent_df['Keep'] = \
            pass_opponent_df['Player Name Receiver'].apply(
                lambda x: True if x in opponent_avg_df['Player Name'].values else False)
        pass_opponent_df = pass_opponent_df[pass_opponent_df['Keep'] == 1].reset_index(drop=True)

        pass_opponent_df['Pass Pair'] = pass_opponent_df['Player Name'] + " - " + pass_opponent_df[
            'Player Name Receiver']
        opponent_network_df = pass_opponent_df.groupby(['Pass Pair'])['Event'].count().reset_index()
        opponent_network_df['Player Name'] = opponent_network_df['Pass Pair'].apply(lambda x: x.split(" - ")[0])
        opponent_network_df['Player Name Receiver'] = opponent_network_df['Pass Pair'].apply(lambda x: x.split(" - ")[1])
        opponent_network_df = pd.merge(left=opponent_network_df,
                                       right=opponent_avg_df.drop(columns=['No Passes']),
                                       left_on=['Player Name'],
                                       right_on=['Player Name'],
                                       how='left')
        opponent_network_df = pd.merge(left=opponent_network_df,
                                       right=opponent_avg_receiver_df,
                                       left_on=['Player Name Receiver'],
                                       right_on=['Player Name Receiver'],
                                       how='left')
        opponent_network_df.iloc[:, -4:] = np.round(opponent_network_df.iloc[:, -4:], 2)
        opponent_network_df.rename(columns={'Start X_x': 'Start X', 'Start Y_x': 'Start Y',
                                            'Start X_y': 'End X', 'Start Y_y': 'End Y'}, inplace=True)

        """ Plot Network Data """
        max_line_width = 10
        max_marker_size = 2000
        opponent_network_df['Pass Width'] = (
                    opponent_network_df['Event'] / opponent_network_df['Event'].max() * max_line_width)
        opponent_avg_df['Size'] = (opponent_avg_df['No Passes'] / opponent_avg_df['No Passes'].max() * max_marker_size)

        min_transparency = 0.3
        color = np.array(to_rgba('white'))
        color = np.tile(color, (len(opponent_network_df), 1))
        c_transparency = opponent_network_df['Event'] / opponent_network_df['Event'].max()
        c_transparency = (c_transparency * (1 - min_transparency)) + min_transparency
        color[:, 3] = c_transparency

        opponent_pitch = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
        opponent_pitch_fig, opponent_pitch_ax = opponent_pitch.draw(figsize=(15, 15), constrained_layout=True,
                                                                    tight_layout=False)
        opponent_pitch.arrows(0, 102,
                              30, 102,
                              width=2,
                              headwidth=5,
                              headlength=5,
                              color='#ffffff',
                              alpha=1,
                              ax=opponent_pitch_ax)

        if pass_opponent_df.shape[0] > 0:
            opponent_pitch.lines(opponent_network_df['Start X'], opponent_network_df['Start Y'],
                                 opponent_network_df['End X'], opponent_network_df['End Y'],
                                 lw=opponent_network_df['Pass Width'],
                                 color=color,
                                 zorder=1,
                                 ax=opponent_pitch_ax)
            opponent_pitch.scatter(opponent_avg_df['Start X'], opponent_avg_df['Start Y'],
                                   s=opponent_avg_df['Size'],
                                   color='#392864',
                                   edgecolors='black',
                                   linewidth=1,
                                   alpha=0.5,
                                   ax=opponent_pitch_ax)
            for index, row in opponent_avg_df.iterrows():
                opponent_pitch.annotate(int(row['Jersey No']), xy=(row['Start X'], row['Start Y']), c='#ffffff',
                                        va='center',
                                        ha='center', size=16, weight='bold', ax=opponent_pitch_ax)

            """ Analysis Network Data """
            top_opponent_player_df = pd.merge(left=opponent_network_df,
                                              right=opponent_avg_df[['Player Name', 'Jersey No']],
                                              left_on=['Player Name Receiver'],
                                              right_on=['Player Name'],
                                              how='left')
            top_opponent_player_df['Player Combo'] = \
                top_opponent_player_df['Jersey No_x'].astype(str) + " - " + top_opponent_player_df[
                    'Jersey No_y'].astype(str)
            top_opponent_player_df['Player Combo'] = top_opponent_player_df['Player Combo'].str.replace(".0", "")
            top_opponent_player_df = top_opponent_player_df.sort_values(by='Event', ascending=True)
            top_opponent_player_df.rename(columns={"Event": "No of Passes"}, inplace=True)
            if top_opponent_player_df.shape[0] > 0:
                opponent_top_fig = px.bar(top_opponent_player_df,
                                          x='No of Passes',
                                          y='Player Combo',
                                          height=600,
                                          title=f"Top {top_opponent_player_df.shape[0]} <b>Successful Passes</b> between "
                                                f"<b>{pass_opponent_df['Player Name'].unique()[0]}</b> and Teammates")
                opponent_top_fig.update_layout({
                    "plot_bgcolor": "rgba(0, 0, 0, 0)"},
                    showlegend=False)
                opponent_top_fig.update_traces(marker_color='#392864')
            else:
                opponent_top_fig = None
    else:
        opponent_pitch_fig = None
        opponent_top_fig = None

    """ Player Event Stats """
    player_stats_df = pd.DataFrame([pass_player_df['Player Name'].unique()[0], pass_player_df.shape[0]]).T
    player_stats_df.columns = ["Player Name", "No of Passes"]
    player_stats_df.set_index("Player Name", inplace=True)

    if pass_opponent_df is not None:
        opponents_stats_df = pd.DataFrame([pass_opponent_df['Player Name'].unique()[0], pass_opponent_df.shape[0]]).T
        opponents_stats_df.columns = ["Player Name", "No of Passes"]
        opponents_stats_df.set_index("Player Name", inplace=True)
    else:
        opponents_stats_df = None

    return player_pitch_fig, opponent_pitch_fig, top_passes_player_df, player_top_fig, \
        top_opponent_player_df, opponent_top_fig, player_stats_df, opponents_stats_df

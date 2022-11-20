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


def team_analysis(data, analysis_type, event_teams, plot_type, no_games, event_outcome, event_type):
    final_df = data.copy()

    if analysis_type == "vs Opponents":
        team_df = final_df[final_df['Team'] == event_teams[0]].reset_index(drop=True)
        opp_df = final_df[final_df['Opponent'] == event_teams[1]].reset_index(drop=True)
        stat_name = "Opponents"
    else:
        team_df = final_df[final_df['Team'] == event_teams[0]].reset_index(drop=True)
        opp_df = final_df[final_df['Team'] == event_teams[1]].reset_index(drop=True)
        stat_name = event_teams[1]

    """ Plot Events """
    pitch_team = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig_team, pitch_ax_team = pitch_team.draw(figsize=(10, 10))
    pitch_team.arrows(0, 102,
                      30, 102,
                      width=2,
                      headwidth=5,
                      headlength=5,
                      color="#ffffff",
                      alpha=1,
                      ax=pitch_ax_team)

    if plot_type == "Position":
        sns.scatterplot(data=team_df,
                        x="Start Y",
                        y="Start X",
                        s=75,
                        color=team_colors[0],
                        alpha=0.75,
                        legend=False)
    else:
        sns.kdeplot(x=team_df['Start Y'],
                    y=team_df['Start X'],
                    shade=True,
                    shade_lowest=False,
                    alpha=0.25,
                    n_levels=10,
                    cmap='plasma')

    pitch_opp = VerticalPitch(pitch_type='opta', pitch_color='#57595D', line_color='white')
    pitch_fig_opp, pitch_ax_opp = pitch_opp.draw(figsize=(10, 10))
    pitch_opp.arrows(0, 102,
                     30, 102,
                     width=2,
                     headwidth=5,
                     headlength=5,
                     color="#ffffff",
                     alpha=1,
                     ax=pitch_ax_opp)

    if plot_type == "Position":
        sns.scatterplot(data=opp_df,
                        x="Start Y",
                        y="Start X",
                        s=75,
                        color=team_colors[1],
                        alpha=0.75,
                        legend=False)
    else:
        sns.kdeplot(x=opp_df['Start Y'],
                    y=opp_df['Start X'],
                    shade=True,
                    shade_lowest=False,
                    alpha=0.25,
                    n_levels=10,
                    cmap='plasma')

    """ Event Stats """
    team_stats = pd.DataFrame([event_teams[0],
                               team_df.shape[0],
                               team_df.shape[0] / no_games[0]]).T
    opp_stats = pd.DataFrame([stat_name,
                              opp_df.shape[0],
                              opp_df.shape[0] / no_games[1]]).T
    event_stats = pd.concat([team_stats, opp_stats])
    event_stats.columns = ['Team', 'No Events', 'Avg Events/G']
    event_stats.set_index('Team', inplace=True)

    """ Analysis by Field Position """
    team_df['Position'] = team_df['Start X'].apply(lambda x: 'Def Third' if x < 34 else (
        'Mid Third' if 34 <= x < 68 else 'Att Third'))
    opp_df['Position'] = opp_df['Start X'].apply(lambda x: 'Def Third' if x < 34 else (
        'Mid Third' if 34 <= x < 68 else 'Att Third'))

    """ Analysis by Direction """
    team_df['Direction'] = team_df['Start Y'].apply(lambda x: 'Right Side' if x < 30 else (
        'Mid Side' if 30 <= x < 70 else 'Left Side'))
    opp_df['Direction'] = opp_df['Start Y'].apply(lambda x: 'Right Side' if x < 30 else (
        'Mid Side' if 30 <= x < 70 else 'Left Side'))
    opp_df['Team Opp'] = stat_name

    """ Analysis Plots """
    analysis_events = \
        pd.concat([team_df[['Team', 'Position', 'Direction']],
                   opp_df[['Team Opp', 'Position', 'Direction']].rename(columns={"Team Opp": "Team"})], axis=0)

    position_stats = pd.DataFrame(analysis_events.groupby('Team')['Position'].value_counts(normalize=True))
    position_stats.columns = ['%']
    position_stats.reset_index(inplace=True)
    position_stats['Team'] = pd.Categorical(position_stats['Team'], [event_teams[0], stat_name])
    position_stats['Position'] = pd.Categorical(position_stats['Position'], ['Def Third', 'Mid Third', 'Att Third'])
    position_stats = position_stats.sort_values(by=['Team', 'Position'])

    direction_stats = pd.DataFrame(analysis_events.groupby('Team')['Direction'].value_counts(normalize=True))
    direction_stats.columns = ['%']
    direction_stats.reset_index(inplace=True)
    direction_stats['Team'] = pd.Categorical(direction_stats['Team'], [event_teams[0], stat_name])
    direction_stats['Direction'] = pd.Categorical(direction_stats['Direction'], ['Right Side', 'Mid Side', 'Left Side'])
    direction_stats = direction_stats.sort_values(by=['Team', 'Direction'])

    """ Insight Plot """
    position_fig = px.bar(position_stats,
                          x='Position',
                          y='%',
                          color='Team',
                          color_discrete_map={event_teams[0]: team_colors[0],
                                              stat_name: team_colors[1]},
                          height=500,
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
                           color_discrete_map={event_teams[0]: team_colors[0],
                                               stat_name: team_colors[1]},
                           height=500,
                           barmode='group',
                           title=f"{event_outcome} <b>{event_type}</b> by Pitch Direction",
                           hover_data={'%': ':.2%'})
    direction_fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)"},
        showlegend=False)
    direction_fig.layout.yaxis.tickformat = ',.0%'

    """ Event Insights """
    """ Analysis Insights """
    if team_df.shape[0]:
        team_position_name = f"the {team_df['Position'].value_counts(normalize=True).index[0]}"
        team_position_count = team_df['Position'].value_counts(normalize=True).values[0]
        team_direction_name = f"the {team_df['Direction'].value_counts(normalize=True).index[0]}"
        team_direction_count = team_df['Direction'].value_counts(normalize=True).values[0]
    else:
        team_position_name = "Any Position"
        team_position_count = 0
        team_direction_name = "Any Direction"
        team_direction_count = 0
    if opp_df.shape[0]:
        opp_position_name = f"the {opp_df['Position'].value_counts(normalize=True).index[0]}"
        opp_position_count = opp_df['Position'].value_counts(normalize=True).values[0]
        opp_direction_name = f"the {opp_df['Direction'].value_counts(normalize=True).index[0]}"
        opp_direction_count = opp_df['Direction'].value_counts(normalize=True).values[0]
    else:
        opp_position_name = "Any Position"
        opp_position_count = 0
        opp_direction_name = "Any Direction"
        opp_direction_count = 0

    position_insight = [[team_position_name, opp_position_name], [team_position_count, opp_position_count]]
    direction_insight = [[team_direction_name, opp_direction_name], [team_direction_count, opp_direction_count]]

    return pitch_fig_team, pitch_fig_opp, event_stats, position_fig, direction_fig, position_insight, direction_insight


def team_passing_network(data, network_players):
    """ Create Pass Df """
    pass_df = data.copy()
    pass_df = pass_df[pass_df['Player Name'] != pass_df['Player Name Receiver']].reset_index(drop=True)

    pass_df['Keep Player'] = \
        pass_df['Player Name'].isin(network_players['Player Name'].values) * 1 + \
        pass_df['Player Name Receiver'].isin(network_players['Player Name'].values) * 1
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
                      right=network_players[['Player Name', 'Jersey No']],
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
                             right=network_players[['Player Name', 'Jersey No']],
                             left_on=['Player Name'],
                             right_on=['Player Name'],
                             how='left')
    top_passes_df = pd.merge(left=top_passes_df,
                             right=network_players.rename(
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
                         height=500,
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


def team_passing_direction(data, analysis_type, passing_teams):

    """ Create Pass Df """
    pass_df = data.copy()

    if pass_df.shape[0] > 0:
        pass_df['Distance'] = \
            pass_df.apply(lambda x: calculate_distance(x['Start X'], x['Start Y'], x['End X'], x['End Y']), axis=1)
        pass_df['Distance Length'] = pass_df['Distance'].apply(lambda x: 'Short Passes' if x <= 10 else (
            'Medium Passes' if 10 < x <= 25 else 'Long Passes'))
        pass_df['Direction'] = pass_df['End X'] - pass_df['Start X']
        pass_df['Direction Type'] = \
            pass_df['Direction'].apply(lambda x: "Forward Passes" if x > 0 else "Backward Passes")

    pass_df_team = pass_df[pass_df['Team'] == passing_teams[0]]
    if analysis_type == "vs Opponents":
        pass_df_opp = pass_df[pass_df['Opponent'] == passing_teams[1]]
    else:
        pass_df_opp = pass_df[pass_df['Team'] == passing_teams[1]]

    """ Team Direction Insights """
    if pass_df_team.shape[0] > 0:
        team_pass_outcome_count = pd.DataFrame(pass_df_team['Outcome'].value_counts())
        team_pass_outcome_perc = pd.DataFrame(pass_df_team['Outcome'].value_counts(normalize=True))
        team_pass_outcome = pd.concat([team_pass_outcome_count, team_pass_outcome_perc], axis=1)
        team_pass_outcome.columns = ['No of Events', '% of Events']

        team_pass_length = pd.DataFrame(pass_df_team.groupby("Outcome")['Distance Length'].value_counts(normalize=True))
        team_pass_length.columns = ['%']
        team_pass_length.reset_index(inplace=True)
        team_pass_direction = \
            pd.DataFrame(pass_df_team.groupby("Outcome")['Direction Type'].value_counts(normalize=True))
        team_pass_direction.columns = ['%']
        team_pass_direction.reset_index(inplace=True)

        """ Length Plot """
        team_length_fig = px.bar(team_pass_length,
                                 x='Distance Length',
                                 y='%',
                                 color='Outcome',
                                 color_discrete_map={"Successful": team_colors[0],
                                                     "Unsuccessful": team_colors[1]},
                                 height=350,
                                 barmode='group',
                                 title=f"Length of Passes by Outcome",
                                 hover_data={'%': ':.2%'})
        team_length_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        team_length_fig.layout.yaxis.tickformat = ',.0%'

        """ Direction Plot """
        team_direction_fig = px.bar(team_pass_direction,
                                    x='Direction Type',
                                    y='%',
                                    color='Outcome',
                                    color_discrete_map={"Successful": team_colors[0],
                                                        "Unsuccessful": team_colors[1]},
                                    height=350,
                                    barmode='group',
                                    title=f"Direction of Passes by Outcome",
                                    hover_data={'%': ':.2%'})
        team_direction_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        team_direction_fig.layout.yaxis.tickformat = ',.0%'

        if 'Successful' in team_pass_outcome.index:
            team_successful_insight = \
                [team_pass_length[team_pass_length['Outcome'] == "Successful"]['Distance Length'].values[0],
                 team_pass_direction[team_pass_direction['Outcome'] == "Successful"]['Direction Type'].values[0]]
        else:
            team_successful_insight = None
        if 'Unsuccessful' in team_pass_outcome.index:
            team_unsuccessful_insight = [
                team_pass_length[team_pass_length['Outcome'] == "Unsuccessful"]['Distance Length'].values[0],
                team_pass_direction[team_pass_direction['Outcome'] == "Unsuccessful"]['Direction Type'].values[0]]
        else:
            team_unsuccessful_insight = None
    else:
        team_pass_outcome = None
        team_length_fig = None
        team_direction_fig = None
        team_successful_insight = None
        team_unsuccessful_insight = None

    """ Team Direction Insights """
    if pass_df_opp.shape[0] > 0:
        opp_pass_outcome_count = pd.DataFrame(pass_df_opp['Outcome'].value_counts())
        opp_pass_outcome_perc = pd.DataFrame(pass_df_opp['Outcome'].value_counts(normalize=True))
        opp_pass_outcome = pd.concat([opp_pass_outcome_count, opp_pass_outcome_perc], axis=1)
        opp_pass_outcome.columns = ['No of Events', '% of Events']

        opp_pass_length = pd.DataFrame(pass_df_opp.groupby("Outcome")['Distance Length'].value_counts(normalize=True))
        opp_pass_length.columns = ['%']
        opp_pass_length.reset_index(inplace=True)
        opp_pass_direction = pd.DataFrame(pass_df_opp.groupby("Outcome")['Direction Type'].value_counts(normalize=True))
        opp_pass_direction.columns = ['%']
        opp_pass_direction.reset_index(inplace=True)

        """ Length Plot """
        opp_length_fig = px.bar(opp_pass_length,
                                x='Distance Length',
                                y='%',
                                color='Outcome',
                                color_discrete_map={"Successful": team_colors[0],
                                                    "Unsuccessful": team_colors[1]},
                                height=350,
                                barmode='group',
                                title=f"Length of Passes by Outcome",
                                hover_data={'%': ':.2%'})
        opp_length_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        opp_length_fig.layout.yaxis.tickformat = ',.0%'

        """ Direction Plot """
        opp_direction_fig = px.bar(opp_pass_direction,
                                   x='Direction Type',
                                   y='%',
                                   color='Outcome',
                                   color_discrete_map={"Successful": team_colors[0],
                                                       "Unsuccessful": team_colors[1]},
                                   height=350,
                                   barmode='group',
                                   title=f"Direction of Passes by Outcome",
                                   hover_data={'%': ':.2%'})
        opp_direction_fig.update_layout({
            "plot_bgcolor": "rgba(0, 0, 0, 0)"},
            showlegend=False)
        opp_direction_fig.layout.yaxis.tickformat = ',.0%'

        if 'Successful' in opp_pass_outcome.index:
            opp_successful_insight = \
                [opp_pass_length[opp_pass_length['Outcome'] == "Successful"]['Distance Length'].values[0],
                 opp_pass_direction[opp_pass_direction['Outcome'] == "Successful"]['Direction Type'].values[0]]
        else:
            opp_successful_insight = None
        if 'Unsuccessful' in opp_pass_outcome.index:
            opp_unsuccessful_insight = [
                opp_pass_length[opp_pass_length['Outcome'] == "Unsuccessful"]['Distance Length'].values[0],
                opp_pass_direction[opp_pass_direction['Outcome'] == "Unsuccessful"]['Direction Type'].values[0]]
        else:
            opp_unsuccessful_insight = None
    else:
        opp_pass_outcome = None
        opp_length_fig = None
        opp_direction_fig = None
        opp_successful_insight = None
        opp_unsuccessful_insight = None

    return \
        [team_pass_outcome, team_length_fig, team_direction_fig, team_successful_insight, team_unsuccessful_insight], \
        [opp_pass_outcome, opp_length_fig, opp_direction_fig, opp_successful_insight, opp_unsuccessful_insight]

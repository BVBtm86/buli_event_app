from mplsoccer import VerticalPitch
import seaborn as sns
import pandas as pd
import plotly.express as px

team_colors = ["#d20614", "#392864"]


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
    analysis_events = pd.concat([team_df[['Team','Position','Direction']],
    opp_df[['Team Opp', 'Position', 'Direction']].rename(columns={"Team Opp":"Team"})], axis=0)

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

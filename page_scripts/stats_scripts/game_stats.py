import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import plotly.express as px


def game_staring_11(data, game_teams):
    """ Create Starting 11 Df """
    df_starting_11 = data.copy()
    df_starting_11['First Name'] = df_starting_11['Player Name'].apply(lambda x: x.split()[0][0]) + ". "
    df_starting_11['Last Name'] = df_starting_11['Player Name'].apply(lambda x: x.split()[1:])
    df_starting_11['Last Name'] = df_starting_11['Last Name'].apply(lambda x: str(x).replace("[", "").
                                                                    replace("]", "").replace(",", "").replace("'",""))
    df_starting_11['Name'] = df_starting_11['First Name'] + df_starting_11['Last Name']

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
                         s=200,
                         hue='Team',
                         alpha=0.75,
                         legend=False)

    text_plot = pd.concat({'x': df_starting_11['X'],
                                'y': df_starting_11['Y'],
                                'Name': df_starting_11['Name']}, axis=1)
    for i, point in text_plot.iterrows():
        ax.text(x=point['x'] - 2.5,
                y=point['y'] - 5,
                s=str(point['Name']),
                color="#ffffff")

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

def game_passing_network(data, data_period, game_teams, plot_type, event_outcome, event_type):
    pass
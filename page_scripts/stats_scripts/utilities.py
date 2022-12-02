import pandas as pd
import numpy as np
from supabase import create_client
import streamlit as st


# ##### Supabase Connection
@st.experimental_singleton(show_spinner=False)
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


# ##### Supabase Table Queries
@st.experimental_memo(ttl=600, show_spinner=False)
def info_query():
    """ Return Game Info """
    game_info_query = supabase.table('buli_events_team_info').select('*').execute().data
    game_info = pd.DataFrame(game_info_query)

    return game_info


@st.experimental_memo(ttl=600, show_spinner=False)
def players_info_query(team, match_day):
    """ Return Player Game Info """
    game_player_query_team = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_player_team_df = pd.DataFrame(game_player_query_team)
    game_player_query_opp = supabase.table('buli_events_player_info').select('*'). \
        eq('Opponent', team).eq('Match Day', match_day).execute().data
    game_player_opp_df = pd.DataFrame(game_player_query_opp)

    game_players_df = pd.concat([game_player_team_df, game_player_opp_df], axis=0)

    return game_players_df


@st.experimental_memo(ttl=600, show_spinner=False)
def event_query(team, match_day):
    """ Return Game Events """
    game_team_query = supabase.table('buli_events_stats').select('*'). \
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_team_df = pd.DataFrame(game_team_query)
    game_opp_query = supabase.table('buli_events_stats').select('*'). \
        eq('Opponent', team).eq('Match Day', match_day).execute().data
    game_opp_df = pd.DataFrame(game_opp_query)

    if game_team_df['Venue'].unique()[0] == 'Away':
        game_team_df['Start X'] = np.abs(game_team_df['Start X'] - 100)
        game_team_df['End X'] = np.abs(game_team_df['End X'] - 100)
        game_team_df['Start Y'] = np.abs(game_team_df['Start Y'] - 100)
        game_team_df['End Y'] = np.abs(game_team_df['End Y'] - 100)

    if game_opp_df['Venue'].unique()[0] == 'Away':
        game_opp_df['Start X'] = np.abs(game_opp_df['Start X'] - 100)
        game_opp_df['End X'] = np.abs(game_opp_df['End X'] - 100)
        game_opp_df['Start Y'] = np.abs(game_opp_df['Start Y'] - 100)
        game_opp_df['End Y'] = np.abs(game_opp_df['End Y'] - 100)

    game_event_df = pd.concat([game_team_df, game_opp_df], axis=0)

    return game_event_df


@st.experimental_memo(ttl=600, show_spinner=False)
def team_query(team_sql, opponent_sql, period_sql, venue_sql, result_sql):
    """ Return Game Events """
    if team_sql == opponent_sql:
        if venue_sql == "Home":
            venue_opp_sql = "Away"
        else:
            venue_opp_sql = "Home"
        if result_sql == "Win":
            result_opp_sql = "Defeat"
        elif result_sql == "Defeat":
            result_opp_sql = "Win"
        else:
            result_opp_sql = "Draw"
        if venue_sql == "All Games":
            if result_sql == "All Results":
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
            else:
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_opp_sql).execute().data
        else:
            if result_sql == "All Results":
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql).execute().data
            else:
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql). \
                    eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql). \
                    eq('Result', result_opp_sql).execute().data
    else:
        venue_opp_sql = venue_sql
        result_opp_sql = result_sql
        if venue_sql == "All Games":
            if result_sql == "All Results":
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
            else:
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_opp_sql).execute().data
        else:
            if result_sql == "All Results":
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql).execute().data
            else:
                game_team_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql). \
                    eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql). \
                    eq('Result', result_opp_sql).execute().data

    game_team_df = pd.DataFrame(game_team_query)
    game_opp_df = pd.DataFrame(game_opp_query)

    game_event_df = pd.concat([game_team_df, game_opp_df], axis=0)

    return game_event_df


@st.experimental_memo(ttl=600, show_spinner=False)
def team_players_query(team, match_days):
    """ Return Player Game Info """
    team_player_query = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).execute().data
    team_player_team_df = pd.DataFrame(team_player_query)
    team_player_team_df = team_player_team_df[team_player_team_df['Match Day'].isin(match_days)].reset_index(drop=True)

    return team_player_team_df


@st.experimental_memo(ttl=600, show_spinner=False)
def avg_keep_players(team, current_match_day):
    """ Return Player With more than 10% Minute Played """
    team_player_query = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).execute().data
    team_players = pd.DataFrame(team_player_query)
    group_players = team_players.groupby('Player Name')['Minutes Played'].sum()

    min_threshold = current_match_day * 90 * 0.1
    final_players = list(group_players[group_players > min_threshold].index)
    final_players.sort()

    return final_players


@st.experimental_memo(ttl=600, show_spinner=False)
def games_player_played(team, player_name):
    """ Return Player With more than 10% Minute Played """
    player_query = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).eq("Player Name", player_name).execute().data
    player_games = pd.DataFrame(player_query)

    match_days_played = player_games['Match Day'].unique()

    return player_games, match_days_played


@st.experimental_memo(ttl=600, show_spinner=False)
def players_query(team_sql, player_name_sql, player_option, match_day_sql, period_sql, venue_sql, result_sql):
    """ Return Game Events """
    if player_option == "By Game":
        player_query = supabase.table('buli_events_stats').select('*'). \
            eq('Team', team_sql).eq("Player Name", player_name_sql).eq("Match Day", match_day_sql).execute().data
    else:
        if venue_sql == "All Games":
            if result_sql == "All Results":
                player_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).eq("Player Name", player_name_sql).\
                    gt('Match Day', period_sql[0] - 1).lt('Match Day', period_sql[1] + 1).execute().data
            else:
                player_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).eq("Player Name", player_name_sql).\
                    gt('Match Day', period_sql[0] - 1).lt('Match Day', period_sql[1] + 1).\
                    eq('Result', result_sql).execute().data
        else:
            if result_sql == "All Results":
                player_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).eq("Player Name", player_name_sql).\
                    gt('Match Day', period_sql[0] - 1).\
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql).execute().data
            else:
                player_query = supabase.table('buli_events_stats'). \
                    select('*').eq('Team', team_sql).eq("Player Name", player_name_sql).\
                    gt('Match Day', period_sql[0] - 1).lt('Match Day', period_sql[1] + 1).\
                    eq('Venue', venue_sql).eq('Result', result_sql).execute().data

    player_df = pd.DataFrame(player_query)

    return player_df


@st.experimental_memo(ttl=600, show_spinner=False)
def avg_keep_players_opponent(team, current_match_day, match_day, player_name):
    """ Return Player With more than 10% Minute Played """
    team_player_query = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).execute().data
    team_players = pd.DataFrame(team_player_query)
    group_players = team_players.groupby('Player Name')['Minutes Played'].sum()

    min_threshold = current_match_day * 90 * 0.1
    season_players = list(group_players[group_players > min_threshold].index)

    if match_day is not None:
        team_day_query = supabase.table('buli_events_player_info').select('*'). \
            eq('Team', team).eq("Match Day", match_day).execute().data
        team_day_df = pd.DataFrame(team_day_query)
        day_players = list(team_day_df['Player Name'].unique())
        raw_players = [player for player in season_players if player in day_players]
    else:
        raw_players = season_players
    final_players = [player for player in raw_players if player != player_name]
    final_players.sort()

    return final_players


@st.experimental_memo(ttl=600, show_spinner=False)
def players_jersey_query(team, team_opp):
    """ Return Player Jersey """
    players_jerseys = supabase.table('buli_events_player_info').select('*'). \
        eq('Team', team).execute().data
    players_jerseys_df = pd.DataFrame(players_jerseys)
    players_jerseys_df = players_jerseys_df[['Player Name', 'Jersey No']].reset_index(drop=True)
    players_jerseys_df.drop_duplicates(inplace=True)
    players_jerseys_df.reset_index(drop=True, inplace=True)

    if team_opp is not None:
        opponent_jerseys = supabase.table('buli_events_player_info').select('*'). \
            eq('Team', team_opp).execute().data
        opponent_jerseys_df = pd.DataFrame(opponent_jerseys)
        opponent_jerseys_df = opponent_jerseys_df[['Player Name', 'Jersey No']].reset_index(drop=True)
        opponent_jerseys_df.drop_duplicates(inplace=True)
        opponent_jerseys_df.reset_index(drop=True, inplace=True)
    else:
        opponent_jerseys_df = None

    return players_jerseys_df, opponent_jerseys_df

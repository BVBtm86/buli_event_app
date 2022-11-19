import pandas as pd
import numpy as np
from supabase import create_client
import streamlit as st
from PIL import Image

# ##### Logo and App Info
buli_logo = Image.open('images/Bundesliga.png')

st.set_page_config(layout="wide",
                   page_title="Bundesliga Events App",
                   page_icon=buli_logo,
                   initial_sidebar_state="expanded")


# ##### Supabase Connection
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = init_connection()


# ##### Supabase Table Queries
@st.experimental_memo(ttl=600)
def info_query():
    """ Return Game Info """
    game_info_query = supabase.table('game_info_stats').select('*').execute().data
    game_info = pd.DataFrame(game_info_query)

    return game_info


@st.experimental_memo(ttl=600)
def players_info_query(team, match_day):
    """ Return Player Game Info """
    game_player_query_team = supabase.table('game_player_info').select('*'). \
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_player_team_df = pd.DataFrame(game_player_query_team)
    game_player_query_opp = supabase.table('game_player_info').select('*'). \
        eq('Opponent', team).eq('Match Day', match_day).execute().data
    game_player_opp_df = pd.DataFrame(game_player_query_opp)

    game_players_df = pd.concat([game_player_team_df, game_player_opp_df], axis=0)

    return game_players_df


@st.experimental_memo(ttl=600)
def event_query(team, match_day):
    """ Return Game Events """
    game_team_query = supabase.table('game_events_stats').select('*'). \
        eq('Team', team).eq('Match Day', match_day).execute().data
    game_team_df = pd.DataFrame(game_team_query)
    game_opp_query = supabase.table('game_events_stats').select('*'). \
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


@st.experimental_memo(ttl=600)
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
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
            else:
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_opp_sql).execute().data
        else:
            if result_sql == "All Results":
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql).execute().data
            else:
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql). \
                    eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Opponent', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql). \
                    eq('Result', result_opp_sql).execute().data
    else:
        venue_opp_sql = venue_sql
        result_opp_sql = result_sql
        if venue_sql == "All Games":
            if result_sql == "All Results":
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).execute().data
            else:
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Result', result_opp_sql).execute().data
        else:
            if result_sql == "All Results":
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql).execute().data
            else:
                game_team_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', team_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_sql). \
                    eq('Result', result_sql).execute().data
                game_opp_query = supabase.table('game_events_stats'). \
                    select('*').eq('Team', opponent_sql).gt('Match Day', period_sql[0] - 1). \
                    lt('Match Day', period_sql[1] + 1).eq('Venue', venue_opp_sql). \
                    eq('Result', result_opp_sql).execute().data

    game_team_df = pd.DataFrame(game_team_query)
    game_opp_df = pd.DataFrame(game_opp_query)

    game_event_df = pd.concat([game_team_df, game_opp_df], axis=0)

    return game_event_df


@st.experimental_memo(ttl=600)
def team_players_query(team, match_days):
    """ Return Player Game Info """
    team_player_query = supabase.table('game_player_info').select('*'). \
        eq('Team', team).execute().data
    team_player_team_df = pd.DataFrame(team_player_query)
    team_player_team_df = team_player_team_df[team_player_team_df['Match Day'].isin(match_days)].reset_index(drop=True)

    return team_player_team_df

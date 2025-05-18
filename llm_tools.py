from typing import Dict, Any, List
import pandas as pd

from stats_functions import (
    aggregate_bowling_stats,  
    aggregate_batter_stats,    
    get_match_up_stats,        
    get_batter_stats_for_match,   
    get_bowler_stats_for_match,   
)

def wrap_agg_bowling(data, bowler, start_date=None, end_date=None):
    df = aggregate_bowling_stats(data, bowler, start_date, end_date)
    return df.to_dict(orient="records")

def wrap_agg_batting(data, batter, start_date=None, end_date=None):
    df = aggregate_batter_stats(data, batter, start_date, end_date)
    return df.to_dict(orient="records")

def wrap_matchup(data, batter, bowler, start_date=None, end_date=None):
    df = get_match_up_stats(data, batter, bowler, start_date, end_date)
    return df.to_dict(orient="records")


def wrap_batter_match(data, batter):
    df = get_batter_stats_for_match(data, batter)
    return df.to_dict(orient="records")

def wrap_bowler_match(data, bowler):
    df = get_bowler_stats_for_match(data, bowler)
    return df.to_dict(orient="records")


def dispatch(fname: str, params: Dict[str, Any], data):
    if fname == "get_aggregated_bowling_stats":
        return wrap_agg_bowling(
            data, params["bowler_name"],
            params.get("start_date"), params.get("end_date")
        )
    if fname == "get_aggregated_batting_stats":
        return wrap_agg_batting(
            data, params["batter_name"],
            params.get("start_date"), params.get("end_date")
        )
    if fname == "get_batter_vs_bowler_stats":
        return wrap_matchup(
            data,
            params["batter_name"], params["bowler_name"],
            params.get("start_date"), params.get("end_date")
        )
    if fname == "get_batting_performance_by_match":
        return wrap_batter_match(data, params["batter_name"])
    if fname == "get_bowling_performance_by_match":
        return wrap_bowler_match(data, params["bowler_name"])
    raise ValueError(f"Unknown function: {fname}")


_date_props = {
    "start_date": {"type": "string",
                   "description": "Inclusive start date (YYYY/MM/DD or any human‑readable form)."},
    "end_date":   {"type": "string",
                   "description": "Inclusive end date. Omit for open ended."},
}

function_schemas: List[Dict[str, Any]] = [
    {  
        "name": "get_aggregated_bowling_stats",
        "description": "Overall bowling stats for a bowler, optionally filtered by date range.",
        "parameters": {
            "type": "object",
            "properties": {"bowler_name": {"type": "string"}, **_date_props},
            "required": ["bowler_name"],
        },
    },
    {   
        "name": "get_aggregated_batting_stats",
        "description": "Overall batting stats for a batter, optionally filtered by date range.",
        "parameters": {
            "type": "object",
            "properties": {"batter_name": {"type": "string"}, **_date_props},
            "required": ["batter_name"],
        },
    },
    {   
        "name": "get_batter_vs_bowler_stats",
        "description": "Head‑to‑head stats between a batter and bowler, optionally filtered by date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "batter_name": {"type": "string"},
                "bowler_name": {"type": "string"},
                **_date_props,
            },
            "required": ["batter_name", "bowler_name"],
        },
    },
    {  
        "name": "get_batting_performance_by_match",
        "description": "Match‑by‑match batting performance for a batter.",
        "parameters": {
            "type": "object",
            "properties": {"batter_name": {"type": "string"}},
            "required": ["batter_name"],
        },
    },
    {   
        "name": "get_bowling_performance_by_match",
        "description": "Match‑by‑match bowling performance for a bowler.",
        "parameters": {
            "type": "object",
            "properties": {"bowler_name": {"type": "string"}},
            "required": ["bowler_name"],
        },
    },
]

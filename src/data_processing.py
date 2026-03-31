import pandas as pd
import numpy as np
from datetime import timedelta

def load_data(filepath):
    """Loads and validates K-Pop playlist dataset."""
    df = pd.read_csv(filepath, parse_dates=["date"])
    
    # Validation & Prep
    df['duration_mins'] = df['duration_ms'] / 60000.0
    df = df.sort_values(by=["date", "position"], ascending=[True, True])
    return df

def calculate_re_entries_and_momentum(df):
    """Calculates chart re-entries, momentum spikes, and decay for each song."""
    
    # We define an "entry" as joining the playlist (rank 1-50)
    # A "re-entry" means prior entry existed but dropped off completely (not in Top 50) for > 1 day
    
    records = []
    
    # Analyze song by song
    grouped = df.groupby(["song", "artist"])
    
    for (song, artist), group in grouped:
        # Sort chronologically
        group = group.sort_values(by="date").reset_index(drop=True)
        
        # Calculate gaps in days between consecutive appearances
        group['date_diff'] = group['date'].diff().dt.days
        
        # An entry/re-entry happens roughly when 'date_diff' > 1 or it's the first record
        # Identify "Run ID" for continuous streaks
        is_new_run = group['date_diff'] > 1.0
        # The first item is always a new run
        is_new_run.iloc[0] = True 
        
        group['run_id'] = is_new_run.cumsum()
        
        # Count total re-entries for this song
        total_runs = group['run_id'].nunique()
        re_entry_count = total_runs - 1 # 0 means original entry only
        
        # Compute specific metrics per Run
        runs = group.groupby('run_id')
        for run_id, run_df in runs:
            start_date = run_df['date'].min()
            end_date = run_df['date'].max()
            duration_days = (end_date - start_date).days + 1
            
            entry_type = "First Entry" if run_id == 1 else "Re-Entry"
            
            # Momentum Spike (Popularity change on re-entry day)
            # Find popularity on the first day of this run
            initial_popularity = run_df.iloc[0]['popularity']
            peak_popularity = run_df['popularity'].max()
            spike_score = peak_popularity - initial_popularity # Higher means massive surge
            
            # Rank Jump (Best rank achieved during this run)
            best_rank = run_df['position'].min()
            
            # Rank Recovery Speed (Days from entry to peak rank)
            peak_date = run_df.loc[run_df['position'].idxmin(), 'date']
            recovery_speed = (peak_date - start_date).days
            
            # Decay (Post-Comeback Retention Days)
            # We already have duration_days, which proxies retention
            
            records.append({
                "song": song,
                "artist": artist,
                "entry_type": entry_type,
                "run_id": run_id,
                "start_date": start_date,
                "end_date": end_date,
                "retention_days": duration_days,
                "re_entry_count": re_entry_count,
                "momentum_spike_score": spike_score,
                "best_rank_achieved": best_rank,
                "rank_recovery_speed": recovery_speed,
                "album_type": run_df['album_type'].iloc[0],
                "is_explicit": run_df['is_explicit'].iloc[0],
                "total_tracks": run_df['total_tracks'].iloc[0]
            })
            
    momentum_df = pd.DataFrame(records)
    
    # Compute Proxy Score for Fandom Intensity
    # Formula: (Retention Days * 0.5) + (Peak Spikes * 0.3) + (Re-entry Count * 0.2)
    # We normalize these values
    def normalize(val):
        return (val - val.min()) / (val.max() - val.min() + 0.0001)
        
    momentum_df["fandom_proxy_score"] = (
        normalize(momentum_df["retention_days"]) * 0.5 + 
        normalize(momentum_df["momentum_spike_score"]) * 0.3 + 
        normalize(momentum_df["re_entry_count"]) * 0.2
    ) * 100
    
    return momentum_df

def get_artist_summary(momentum_df):
    """Aggregates fandom scores by artist."""
    summary = momentum_df.groupby("artist").agg({
        "fandom_proxy_score": "mean",
        "re_entry_count": "max",
        "momentum_spike_score": "max",
        "entry_type": "count"
    }).reset_index()
    summary = summary.rename(columns={"entry_type": "total_entries"})
    summary = summary.sort_values(by="fandom_proxy_score", ascending=False)
    return summary

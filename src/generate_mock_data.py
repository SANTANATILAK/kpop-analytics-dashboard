import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_mock_data(start_date="2023-01-01", days=365):
    """Generates synthetic K-Pop playlist chart data capturing momentum and re-entries."""
    
    dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(days)]
    
    artists = [
        "BTS", "BLACKPINK", "NewJeans", "Stray Kids", "TWICE", 
        "SEVENTEEN", "TXT", "LE SSERAFIM", "IVE", "ATEEZ"
    ]
    
    songs = {
        "BTS": [("Dynamite", False, "Single", 1, 200000), ("Butter", False, "Single", 1, 160000), ("Fake Love", False, "Album", 11, 240000)],
        "BLACKPINK": [("Pink Venom", False, "Album", 8, 190000), ("How You Like That", False, "Single", 1, 180000)],
        "NewJeans": [("Super Shy", False, "Album", 6, 150000), ("OMG", False, "Single", 2, 210000), ("Ditto", False, "Single", 2, 195000)],
        "Stray Kids": [("God's Menu", False, "Album", 14, 180000), ("MANIAC", False, "Album", 7, 190000)],
        "TWICE": [("The Feels", False, "Single", 1, 190000), ("Feel Special", False, "Album", 7, 210000)],
        "SEVENTEEN": [("Super", False, "Album", 6, 185000), ("HOT", False, "Album", 9, 200000)],
        "TXT": [("Sugar Rush Ride", False, "Album", 5, 175000), ("0X1=LOVESONG", False, "Album", 8, 205000)],
        "LE SSERAFIM": [("ANTIFRAGILE", False, "Album", 5, 185000), ("UNFORGIVEN", False, "Album", 7, 180000)],
        "IVE": [("LOVE DIVE", False, "Single", 2, 175000), ("I AM", False, "Album", 11, 180000)],
        "ATEEZ": [("BOUNCY", False, "Album", 6, 195000), ("Guerrilla", False, "Album", 7, 200000)]
    }

    # Introduce some explicit Western collabs to test explicit flag
    songs["BTS"].append(("ON (feat. Sia)", True, "Album", 20, 240000))
    songs["BLACKPINK"].append(("Ice Cream (with Selena Gomez)", False, "Single", 1, 170000))

    data = []
    
    for date in dates:
        daily_chart = []
        for artist in artists:
            for song_info in songs[artist]:
                title, is_explicit, album_type, total_tracks, duration_ms = song_info
                
                # Base popularity random walk (simulates organic decay)
                base_pop = np.random.normal(50, 15)
                
                # Combine multiple sin waves to simulate comeback momentum and re-entries
                # K-Pop has sharp spikes, usually around anniversaries or new album releases (even for old songs)
                cycle_period = random.choice([30, 60, 90, 180]) # days between spikes
                days_since_start = (date - dates[0]).days
                
                momentum_spike = 0
                if days_since_start % cycle_period < 5: 
                    # Sharp 5-day spike (Fandom push)
                    momentum_spike = np.random.normal(30, 5) 
                elif days_since_start % cycle_period < 15:
                    # Decay phase
                    momentum_spike = np.random.normal(10, 5)

                popularity = max(0, min(100, base_pop + momentum_spike))
                
                # Calculate rank based on popularity relative to others that day (we will sort later)
                daily_chart.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "song": title,
                    "artist": artist,
                    "popularity": round(popularity, 2),
                    "duration_ms": duration_ms,
                    "album_type": album_type,
                    "total_tracks": total_tracks,
                    "is_explicit": is_explicit,
                    "album_cover_url": f"https://example.com/{artist.lower().replace(' ', '_')}_cover.jpg"
                })
        
        # Sort by popularity to assign rank 1-50
        daily_chart = sorted(daily_chart, key=lambda x: x["popularity"], reverse=True)[:50]
        
        for rank, entry in enumerate(daily_chart, 1):
            entry["position"] = rank
            data.append(entry)

    df = pd.DataFrame(data)
    
    # Reorder columns to match requested format
    cols = ["date", "position", "song", "artist", "popularity", "duration_ms", "album_type", "total_tracks", "is_explicit", "album_cover_url"]
    df = df[cols]
    
    # Ensure directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), '../data/playlist_history.csv')
    df.to_csv(out_path, index=False)
    print(f"Mock data generated successfully at {out_path}")

if __name__ == "__main__":
    generate_mock_data()

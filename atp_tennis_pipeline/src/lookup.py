import pandas as pd

def load_data():
    # Load the pre-built pipeline data
    rankings = pd.read_parquet("data/output/atp_rankings.parquet")
    stats = pd.read_parquet("data/output/atp_player_stats.parquet")
    return rankings, stats

def search_player(name: str, rankings: pd.DataFrame, stats: pd.DataFrame):
    # Search for a player by name (case-insensitive, partial match)
    name_lower = name.lower()

    # Search in the stats table - check if the input matches any part of the name
    mask = stats["player_name"].str.lower().str.contains(name_lower, na=False)
    matches = stats[mask]

    if len(matches) == 0:
        print(f"\nNo player found matching '{name}")
        return
    
    if len(matches) > 1:
        print(f"\nFound {len(matches)} players matching '{name}:") 
        for _, row in matches.iterrows():
            print(f" - {row['player_name']} ({row['country_code']})")
        print("Try a more specific name.")
        return
    
    # Exactly one match - show their full profile
    player = matches.iloc[0]
    player_id = player["player_id"]

    # Check if they have a ranking
    rank_row = rankings[rankings["player_id"] == player_id]

    print_player_card(player, rank_row)

def print_player_card(player: pd.Series, rank_row: pd.DataFrame):
    """Display a player's stats in a nice format."""
    print("\n" + "=" * 50)
    print(f"    {player['player_name']} ({player['country_code']})")
    print("=" * 50)

    # Ranking
    if len(rank_row) > 0:
        rank = int(rank_row.iloc[0]["rank"])
        points = int(rank_row.iloc[0]["ranking_points"])
        print(f"    Ranking:    #{rank} ({points} pts)")
    else:
        print(f"    Ranking:    Unranked")

    # Win/Loss record
    print(f"    Record:     {player['wins']}W - {player['losses']}L ({player['win_pct']}%)")
    print(f"    Aces/match: {player['aces_avg']}")

    # Surface stats
    print(f"\n Surface Performance:")
    for surface, col in [("hard", "hard_win_pct"), ("Clay","clay_win_pct"), ("Grass","grass_win_pct")]:
        if col in player.index and pd.notna(player[col]):
            print(f"    {surface:10} {player[col]}% wins")
    
    print("=" * 50 + "\n")


def main():
    """Interactive player lookup - keeps asking until you type 'quit"""
    print("\nLoading ATP data...")
    rankings, stats = load_data()
    print(f"Ready! {len(stats)} players loaded.\n")

    while True:
        name = input("Enter a player name (or 'quit' to exit):").strip()

        if name.lower() == "quit":
            print("Goodbye!")
            break
        if name == "":
            continue
        search_player(name, rankings, stats)

if __name__ == "__main__":
    main()
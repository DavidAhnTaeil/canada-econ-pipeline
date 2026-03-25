import json
from api_client import make_request

# Test: Get available baseball leagues
# data = make_request("/leagues")

# for league in data["response"]:
#     print(f"{league['id']:>4} {league['name']} ({league['country']['name']})")

data = make_request("/games", params={"league": 5, "season":2025})
# data = make_request("/seasons")
print(f"2025 results: {data['results']}")
print(json.dumps(data["response"][:2], indent=2))

# for team in data["response"]:
#     print(f"    ID: {team['id']:<5} {team['name']}")

# print("\n   KBO 2024 Standings:")
# print(" " + "-" *55)

# for entry in data["response"][0]:
#     team = entry["team"]["name"]
#     games = entry["games"]["played"]
#     win = entry["games"]["win"]["total"]
#     lose = entry["games"]["lose"]["total"]
#     pct = entry["games"]["win"]["percentage"]
#     print(f"    {entry['position']:<4} {team:<20} {win}W - {lose}L ({pct})")

data = make_request("/games", params={"league": 1, "season": 2025, "date": "2025-04-10"})

print(f"Results: {data['results']}")
if data["response"]:
    print(json.dumps(data["response"][0], indent=2))
else:
    print("No data. Let's check what's available...")
    # Try the status endpoint to see our account
    status = make_request("/status")
    print(json.dumps(status, indent=2))
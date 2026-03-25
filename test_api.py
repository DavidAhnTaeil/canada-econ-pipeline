import json
from api_client import get_exchange_rates

# Test: Get USD/CAD rates for the last week
data = get_exchange_rates("KRW", "2025-03-10", "2025-03-19")

# Let's see what the response looks like
print(json.dumps(data, indent=2))

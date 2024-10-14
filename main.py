import json
import re

# https://github.com/ua-parser/uap-python
from ua_parser import user_agent_parser

from user_agents.user_agent import UserAgent
from user_agents.update_data import get_user_agent_data

# Inspired from intoli/user-agents: https://github.com/intoli/user-agents

print("PY3 user-agents")

# get_user_agent_data()

# -----------------------------------------------------------
# https://github.com/intoli/user-agents
# -----------------------------------------------------------

# Generating a Random User Agent
user_agent = UserAgent()
print(str(user_agent))
print(json.dumps(user_agent.data, indent=2))

# Restricting Device Categories
user_agent = UserAgent({"deviceCategory": "mobile"})

# Generating Multiple User Agents With The Same Filters
user_agent = UserAgent({"platform": "Win32"})
user_agents = [user_agent() for _ in range(1000)]

# Regular Expression Matching
user_agent = UserAgent({"userAgent": re.compile("Safari")})
print(user_agent)


# Custom Filter Functions
user_agent = UserAgent({"custom_filter": lambda agent: agent["screenWidth"] > 1300})
print(user_agent)

def filter_user_agent(data):
    user_agent_parsed = user_agent_parser.Parse(data["userAgent"])
    return (
        user_agent_parsed["os"]["family"] == "iOS"
        and int(user_agent_parsed["os"]["major"]) > 11
    )


user_agent = UserAgent({"custom_filter": filter_user_agent})
print(user_agent)

# Combining Filter
user_agent = UserAgent(
    {
        "userAgent": re.compile(r"Safari"),
        "connection": {
            "effectiveType": "4g",
        },
        "deviceCategory": "desktop",
        "platform": "MacIntel",
    }
)
print(user_agent)

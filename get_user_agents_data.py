import os

from user_agents.update_data import get_user_agent_data

if __name__ == "__main__":

    print("PY3 user-agents")

    os.environ['HTTP_PROXY'] = 'proxy-internet.crip.cnamts.fr:3128'
    os.environ['HTTPS_PROXY'] = 'proxy-internet.crip.cnamts.fr:3128'
    get_user_agent_data()

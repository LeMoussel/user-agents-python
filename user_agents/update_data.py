import os
import gzip

# https://requests.readthedocs.io/en/latest/
import requests


def gunzip_data(input_filename=None):
    if not input_filename or not input_filename.endswith(".gz"):
        raise ValueError(
            "Filename must be specified and end with `.gz` for gunzipping."
        )

    output_filename = input_filename[:-3]
    with open(input_filename, "rb") as f:
        compressed_data = f.read()

    data = gzip.decompress(compressed_data)

    with open(output_filename, "wb") as f:
        f.write(data)


def get_user_agent_data():
    USER_AGENT_FILE = "data/user-agents.json.gz"
    try:
        response = requests.get(
            url="https://raw.githubusercontent.com/intoli/user-agents/master/src/user-agents.json.gz",
            timeout=15,
        )
        response.raise_for_status()

        with open(USER_AGENT_FILE, "wb") as file:
            file.write(response.content)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.ConnectionError as err:
        print(f"Connection error occurred: {err}")
    except requests.exceptions.Timeout as err:
        print(f"Timeout error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")

    gunzip_data(USER_AGENT_FILE)
    os.remove(USER_AGENT_FILE)


if __name__ == "__main__":
    get_user_agent_data()

# TODO rename user-agents-python to py3-user-agents
# TODO download update_data

# pylint: disable=line-too-long

import re
import random
import json
import pathlib
from typing import Callable, List, Any, Union, Dict


# Inspired from Intoli user-agents : https://github.com/intoli/user-agents/blob/main/src/user-agent.ts


# Normalizes the total weight to 1 and constructs a cumulative distribution.
def make_cumulative_weight_index_pairs(weight_index_pairs):
    total_weight = sum(weight for weight, _ in weight_index_pairs)
    cumulative_sum = 0
    cumulative_weight_index_pairs = []
    for weight, index in weight_index_pairs:
        cumulative_sum += weight / total_weight
        cumulative_weight_index_pairs.append((cumulative_sum, index))
    return cumulative_weight_index_pairs


def filter_user_agents(
    agent: Dict[str, Any], criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    match = True
    for key, value in criteria.items():
        if callable(value):
            if not value(agent):
                match = False
                break
        elif key in agent:
            if isinstance(value, str) or isinstance(value, (int, float)):
                if agent[key] != value:
                    match = False
                    break
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key in agent[key]:
                        if agent[key][sub_key] != sub_value:
                            match = False
                            break
                    else:
                        match = False
                        break
            elif isinstance(value, re.Pattern):
                if not re.search(value, agent[key]):
                    match = False
                    break
        else:
            match = False
            break

    return match


# Construct normalized cumulative weight index pairs given the filters.
def construct_cumulative_weight_index_pairs_from_filters(filters):
    if not filters:
        return default_cumulative_weight_index_pairs

    weight_index_pairs = [
        (raw_user_agent["weight"], index)
        for index, raw_user_agent in enumerate(user_agents)
        if filter_user_agents(raw_user_agent, filters)
    ]

    return make_cumulative_weight_index_pairs(weight_index_pairs)


with open(
    file=str(
        pathlib.Path(__file__).parent.resolve().joinpath("data/user-agents.json")
    ),
    mode="r",
    encoding="utf-8",
) as f:
    user_agents = json.load(f)

# Precompute these so that we can quickly generate unfiltered user agents.
default_weight_index_pairs = [
    (agent["weight"], index) for index, agent in enumerate(user_agents)
]
default_cumulative_weight_index_pairs = make_cumulative_weight_index_pairs(
    default_weight_index_pairs
)

UserAgentData = Dict[str, Any]
NestedValueOf = Union[str, Dict[str, Any]]
Filter = Union[Callable[[Any], bool], re.Pattern, List[Any], Dict[str, Any], str]


class UserAgent:
    def __init__(self, filters=None):
        if not isinstance(filters, dict):
            filters = {"userAgent": filters}

        self.cumulative_weight_index_pairs = (
            construct_cumulative_weight_index_pairs_from_filters(filters)
        )

        if not self.cumulative_weight_index_pairs:
            raise ValueError("No user agents matched your filters.")

        self.randomize()

    def __str__(self):
        return self.data["userAgent"]

    def __call__(self):
        return self.random()

    def __len__(self):
        return len(self.data["userAgent"])

    def __repr__(self):
        return self.__str__()

    def random(self):
        self.randomize()
        return self

    def randomize(self):
        # Find a random raw random user agent.
        random_number = random.random()
        index = next(
            index
            for cumulative_weight, index in self.cumulative_weight_index_pairs
            if cumulative_weight > random_number
        )
        self.data = user_agents[index]

    @staticmethod
    def random_user_agent(filters=None):
        try:
            return UserAgent(filters)
        except ValueError:
            return None

# TODO rename user-agents-python to py3-user-agents
# TODO download update_data

# pylint: disable=line-too-long

import re
import random
import json
from typing import Callable, List, Any, Union, Dict


# Inspired from Intoli user-agents : https://github.com/intoli/user-agents/blob/main/src/user-agent.ts

# Load the user agents data from a JSON file
with open(file="data/user-agents.json", mode="r", encoding="utf-8") as f:
    user_agents = json.load(f)


# Normalizes the total weight to 1 and constructs a cumulative distribution.
def make_cumulative_weight_index_pairs(weight_index_pairs):
    total_weight = sum(weight for weight, _ in weight_index_pairs)
    cumulative_sum = 0
    cumulative_weight_index_pairs = []
    for weight, index in weight_index_pairs:
        cumulative_sum += weight / total_weight
        cumulative_weight_index_pairs.append((cumulative_sum, index))
    return cumulative_weight_index_pairs


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

"""
def construct_filter(
    filters: Filter,
    accessor: Callable[[Any], Any] = lambda parent_object: parent_object,
) -> Callable[[Any], bool]:
    # Example usage:
    # filter_func = construct_filter({'browser': {'name': 'Chrome'}})
    # result = filter_func({'browser': {'name': 'Chrome', 'version': '91.0'}})
    # print(result)  # True

    def create_regex_filter(regex: re.Pattern) -> Callable[[Any], bool]:
        def regex_filter(value: Any) -> bool:
            if isinstance(value, dict) and "userAgent" in value:
                return bool(regex.search(value["userAgent"]))
            return bool(regex.search(str(value)))

        return regex_filter

    def create_equality_filter(target: Any) -> Callable[[Any], bool]:
        def equality_filter(value: Any) -> bool:
            if isinstance(value, dict) and "userAgent" in value:
                return target == value["userAgent"]
            return target == value

        return equality_filter

    if callable(filters):
        child_filters = [filters]
    elif isinstance(filters, re.Pattern):
        child_filters = [create_regex_filter(filters)]
    elif isinstance(filters, list):
        child_filters = [construct_filter(child_filter) for child_filter in filters]
    elif isinstance(filters, dict):
        child_filters = [
            construct_filter(value_filter, lambda parent_object: parent_object.get(key))
            for key, value_filter in filters.items()
        ]
    else:
        child_filters = [create_equality_filter(filters)]

    def filter_function(parent_object: Any) -> bool:
        try:
            value = accessor(parent_object)
            return all(child_filter(value) for child_filter in child_filters)
        except Exception:
            # This happens when a user-agent lacks a nested property.
            return False

    return filter_function
"""

"""
UserAgentData = Dict[str, Any]
Filter = Union[
    Callable[[UserAgentData], bool], str, re.Pattern, List[Any], Dict[str, Any]
]


# Construct a filter function that acts on raw user agents.
def construct_filter(
    filters: Union[
        Callable[[Any], bool],
        re.Pattern,
        List[Union[Callable[[Any], bool], re.Pattern]],
        Dict[str, Union[Callable[[Any], bool], re.Pattern]],
    ],
    accessor: Callable[[Any], Any] = lambda parent_object: parent_object,
) -> Callable[[Any], bool]:
    child_filters: List[Callable[[Any], bool]]

    if callable(filters):
        child_filters = [filters]
    elif isinstance(filters, re.Pattern):
        child_filters = [
            lambda value: isinstance(value, dict)
            and "userAgent" in value
            and value["userAgent"]
            and filters.match(value["userAgent"])
            or filters.match(str(value))
        ]
    elif isinstance(filters, list):
        child_filters = [construct_filter(child_filter) for child_filter in filters]
    elif isinstance(filters, dict):
        child_filters = [
            construct_filter(value_filter, lambda parent_object: parent_object[key])
            for key, value_filter in filters.items()
        ]
    else:
        child_filters = [
            lambda value: isinstance(value, dict)
            and "userAgent" in value
            and value["userAgent"]
            and filters == value["userAgent"]
            or filters == value
        ]

    return lambda parent_object: all(
        child_filter(accessor(parent_object)) for child_filter in child_filters
    )
"""


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
        user_agent = UserAgent()
        user_agent.cumulative_weight_index_pairs = self.cumulative_weight_index_pairs
        user_agent.randomize()
        return user_agent

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

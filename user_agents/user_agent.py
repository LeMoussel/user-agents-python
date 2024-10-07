import random
from copy import deepcopy
import json

# Inspired from Intoli user-agents : https://github.com/intoli/user-agents/blob/main/src/user-agent.ts

# Load the user agents data from a JSON file
with open(
    file='data/user-agents.json',
    mode='r',
    encoding='utf-8'
) as f:
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
default_weight_index_pairs = [(agent['weight'], index) for index, agent in enumerate(user_agents)]
default_cumulative_weight_index_pairs = make_cumulative_weight_index_pairs(default_weight_index_pairs)


# Turn the various filter formats into a single filter function that acts on raw user agents.
def construct_filter(filters, accessor=lambda x: x):
    if callable(filters):
        child_filters = [filters]
    elif isinstance(filters, str):
        child_filters = [lambda value: filters == value.get('userAgent', '') if isinstance(value, dict) else filters == value]
    elif isinstance(filters, list):
        child_filters = [construct_filter(f) for f in filters]
    elif isinstance(filters, dict):
        child_filters = [construct_filter(value_filter, accessor=lambda obj, key=key: obj.get(key))
                         for key, value_filter in filters.items()]
    else:
        child_filters = [lambda value: filters == value.get('userAgent', '') if isinstance(value, dict) else filters == value]

    def filter_fn(parent_object):
        try:
            value = accessor(parent_object)
            return all(child_filter(value) for child_filter in child_filters)
        except (KeyError, AttributeError, TypeError):
            # This happens when a user-agent lacks a nested property.
            return False

    return filter_fn


# Construct normalized cumulative weight index pairs given the filters.
def construct_cumulative_weight_index_pairs_from_filters(filters):
    if not filters:
        return default_cumulative_weight_index_pairs

    filter_fn = construct_filter(filters)
    weight_index_pairs = [
        (raw_user_agent['weight'], index)
        for index, raw_user_agent in enumerate(user_agents)
        if filter_fn(raw_user_agent)
    ]

    return make_cumulative_weight_index_pairs(weight_index_pairs)


class UserAgent:
    def __init__(self, filters=None):
        self.cumulative_weight_index_pairs = construct_cumulative_weight_index_pairs_from_filters(filters)

        if not self.cumulative_weight_index_pairs:
            raise ValueError('No user agents matched your filters.')

        self.randomize()

    def __str__(self):
        return self.data['userAgent']

    def __call__(self):
        return self.random()

    def __len__(self):
        return len(self.data['userAgent'])

    def random(self):
        user_agent = UserAgent()
        user_agent.cumulative_weight_index_pairs = self.cumulative_weight_index_pairs
        user_agent.randomize()
        return user_agent

    def randomize(self):
        # Find a random raw random user agent.
        random_number = random.random()
        index = next(
            index for cumulative_weight, index in self.cumulative_weight_index_pairs
            if cumulative_weight > random_number
        )
        raw_user_agent = user_agents[index]
        self.data = deepcopy(raw_user_agent)

    @staticmethod
    def random_user_agent(filters=None):
        try:
            return UserAgent(filters)
        except ValueError:
            return None

    def __repr__(self):
        return self.__str__()




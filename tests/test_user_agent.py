# pylint: disable=missing-docstring

import re
import unittest
from user_agents.user_agent import UserAgent

range_iterations = range(1000)


class TestUserAgent(unittest.TestCase):
    def test_user_agent(self):
        user_agent = UserAgent()
        self.assertGreater(len(user_agent), 0)

    def test_support_object_properties(self):
        for _ in range_iterations:
            user_agent = UserAgent({"deviceCategory": "tablet"})
            self.assertEqual(user_agent.data["deviceCategory"], "tablet")

    def test_support_nested_object_properties(self):
        for _ in range_iterations:
            user_agent = UserAgent({"connection": {"effectiveType": "4g"}})
            self.assertEqual(user_agent.data["connection"]["effectiveType"], "4g")

    def test_support_multiple_object_properties(self):
        for _ in range_iterations:
            user_agent = UserAgent({"deviceCategory": "mobile", "pluginsLength": 0})
            self.assertEqual(user_agent.data["deviceCategory"], "mobile")
            self.assertEqual(user_agent.data["pluginsLength"], 0)

    def test_support_top_level_regular_expressions(self):
        for _ in range_iterations:
            user_agent = UserAgent(re.compile("Safari"))
            self.assertRegex(user_agent.data["userAgent"], "Safari")

    def test_support_object_property_regular_expressions(self):
        for _ in range_iterations:
            user_agent = UserAgent({"userAgent": re.compile("Safari")})
            self.assertRegex(user_agent.data["userAgent"], "Safari")

    def test_support_top_level_arrays(self):
        user_agent = UserAgent([re.compile("Android"), re.compile("Linux")])
        for _ in range_iterations:
            random_user_agent = user_agent()
            self.assertRegex(random_user_agent.data["userAgent"], "Android")
            self.assertRegex(random_user_agent.data["userAgent"], "Linux")

    def test_support_object_property_arrays(self):
        for _ in range_iterations:
            user_agent = UserAgent(
                {"deviceCategory": [re.compile(r"(tablet|mobile)"), "mobile"]}
            )
            self.assertEqual(user_agent.data["deviceCategory"], "mobile")

    def test_constructor_throws_error_when_no_filters_match(self):
        with self.assertRaises(ValueError):
            UserAgent({"deviceCategory": "fake-no-matches"})

    def test_static_random_returns_null_when_no_filters_match(self):
        self.assertIsNone(
            UserAgent.random_user_agent({"deviceCategory": "fake-no-matches"})
        )

    def test_static_random_returns_valid_user_agent_when_filter_matches(self):
        user_agent = UserAgent.random_user_agent({"userAgent": re.compile("Chrome")})
        self.assertIsNotNone(user_agent)
        self.assertIn("Chrome", str(user_agent))
        self.assertRegex(user_agent.data["userAgent"], "Chrome")

    def test_call_handler_produces_new_user_agents_that_pass_same_filters(self):
        for _ in range_iterations:
            user_agent = UserAgent.random_user_agent({"userAgent": re.compile("Chrome")})
            self.assertRegex(user_agent.data["userAgent"], "Chrome")

    def test_cumulative_weight_index_pairs_length_greater_than_100(self):
        user_agent = UserAgent()
        self.assertGreater(len(user_agent.cumulative_weight_index_pairs), 100)

    def test_cumulative_weight_index_pairs_shorter_length_when_filter_applied(self):
        user_agent = UserAgent()
        filtered_user_agent = UserAgent({"deviceCategory": "mobile"})
        self.assertGreater(
            len(user_agent.cumulative_weight_index_pairs),
            len(filtered_user_agent.cumulative_weight_index_pairs),
        )


if __name__ == "__main__":
    unittest.main()

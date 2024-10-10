import unittest


from user_agents.user_agent import UserAgent

# The randomization tests will be repeated once for each element in the range.
# We should add a more sophisticated RNG with seeding support for additional testing.
# range_ = [None] * 1000


class TestUserAgent(unittest.TestCase):
    def test_user_agent(self):
        user_agent = UserAgent()
        self.assertGreater(len(user_agent), 0)


if __name__ == "__main__":
    unittest.main()

    # TODO rename user-agents-python to py3-user-agents
    # TODO download update_data

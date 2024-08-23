import unittest
import skills.semantic_networks.gpp_solving_functions as gpp_solving_functions

class TestFindPathBetweenTwoStates(unittest.TestCase):

    def test_find_path(self):
        start_state = [3, 0, 3, 0, 0]
        goal_state = [2, 1, 2, 1, 1]
        expected_path = [('start', [3, 0, 3, 0, 0]), ('move_1_guard_1_prisoner', [2, 1, 2, 1, 1])]
        result = gpp_solving_functions.find_path_between_two_states(start_state, goal_state)
        self.assertEqual(result, expected_path)

    def test_find_path_full(self):
        start_state = [3, 0, 3, 0, 0]
        goal_state = [0, 3, 0, 3, 1]
        expected_path = [('start', [3, 0, 3, 0, 0]), ('move_2_prisoners', [3, 0, 1, 2, 1]),
                         ('move_1_prisoner', [3, 0, 2, 1, 0]), ('move_2_prisoners', [3, 0, 0, 3, 1]),
                         ('move_1_prisoner', [3, 0, 1, 2, 0]), ('move_2_guards', [1, 2, 1, 2, 1]),
                         ('move_1_guard_1_prisoner', [2, 1, 2, 1, 0]), ('move_2_guards', [0, 3, 2, 1, 1]),
                         ('move_1_prisoner', [0, 3, 3, 0, 0]), ('move_2_prisoners', [0, 3, 1, 2, 1]),
                         ('move_1_guard', [1, 2, 1, 2, 0]), ('move_1_guard_1_prisoner', [0, 3, 0, 3, 1])]

        result = gpp_solving_functions.find_path_between_two_states(start_state, goal_state)
        self.assertEqual(result, expected_path)
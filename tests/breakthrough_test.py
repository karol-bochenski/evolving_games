import unittest
import numpy
import breakthrough
from mcts import mcts

class BreakthroughTest(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_game(self):
        state = breakthrough.game.initialState()
        state = mcts.findNextMove(state).game_state
        state = mcts.findNextMove(state)
        state = mcts.findNextMove(state.game_state).game_state
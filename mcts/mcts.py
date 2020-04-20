import random
import sys
import math
import time

class UCTNode():
    def __init__(self, game_state, parent=None):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.total_value = 0
        self.number_visits = 0

    def best_move(self):
        return max(self.children,
                key=lambda node: node.number_visits)

    def uctValue(self):
            if self.number_visits == 0:
                return sys.maxsize
            return ((self.total_value * 1.0) / self.number_visits) + (1.41 * math.sqrt(math.log(self.parent.number_visits) / self.number_visits))

    def best_child(self):
        return max(self.children,
                key=lambda node: node.uctValue())

    def select_leaf(self):
        current = self
        while len(current.children) != 0:
            current = current.best_child()
        return current

    def simulateRandomPlayout(self, player):
        if(self.game_state.winner == ~player):
            self.parent.total_value = -999999
            return self.game_state.winner
        game_state = self.game_state.copy()
        while not game_state.finished:
            game_state._possibleMoves = None
            moves = game_state.possibleMoves
            moveInfo = random.choice(moves)
            game_state = game_state.applyMove_(moveInfo)
        return game_state.winner

    def expand_node(self):
        for state in self.game_state.possibleStates:
            newNode = UCTNode(state, parent=self)
            self.children.append(newNode)

    def backup(self, winner, player):
        current = self
        while current is not None:
            current.number_visits += 1
            if winner == player:
                current.total_value += 1
            current = current.parent

def findNextMove(state):
    rootNode = UCTNode(state)
    t_end = time.time() + 1
    n = 0
    while time.time() < t_end:
        promisingNode = rootNode.select_leaf()
        if promisingNode.game_state.finished == False :
            promisingNode.expand_node()
        nodeToExplore = promisingNode
        if len(promisingNode.children) > 0:
            nodeToExplore = random.choice(promisingNode.children)

        winner = nodeToExplore.simulateRandomPlayout(state.currentPlayer)
        nodeToExplore.backup(winner, state.currentPlayer)
        n += 1
    winnerNode = rootNode.best_move()
    return winnerNode
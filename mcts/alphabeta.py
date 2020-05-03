from game_elements.player import Player
from game_definitions.heuristicValueEvaluator import HeuristicCalculator

class AlphaBeta:
    def __init__(self, game):
        self.heuristicCalc = HeuristicCalculator(game)

    def findBestMove(self, game_state):
        maximizePlayer1 = game_state.currentPlayer == Player.P1
        return self.alphaBeta(game_state, maximizePlayer1, -5000, 5000, 3)[1]

    def alphaBeta(self, game_state, ismin, alpha, beta, depth):
        if (depth == 0):
            value = self.heuristicCalc.calculate(game_state) 
            return value[1] - value[0],game_state
        if(game_state.winner is not None):
            return (2000,game_state) if (game_state.winner == Player.P2) else (-2000, game_state)
        retstate = None
        if(ismin):
            mval = 999999
            for state in game_state.possibleStates:
                beta, _ = self.alphaBeta(state, True, alpha, beta, depth - 1)
                if(beta < mval):
                    mval = beta
                    retstate = state
                if(alpha >= beta):
                    break
            return beta, retstate
        else:
            mval = -999999
            for state in game_state.possibleStates:
                alpha, _ = self.alphaBeta(state, False, alpha, beta, depth - 1)
                if(alpha > mval):
                    mval = alpha
                    retstate = state
                if(alpha >= beta):
                    break
            return alpha, retstate


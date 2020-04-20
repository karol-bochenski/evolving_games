from game_elements.player import Player

class AlphaBeta:
    def __init__(self):
        self.traversed_states = {}

    def findBestMove(self, game_state):
        return self.alphaBeta(game_state, False, -2, 2, 8)

    def alphaBeta(self, game_state, ismin, alpha, beta, depth):
        if (depth == 0):
            return 0,game_state
        if(game_state.winner is not None):
            return (1,game_state) if (game_state.winner == Player.P2) else (-1, game_state)
        retstate = None
        if(ismin):
            mval = 2
            for state in game_state.possibleStates:
                if (state,ismin) in self.traversed_states:
                    beta = self.traversed_states[(state, ismin)]
                else:
                    beta, _ = self.alphaBeta(state, True, alpha, beta, depth - 1)
                    self.traversed_states[(state, ismin)] = beta
                if(beta < mval):
                    mval = beta
                    retstate = state
                if(alpha >= beta):
                    break
            return beta, retstate
        else:
            mval = -2
            for state in game_state.possibleStates:
                if (state,ismin) in self.traversed_states:
                    alpha = self.traversed_states[(state, ismin)]
                else:
                    alpha, _ = self.alphaBeta(state, False, alpha, beta, depth - 1)
                    self.traversed_states[(state, ismin)] = alpha
                if(alpha > mval):
                    mval = alpha
                    retstate = state
                if(alpha >= beta):
                    break
            return alpha, retstate


from game_definitions.boardGame import BoardGame, GameState
from game_elements.player import Player
from game_definitions.moves import Hop, Leap, Slide, Move 
from game_definitions.win_conditions import And,Or,EnemyPieceTypeRemoved,EnemyTotalPiecesLeft,PieceIsPlacedAt

class HeuristicCalculator:

    moveTypeValues = {
        Hop : lambda hop: 1 if hop.can_attack else 0.25,
        Leap : lambda _ : 1.5,
        Slide : lambda _ : 2.25
    }

    def __init__(self, game:BoardGame):
        self.game = game
        self.modifiers = [1,1,1]
        self.pieceTypesEvaluated = self.evaluateGamePieces(game.piece_types[Player.P1][1:])
        self.maxDistance = game.initialBoard.width + game.initialBoard.height
        self.conditionEvaluator = {
            Player.P1 : self.prepareWinConditionCalculation(game.winConditions[Player.P1]),
            Player.P2 : self.prepareWinConditionCalculation(game.winConditions[Player.P2])
        }

    def prepareWinConditionCalculation(self, condition):
        conditionType = type(condition)
        evaluator = None
        if conditionType == And:
            evaluator = self.prepareAnd(condition)
        elif conditionType == Or:
            evaluator = self.prepareOr(condition)
        elif conditionType == PieceIsPlacedAt:
            evaluator = self.preparePlacedAt(condition)
        elif conditionType == EnemyPieceTypeRemoved:
            evaluator = self.prepareTypeRemoved(condition)
        elif conditionType == EnemyTotalPiecesLeft:
            evaluator = self.prepareTotalLeft(condition)
        return evaluator
    
    def prepareAnd(self, condition:And):
        evaluator1 = self.prepareWinConditionCalculation(condition.conditionA)
        evaluator2 = self.prepareWinConditionCalculation(condition.conditionB)
        def evaluate(game_state):
            return (evaluator1(game_state) + evaluator2(game_state)) / 2
        return evaluate

    def prepareOr(self, condition:Or):
        evaluator1 = self.prepareWinConditionCalculation(condition.conditionA)
        evaluator2 = self.prepareWinConditionCalculation(condition.conditionB)
        def evaluate(game_state):
            return min(evaluator1(game_state),evaluator2(game_state))
        return evaluate

    def preparePlacedAt(self, condition:PieceIsPlacedAt):
        target_squares = condition.target_squares
        def evaluate(game_state):
            squares = game_state.getPiecesForPlayer(condition.player)
            minDistance = 999999
            for square in squares:
                for targetSquare in target_squares:
                    x,y = square.coords.x - targetSquare[0], square.coords.y - targetSquare[1]
                    distance = abs(x) + abs(y)
                    if(distance < minDistance):
                        minDistance = distance
            return ((self.maxDistance - minDistance) / self.maxDistance) * 100
        return evaluate

    def prepareTypeRemoved(self, condition: EnemyPieceTypeRemoved):
        totalNumber = len([square for square in self.game.initialBoard.iterate() if square.owner == ~condition.player and square.piece == condition.pieceId])
        def evaluate(game_state):
            squares = len([square for square in game_state.getPiecesForPlayer(~condition.player) if square.pieceId == condition.pieceId])
            return ((totalNumber - squares) / totalNumber) * 100
        return evaluate

    def prepareTotalLeft(self, condition: EnemyTotalPiecesLeft):
        totalNumber = len([square for square in self.game.initialBoard.iterate() if square.owner == ~condition.player])
        totalNumber -= condition.totalLeft
        def evaluate(game_state):
            currentNumber = len(game_state.getPiecesForPlayer(~condition.player)) - condition.totalLeft
            return ((totalNumber - currentNumber) / totalNumber) * 100
        return evaluate

    def evaluateGamePieces(self, pieces):
        piecesValues = {}
        for i, piece in enumerate(pieces):
            pieceValue = 0
            duplicates = set()
            for move in piece.moveset:
                if (type(move),move.direction) in duplicates or (type(move),move.direction.inverted()) in duplicates:
                    continue
                duplicates.add((type(move), move.direction))
                pieceValue += self.evaluateMove(move)
            piecesValues[i + 1] = pieceValue
        return piecesValues

    def evaluateMove(self, move:Move):
        baseValue = self.moveTypeValues[type(move)](move)
        directionBonus = 0
        conditionMultiplicator = 1
        forward = move.direction.y
        if forward > 0:
            directionBonus += 0.75 + forward / 4
        sideways = move.direction.x
        if sideways > 0:
            directionBonus += 0.5 + sideways / 4
        if move.condition:
            conditionMultiplicator = 0.8
        return (baseValue + directionBonus) * conditionMultiplicator
        
    def evaluateCurrentMobility(self, game_state, player):
        squares = game_state.getPiecesForPlayer(player)
        mobilitySum = 0
        for square in squares:
            baseValue = self.pieceTypesEvaluated[square.piece]
            mobility = len(square.getLegalMoves())
            mobilitySum += baseValue * mobility
        return mobilitySum

    def evaluateBoardStrength(self, game_state, player):
        value = 0
        for square in game_state.getPiecesForPlayer(player):
            value += self.pieceTypesEvaluated[square.piece]
        return value

    def calculatePlayer(self, game_state, player):
        strength = self.evaluateBoardStrength(game_state, player)
        mobility = self.evaluateCurrentMobility(game_state, player)
        conditions = self.conditionEvaluator[player](game_state)
        return ((strength * self.modifiers[0]) + \
               (mobility * self.modifiers[1]) + \
               (conditions * self.modifiers[2])) / sum(self.modifiers)

    def calculate(self, game_state:GameState):
        player1value = self.calculatePlayer(game_state, Player.P1)
        player2value = self.calculatePlayer(game_state, Player.P2)
        return [player1value, player2value]
import yaml
from game_definitions.boardGame import BoardGame

def fromFile(filePath):
    with open(filePath, "r") as gameStr:
        game = BoardGame.fromDict(yaml.safe_load(gameStr))
    return game

def toFile(boardGame, filePath):
    with open(filePath, "w") as gameFile:
        yaml.safe_dump(boardGame.toDict(), gameFile)
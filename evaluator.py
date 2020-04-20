

def pieceTraverse(moveset, startingPosition, board):
    reachableSquares = [move.direction for move in moveset]
    visited = {startingPosition}
    queue = [ (startingPosition + destination) for destination in reachableSquares if board.contains(startingPosition + destination)]
    print(queue)
    while queue:
        currentSquare = queue.pop()
        visited.add(currentSquare)
        for destination in [currentSquare + reach for reach in reachableSquares if board.contains(currentSquare + reach)]:
            if destination in visited:
                continue
            queue.append(destination)
    return visited
    
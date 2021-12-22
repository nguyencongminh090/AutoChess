import chess.engine
from chess.engine import Cp, Mate, MateGiven

engine = chess.engine.SimpleEngine.popen_uci('stockfish.exe')

board = chess.Board()
while not board.is_game_over():
    result = engine.play(board, chess.engine.Limit(time=0.1), info=chess.engine.INFO_SCORE)
    result.info['score'].white().is_mate()
    print(result.info['score'].white().score(mate_score=100000))
    board.push(result.move)

engine.quit()

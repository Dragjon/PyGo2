from evaluation import *
import chess
import time

def mvv_lva(board, move):

    captured_piece = board.piece_at(move.to_square)
    attacking_piece = board.piece_at(move.from_square)

    if captured_piece is not None and attacking_piece is not None:
        return (piece_values[captured_piece.piece_type] - piece_values[attacking_piece.piece_type])
    elif  board.is_castling(move):
        return 20
    elif board.gives_check(move):
        return 10
    else:
        return 0  # No capture, castling, or check return 0

def quiescence(board, alpha, beta, color, nodes):
    if board.can_claim_draw() or board.is_stalemate() or board.is_insufficient_material():
        return 0, nodes
    
    if board.is_checkmate():
        return -30000 + int(board.ply()), nodes

    stand_pat = color * evaluate_board(board)

    if stand_pat >= beta:
        return beta, nodes

    if alpha < stand_pat:
        alpha = stand_pat

    # Sort captures using MVV-LVA heuristic
    captures = sorted(
        (move for move in board.legal_moves if board.is_capture(move)),
        key=lambda move: mvv_lva(board, move),
        reverse=True
    )

    for move in captures:
        board.push(move)
        nodes += 1
        score, nodes = quiescence(board, -beta, -alpha, -color, nodes)
        score = -score
        board.pop()

        if score >= beta:
            return beta, nodes

        if score > alpha:
            alpha = score

    return alpha, nodes



transposition_table = {}  # Global transposition table

def store_transposition(board, depth, score, flag):
    key = (board.fen(), depth)  # Use board.fen() to obtain a hashable representation
    transposition_table[key] = {'score': score, 'flag': flag}

def lookup_transposition(board, depth, alpha, beta):
    key = (board.fen(), depth)  # Use board.fen() to obtain a hashable representation
    if key in transposition_table:
        entry = transposition_table[key]
        if entry['flag'] == 'exact':
            return entry['score']
        elif entry['flag'] == 'lowerbound':
            alpha = max(alpha, entry['score'])
        elif entry['flag'] == 'upperbound':
            beta = min(beta, entry['score'])
        if alpha >= beta:
            return entry['score']
    return None

def negamax(board, depth, alpha, beta, color, nodes):
    transposition_result = lookup_transposition(board, depth, alpha, beta)
    if transposition_result is not None:
        return transposition_result, nodes
    
    if board.can_claim_draw() or board.is_stalemate() or board.is_insufficient_material():
        return 0, nodes
    
    if board.is_checkmate():
        return -30000 + int(board.ply()), nodes

    if depth == 0:
        score, nodes = quiescence(board, alpha, beta, color, nodes)
        store_transposition(board, depth, score, 'exact')
        return score, nodes

    max_score = float('-inf')

    # Sort moves using MVV-LVA heuristic
    moves = sorted(board.legal_moves, key=lambda move: mvv_lva(board, move), reverse=True)

    for move in moves:
        board.push(move)
        nodes += 1
        score, nodes = negamax(board, depth - 1, -beta, -alpha, -color, nodes)
        score = -score
        board.pop()

        if score > max_score:
            max_score = score

        alpha = max(alpha, max_score)

        if alpha >= beta:
            store_transposition(board, depth, max_score, 'lowerbound')
            break 

    store_transposition(board, depth, max_score, 'exact')
    return max_score, nodes


def get_best_move(board, depth):
    best_move = None
    max_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    nodes = 0

    if board.turn == chess.WHITE:
        color = 1
    else:
        color = -1

    # Sort moves using MVV-LVA heuristic
    moves = sorted(board.legal_moves, key=lambda move: mvv_lva(board, move), reverse=True)

    for move in moves:
        board.push(move)
        nodes += 1
        if board.is_checkmate():
            board.pop()
            return move, 30000 - int(board.ply()), nodes

        score, nodes = negamax(board, depth - 1, -beta, -alpha, -color, nodes)
        score = -score
        board.pop()

        if score > max_score:
            max_score = score
            best_move = move

        alpha = max(alpha, max_score)

        if alpha >= beta:
            break 

    return best_move, max_score, nodes



def play_game():
    board = chess.Board()
    eval = 0
    nodes = 0
    elapsed_time = 0
    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            move = input("Your move: ")
            board.push(chess.Move.from_uci(move))
        else:
            # AI move using negamax
            depth = 3
            start_time = time.time()
            best_move, eval, nodes = get_best_move(board, depth)
            elapsed_time = time.time() - start_time
            board.push(best_move)
            print(f"Depth: {depth}")
            print(f"Eval: {eval}")
            print(f"Nodes: {nodes}")
            print(f"Time ms {int(elapsed_time*1000)}")
            if elapsed_time != 0:
                print(f"NPS: {int(nodes/elapsed_time)}")
            else:
                print("NPS: 0\n")
            print(f"Bestmove: {best_move}\n")

    print("Game Over")
    print("Result: ", board.result())

if __name__ == "__main__":
    play_game()

#board = chess.Board(fen="k2r4/5pb1/1R1p1p1p/3Pp3/4P1P1/3n1N1P/5P2/1R4K1 w - - 1 35")
#print(board.ply())
    
#import cProfile

#if __name__ == "__main__":
 #   cProfile.run('play_game()')

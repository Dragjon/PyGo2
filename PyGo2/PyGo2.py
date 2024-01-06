from evaluation import *
import chess
import chess.polyglot
import time
import threading
import msvcrt

INFINITY = 30000
NEGATIVEINFINITY = -30000

def mvv_lva(board, move):

    captured_piece = board.piece_at(move.to_square)
    attacking_piece = board.piece_at(move.from_square)

    if captured_piece is not None and attacking_piece is not None:
        return (piece_values_mid[captured_piece.piece_type] - piece_values_mid[attacking_piece.piece_type])
    elif  board.is_castling(move):
        return 20
    elif board.gives_check(move):
        return 10
    else:
        return 0  # No capture, castling, or check return 0
    
# Transposition table
TABLE_SIZE = 2**20  # Choose a suitable size for the table
transposition_table = [{} for _ in range(TABLE_SIZE)]

def store_transposition(board, depth, score, node_type):
    zobrist_key = chess.polyglot.zobrist_hash(board)
    index = zobrist_key % TABLE_SIZE
    
    if zobrist_key in transposition_table[index]:
        # Handle collision using separate chaining
        transposition_table[index][zobrist_key].append((depth, score, node_type))
    else:
        transposition_table[index][zobrist_key] = [(depth, score, node_type)]

def probe_transposition(board, depth):
    zobrist_key = chess.polyglot.zobrist_hash(board)
    index = zobrist_key % TABLE_SIZE
    
    if zobrist_key in transposition_table[index]:
        entries = transposition_table[index][zobrist_key]
        for entry in entries:
            if entry[0] >= depth:
                return entry
    return None

extensions = 0
max_extensions = 5

def negamax(board, depth, start_depth, start_time, alpha, beta, color, nodes, safety_threshold=200):

    global extensions
    global max_extensions

    # Usage in your code
    tt_entry = probe_transposition(board, depth)
    if tt_entry is not None:
        depth_in_tt, score_in_tt, node_type_in_tt = tt_entry

        if node_type_in_tt == 'exact':
            return score_in_tt, nodes

        if node_type_in_tt == 'lowerbound' and score_in_tt > alpha:
            alpha = score_in_tt

        elif node_type_in_tt == 'upperbound' and score_in_tt < beta:
            beta = score_in_tt

        if alpha >= beta:
            return score_in_tt, nodes

    if board.can_claim_draw() or board.is_stalemate() or board.is_insufficient_material():
        return 0-contempt, nodes
    
    if board.is_checkmate():
        return -30000 + int(board.ply()), nodes

    if depth == 0:
        score = color * evaluate_board(board)
        return score, nodes

    max_score = NEGATIVEINFINITY

    # Sort moves using MVV-LVA heuristic
    moves = sorted(board.legal_moves, key=lambda move: mvv_lva(board, move), reverse=True)

    for move in moves:
        elapsed_time = time.time() - start_time
        board.push(move)
        nodes += 1

        if extensions <= max_extensions:
            if board.is_check():
                extensions += 1
                score, nodes = negamax(board, depth, start_depth, start_time, -beta, -alpha, -color, nodes)
            elif board.is_capture(move):
                extensions += 1
                score, nodes = negamax(board, depth, start_depth, start_time, -beta, -alpha, -color, nodes)
            
        else:
            score, nodes = negamax(board, depth - 1, start_depth, start_time, -beta, -alpha, -color, nodes)

        score = -score

        board.pop()

        if score > max_score:
            max_score = score
            node_type = 'exact' if max_score > alpha and max_score < beta else ('lowerbound' if max_score <= alpha else 'upperbound')
            if depth >= start_depth:
                print(f"info depth {depth} score cp {-int(max_score)} {node_type} nodes {int(nodes)} nps {int(nodes/max(0.01, elapsed_time))} time {int(elapsed_time*1000)}")


        alpha = max(alpha, max_score)

        if alpha >= beta:
            break
        
        node_type = 'exact' if max_score > alpha and max_score < beta else ('lowerbound' if max_score <= alpha else 'upperbound')
        store_transposition(board, depth, max_score, node_type)

        if depth >= start_depth:
            print(f"info depth {depth} score cp {int(max_score)} {node_type} nodes {int(nodes)} nps {int(nodes/max(0.01, elapsed_time))} time {int(elapsed_time*1000)}")

    return max_score, nodes

# Event to signal when to stop the search
stop_event = threading.Event()

def best_move(board, start_time, max_time, depth):
    global stop_event
    if board.turn == chess.WHITE:
        color = 1
    else:
        color = -1

    alpha = NEGATIVEINFINITY
    beta = INFINITY
    max_score = NEGATIVEINFINITY
    nodes = 0

    if use_opening_book:
        # Try moves from the opening book first
        with chess.polyglot.open_reader(opening_book_path) as reader:
            for entry in reader.find_all(board):
                move = entry.move
                if move in board.legal_moves:
                    return move  # Return a move from the opening book

    best_mv = None

    # Start a thread for user input
    input_thread = threading.Thread(target=check_input)
    input_thread.start()

    for current_depth in range(1, depth + 1):

        ordered_moves = sorted(board.legal_moves, key=lambda move: mvv_lva(board, move), reverse=True)

        if len(ordered_moves) == 1:
            return ordered_moves[0]

        for move in ordered_moves:
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time or stop_event.is_set():
                stop_event.set()  # Set the event to signal the stop
                input_thread.join()  # Wait for the input thread to finish
                return best_mv

            board.push(move)
            nodes += 1
            if board.is_checkmate():
                board.pop()
                return move

            if board.is_check():
                score, nodes = negamax(board, current_depth, current_depth, start_time, -beta, -alpha, -color, nodes)

            elif board.is_capture(move):
                score, nodes = negamax(board, current_depth, current_depth, start_time, -beta, -alpha, -color, nodes)
            else:
                score, nodes = negamax(board, current_depth - 1, current_depth, start_time, -beta, -alpha, -color, nodes)
            score = -score
            board.pop()

            if score > max_score:
                max_score = score
                best_mv = move

            alpha = max(alpha, max_score)

            if alpha >= beta:
                break

            node_type = 'exact' if max_score > alpha and max_score < beta else ('lowerbound' if max_score <= alpha else 'upperbound')
            print(f"info depth {current_depth} score cp {int(max_score)} {node_type} nodes {int(nodes)} nps {int(nodes/max(0.01, elapsed_time))} time {int(elapsed_time*1000)} pv {best_mv}")

    stop_event.set()  # Set the event to signal the stop
    input_thread.join()  # Wait for the input thread to finish
    return best_mv

def check_input():
    global stop_event
    while not stop_event.is_set():
        if msvcrt.kbhit():
            user_input = msvcrt.getch().decode('utf-8')
            if user_input.lower() == "stop":
                stop_event.set()

def calculateMaxTime(remaining_time):
    return remaining_time / 30

def parse_parameters(line):
    DEFAULT_WTIME = 1000000
    DEFAULT_BTIME = 1000000
    parameters = line.split()[1:]
    wtime, btime = DEFAULT_WTIME, DEFAULT_BTIME
    default_movetime = None
    movetime = default_movetime

    for i in range(len(parameters)):
        if parameters[i] == "infinite":
            wtime = float('inf')
            btime = float('inf')
        elif parameters[i] == "wtime" and i + 1 < len(parameters):
            wtime = float(parameters[i + 1])
        elif parameters[i] == "btime" and i + 1 < len(parameters):
            btime = float(parameters[i + 1])
        elif parameters[i] == "movetime" and i + 1 < len(parameters):
            movetime = float(parameters[i + 1])

    return wtime, btime, movetime

opening_book_path = 'C:\\Users\\dragon\\Desktop\\PyGo2\\book\\komodo.bin'
contempt = 0
use_opening_book = True

def play_chess():
    global contempt
    global opening_book_path
    global use_opening_book
    global stop_event
    global extensions

    board = chess.Board()
    remaining_time = 1000000

    while True:
        line = input()
        if line == "uci":
            print("id name PyGo V2")
            print("id author Chess123easy")
            print(f"option name Book_Path type string default {opening_book_path}")
            print(f"option name Contempt type spin default {contempt} min -100 max 100")
            print(f"option name Use_Opening_Book type check default {int(use_opening_book)}")
            print("uciok")
        elif line.startswith("setoption name Book Path"):
            _, book_path = line.split("setoption name Book Path", 1)
            opening_book_path = book_path.strip()
        elif line.startswith("setoption name Contempt"):
            _, contempt_value = line.split("setoption name Contempt", 1)
            contempt = int(contempt_value.strip())
        elif line.startswith("setoption name Use Opening Book"):
            _, use_opening_book_value = line.split("setoption name Use Opening Book", 1)
            use_opening_book = bool(int(use_opening_book_value.strip()))
        elif line == "isready":
            print("readyok")
        elif line.startswith("position startpos"):
            board = chess.Board()
            if "moves" in line:
                _, moves_part = line.split("moves")
                moves = moves_part.strip().split()
                for move in moves:
                    board.push_uci(move)
        elif line.startswith("position fen"):
            _, fen = line.split("fen", 1)
            board.set_fen(fen.strip())
            if "moves" in line:
                _, moves_part = line.split("moves")
                moves = moves_part.strip().split()
                for move in moves:
                    board.push_uci(move)
        elif line.startswith("go"):
            stop_event.clear()
            extensions = 0
            wtime, btime, movetime = parse_parameters(line)
            remaining_time = (wtime if board.turn == chess.WHITE else btime) if movetime is None else movetime
            start_time = time.time()
            max_time = calculateMaxTime(remaining_time/1000)
            move = best_move(board, start_time, max_time, depth=1000).uci()
            print(f"bestmove {move}")
        elif line == "quit":
            break


if __name__ == "__main__":
    play_chess()
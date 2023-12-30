import chess
from psqt import *
from piece_values import *

def is_endgame(board):
  # Check if there are no major pieces
  no_major_pieces = (
      sum(1 for _ in board.pieces(chess.ROOK, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.QUEEN, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.ROOK, chess.BLACK)) == 0
      and sum(1 for _ in board.pieces(chess.QUEEN, chess.BLACK)) == 0)
  if no_major_pieces:
    return True

  # Check for two rooks and no queen
  if (sum(1 for _ in board.pieces(chess.QUEEN, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.ROOK, chess.WHITE)) <= 1
      and sum(1 for _ in board.pieces(chess.QUEEN, chess.BLACK)) == 0
      and sum(1 for _ in board.pieces(chess.ROOK, chess.BLACK)) <= 1):
    return True

  # Check for two queens or less, kings, and no other pieces except pawns
  if (sum(1 for _ in board.pieces(chess.QUEEN, chess.WHITE)) <= 1
      and sum(1 for _ in board.pieces(chess.KNIGHT, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.BISHOP, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.ROOK, chess.WHITE)) == 0
      and sum(1 for _ in board.pieces(chess.QUEEN, chess.BLACK)) <= 1
      and sum(1 for _ in board.pieces(chess.KNIGHT, chess.BLACK)) == 0
      and sum(1 for _ in board.pieces(chess.BISHOP, chess.BLACK)) == 0
      and sum(1 for _ in board.pieces(chess.ROOK, chess.BLACK)) == 0):
    return True

  # If none of the above conditions are met, return False
  return False

def evaluate_board(board):
    score = 0

    # Iterate through all squares on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)

        if piece is None:
            continue  # Skip empty squares

        if piece.color == chess.WHITE:
            score += piece_values[piece.piece_type]
            square = 0b111_000 ^ square
            # Add position value based on piece-square table
            if piece.piece_type == chess.PAWN:
                score += psqt_pawn[square]
            elif piece.piece_type == chess.KNIGHT:
                score += psqt_knight[square]
            elif piece.piece_type == chess.BISHOP:
                score += psqt_bishop[square]
            elif piece.piece_type == chess.ROOK:
                score += psqt_rook[square]
            elif piece.piece_type == chess.QUEEN:
                score += psqt_queen[square]
            elif piece.piece_type == chess.KING:
                if is_endgame(board):
                    score += psqt_endking[square]
                else:
                    score += psqt_midking[square]
        else:
            score -= piece_values[piece.piece_type]
            # Subtracting position value based on piece-square table
            if piece.piece_type == chess.PAWN:
                score -= psqt_pawn[square]
            elif piece.piece_type == chess.KNIGHT:
                score -= psqt_knight[square]
            elif piece.piece_type == chess.BISHOP:
                score -= psqt_bishop[square]
            elif piece.piece_type == chess.ROOK:
                score -= psqt_rook[square]
            elif piece.piece_type == chess.QUEEN:
                score -= psqt_queen[square]
            elif piece.piece_type == chess.KING:
                if is_endgame(board):
                    score -= psqt_endking[square]
                else:
                    score -= psqt_midking[square]


    return score
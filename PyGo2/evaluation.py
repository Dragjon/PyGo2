import chess
from psqt import *
from piece_values import *
from game_phase import gamePhaseInc

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
    mgScore = 0
    egScore = 0
    gamePhase = 0

    # Iterate through all squares on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)

        if piece is None:
            continue  # Skip empty squares

        gamePhase += gamePhaseInc[piece.piece_type]

        if piece.color == chess.WHITE:
            mgScore += piece_values_mid[piece.piece_type]
            egScore += piece_values_end[piece.piece_type]
            square = 0b111_000 ^ square
            # Add position value based on piece-square table
            if piece.piece_type == chess.PAWN:
                mgScore += psqt_midpawn[square]
                egScore += psqt_endpawn[square]
            elif piece.piece_type == chess.KNIGHT:
                mgScore += psqt_midknight[square]
                egScore += psqt_endknight[square]
            elif piece.piece_type == chess.BISHOP:
                mgScore += psqt_midbishop[square]
                egScore += psqt_endbishop[square]
            elif piece.piece_type == chess.ROOK:
                mgScore += psqt_midrook[square]
                egScore += psqt_endrook[square]
            elif piece.piece_type == chess.QUEEN:
                mgScore += psqt_midqueen[square]
                egScore += psqt_endqueen[square]
            elif piece.piece_type == chess.KING:
                mgScore += psqt_midking[square]
                egScore += psqt_endking[square]
        else:
            mgScore -= piece_values_mid[piece.piece_type]
            egScore -= piece_values_end[piece.piece_type]
            # Subtracting position value based on piece-square table
            if piece.piece_type == chess.PAWN:
                mgScore -= psqt_midpawn[square]
                egScore -= psqt_endpawn[square]
            elif piece.piece_type == chess.KNIGHT:
                mgScore -= psqt_midknight[square]
                egScore -= psqt_endknight[square]
            elif piece.piece_type == chess.BISHOP:
                mgScore -= psqt_midbishop[square]
                egScore -= psqt_endbishop[square]
            elif piece.piece_type == chess.ROOK:
                mgScore -= psqt_midrook[square]
                egScore -= psqt_endrook[square]
            elif piece.piece_type == chess.QUEEN:
                mgScore -= psqt_midqueen[square]
                egScore -= psqt_endqueen[square]
            elif piece.piece_type == chess.KING:
                mgScore -= psqt_midking[square]
                egScore -= psqt_endking[square]
    mgPhase = gamePhase
    if (mgPhase > 24): 
        mgPhase = 24 # in case of early promotion 

    egPhase = 24 - mgPhase
    return (mgScore * mgPhase + egScore * egPhase) / 24
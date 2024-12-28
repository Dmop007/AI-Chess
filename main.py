import pygame
import sys
import chess
import time
import pyttsx3
import random
import os

# Initialize Pygame and pyttsx3
pygame.init()
engine = pyttsx3.init()

# Constants
WIDTH, HEIGHT = 800, 1000  # Increased height to add space for the display below the board
SQUARE_SIZE = WIDTH // 8
FPS = 60
SCORE_FILE = "chess_scores.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load scores from the file
def load_scores():
    if not os.path.exists(SCORE_FILE):
        return 0, 0, 0  # Default scores if the file doesn't exist
    with open(SCORE_FILE, "r") as file:
        lines = file.readlines()
        if len(lines) != 3:
            return 0, 0, 0  # Default scores if the file is not formatted correctly
        grok_wins = int(lines[0].strip())
        chatgpt_wins = int(lines[1].strip())
        draws = int(lines[2].strip())
        return grok_wins, chatgpt_wins, draws

# Save scores to the file
def save_scores(grok_wins, chatgpt_wins, draws):
    with open(SCORE_FILE, "w") as file:
        file.write(f"{grok_wins}\n")
        file.write(f"{chatgpt_wins}\n")
        file.write(f"{draws}\n")

# Load images
def load_images():
    pieces = ['bK', 'bN', 'bB', 'bQ', 'bR', 'bP', 'wK', 'wN', 'wB', 'wQ', 'wR', 'wP']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    return images

# Draw the board
def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces
def draw_pieces(screen, board, images):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != '--':
                screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Convert Pygame board to python-chess board
def pygame_to_chess_board(pygame_board):
    chess_board = chess.Board.empty()
    for row in range(8):
        for col in range(8):
            piece = pygame_board[row][col]
            if piece != '--':
                chess_board.set_piece_at(chess.square(col, 7 - row), chess.Piece.from_symbol(piece[1].upper() if piece[0] == 'w' else piece[1].lower()))
    return chess_board

# Convert python-chess board to Pygame board
def chess_to_pygame_board(chess_board):
    pygame_board = [['--' for _ in range(8)] for _ in range(8)]
    for square in chess.SQUARES:
        piece = chess_board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            pygame_board[7 - row][col] = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
    return pygame_board

# Count the pieces of each color
def count_pieces(board):
    white_count = 0
    black_count = 0
    for piece in board.piece_map().values():
        if piece.color == chess.WHITE:
            white_count += 1
        else:
            black_count += 1
    return white_count, black_count

# Simple minimax AI with Alpha-Beta Pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def evaluate_board(board):
    white_count, black_count = count_pieces(board)
    eval = 0
    for piece in board.piece_map().values():
        if (piece.color == chess.WHITE and white_count <= 2) or (piece.color == chess.BLACK and black_count <= 2):
            # Shift focus away from the king if only two pieces of one color are left
            if piece.piece_type == chess.KING:
                continue
        eval += piece_value(piece)
    return eval

def piece_value(piece):
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    return values[piece.piece_type] if piece.color == chess.WHITE else -values[piece.piece_type]

def get_best_move_minimax(board, depth):
    best_move = None
    best_value = float('-inf')
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if board_value > best_value:
            best_value = board_value
            best_move = move
    return best_move

# Trash-talking phrases
trash_talk_white = [
    "Is that the best you can do?",
    "You're going down!",
    "Watch and learn!",
    "You're no match for me!",
    "This will be over soon."
]

trash_talk_black = [
    "You're making this too easy!",
    "Better luck next time!",
    "I'm just getting started!",
    "You don't stand a chance!",
    "Prepare to lose!"
]

# Text-to-speech function with different voices
def speak(text, voice_id):
    engine.setProperty('voice', voice_id)
    engine.say(text)
    engine.runAndWait()

# Display the winner and AI names
def display_winner(screen, winner, ai_white, ai_black, grok_wins, chatgpt_wins, draws):
    font = pygame.font.SysFont(None, 36)
    ai_info_white = f"White (GROK): {ai_white.__name__}"
    ai_info_black = f"Black (ChatGPT): {ai_black.__name__}"
    score_info = f"GROK Wins: {grok_wins} | ChatGPT Wins: {chatgpt_wins} | Draws: {draws}"
    text_winner = font.render(winner, True, BLUE)
    text_white = font.render(ai_info_white, True, BLUE)
    text_black = font.render(ai_info_black, True, BLUE)
    text_score = font.render(score_info, True, BLUE)
    screen.fill(WHITE, (0, 800, WIDTH, 200))  # Clear the area below the board
    screen.blit(text_white, (10, 810))
    screen.blit(text_black, (10, 840))
    screen.blit(text_winner, (10, 870))
    screen.blit(text_score, (10, 900))
    pygame.display.flip()
    time.sleep(30)  # Display the winner for 30 seconds
    pygame.quit()
    sys.exit()

# Display AI names and scores below the board during the game
def display_ai_names(screen, ai_white, ai_black, grok_wins, chatgpt_wins, draws):
    font = pygame.font.SysFont(None, 36)
    ai_info_white = f"White (GROK): {ai_white.__name__}"
    ai_info_black = f"Black (ChatGPT): {ai_black.__name__}"
    score_info = f"GROK Wins: {grok_wins} | ChatGPT Wins: {chatgpt_wins} | Draws: {draws}"
    screen.fill(WHITE, (0, 800, WIDTH, 200))  # Clear the area below the board
    text_white = font.render(ai_info_white, True, BLUE)
    text_black = font.render(ai_info_black, True, BLUE)
    text_score = font.render(score_info, True, BLUE)
    screen.blit(text_white, (10, 810))
    screen.blit(text_black, (10, 840))
    screen.blit(text_score, (10, 870))
    pygame.display.flip()

# Main function
def main():
    global grok_wins, chatgpt_wins, draws

    # Load the scores from the file
    grok_wins, chatgpt_wins, draws = load_scores()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    images = load_images()

    # Initial board setup
    board = [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    ]

    chess_board = pygame_to_chess_board(board)
    turn = 'w'  # White starts

    move_count = 0  # Counter to track the number of moves

    # AI functions for white (GROK) and black (ChatGPT)
    ai_white = get_best_move_minimax  # Using minimax for GROK
    ai_black = get_best_move_minimax  # Using minimax for ChatGPT

    # Set different voices for each AI
    voices = engine.getProperty('voices')
    white_voice_id = voices[0].id  # Use the first available voice for white
    black_voice_id = voices[1].id  # Use the second available voice for black

    # Initial display of the board and AI names
    draw_board(screen)
    draw_pieces(screen, board, images)
    display_ai_names(screen, ai_white, ai_black, grok_wins, chatgpt_wins, draws)
    pygame.display.flip()

    # Initial delay before the first move
    time.sleep(5)

    # Game loop
    while not chess_board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # AI move for white (GROK)
        if turn == 'w' and ai_white:
            move = ai_white(chess_board, 3)
            if move:
                chess_board.push(move)
                board = chess_to_pygame_board(chess_board)
                turn = 'b'
                move_count += 1
                if move_count > 4:  # Only start trash-talking after the first 4 moves
                    speak(random.choice(trash_talk_white), white_voice_id)  # White AI trash talk
            time.sleep(1)  # Delay for human viewing

        # AI move for black (ChatGPT)
        if turn == 'b' and ai_black:
            move = ai_black(chess_board, 3)
            if move:
                chess_board.push(move)
                board = chess_to_pygame_board(chess_board)
                turn = 'w'
                move_count += 1
                if move_count > 4:  # Only start trash-talking after the first 4 moves
                    speak(random.choice(trash_talk_black), black_voice_id)  # Black AI trash talk
            time.sleep(1)  # Delay for human viewing

        draw_board(screen)
        draw_pieces(screen, board, images)
        pygame.display.flip()
        clock.tick(FPS)

    # Determine the outcome and update the scores
    if chess_board.is_checkmate():
        if chess_board.turn == chess.BLACK:
            winner = "GROK Wins!"
            grok_wins += 1
        else:
            winner = "ChatGPT Wins!"
            chatgpt_wins += 1
    elif chess_board.is_stalemate() or chess_board.is_insufficient_material() or chess_board.is_seventyfive_moves() or chess_board.is_variant_draw():
        winner = "Draw!"
        draws += 1
    else:
        winner = "Game Over!"

    # Save the updated scores to the file
    save_scores(grok_wins, chatgpt_wins, draws)

    # Display the winner and updated scores
    display_winner(screen, winner, ai_white, ai_black, grok_wins, chatgpt_wins, draws)

if __name__ == "__main__":
    main()

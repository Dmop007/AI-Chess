import pygame
import sys
import chess
import time
import pyttsx3
import random
import os
import requests
import chess.engine

# Initialize Pygame and pyttsx3
pygame.init()
tts_engine = pyttsx3.init()

# Initialize Stockfish engine
engine_path = "path/to/stockfish"  # Update this path to the location of your Stockfish executable
try:
    stockfish_engine = chess.engine.SimpleEngine.popen_uci(engine_path)
except Exception as e:
    print(f"Error initializing Stockfish engine: {e}")
    stockfish_engine = None

# Constants
WIDTH, HEIGHT = 800, 1000
SQUARE_SIZE = WIDTH // 8
FPS = 60
SCORE_FILE = "chess_scores.txt"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (211, 211, 211)

# Initialize win counters for each player
win_counters = {
    "grok_move": {"white_wins": 0, "black_wins": 0, "vs": {}},
    "chatgpt_move": {"white_wins": 0, "black_wins": 0, "vs": {}},
    "get_user_move": {"white_wins": 0, "black_wins": 0, "vs": {}},
    "stockfish_move": {"white_wins": 0, "black_wins": 0, "vs": {}},
    "get_best_move_minimax": {"white_wins": 0, "black_wins": 0, "vs": {}},
    "random_move": {"white_wins": 0, "black_wins": 0, "vs": {}}
}

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_scores(scores):
    with open(SCORE_FILE, "w") as file:
        for score in scores:
            file.write(score + "\n")

def record_match(scores, white_player, black_player, winner, match_time, num_moves):
    new_record = f"White Player: {white_player}, Black Player: {black_player}, Winner: {winner}, Match Time: {match_time:.2f} seconds, Number of Moves: {num_moves}"
    scores.append(new_record)
    save_scores(scores)
    if winner == "White":
        win_counters[white_player]["white_wins"] += 1
        if black_player not in win_counters[white_player]["vs"]:
            win_counters[white_player]["vs"][black_player] = {"wins": 0, "losses": 0}
        win_counters[white_player]["vs"][black_player]["wins"] += 1
    elif winner == "Black":
        win_counters[black_player]["black_wins"] += 1
        if white_player not in win_counters[black_player]["vs"]:
            win_counters[black_player]["vs"][white_player] = {"wins": 0, "losses": 0}
        win_counters[black_player]["vs"][white_player]["wins"] += 1

def load_images():
    pieces = ['bK', 'bN', 'bB', 'bQ', 'bR', 'bP', 'wK', 'wN', 'wB', 'wQ', 'wR', 'wP']
    return {piece: pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE)) for piece in pieces}

def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board, images):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (piece != '--'):
                screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def pygame_to_chess_board(pygame_board):
    chess_board = chess.Board.empty()
    for row in range(8):
        for col in range(8):
            piece = pygame_board[row][col]
            if piece != '--':
                chess_board.set_piece_at(chess.square(col, 7 - row), chess.Piece.from_symbol(piece[1].upper() if piece[0] == 'w' else piece[1].lower()))
    return chess_board

def chess_to_pygame_board(chess_board):
    pygame_board = [['--' for _ in range(8)] for _ in range(8)]
    for square in chess.SQUARES:
        piece = chess_board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            pygame_board[7 - row][col] = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
    return pygame_board

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
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    return sum(piece_values[piece.piece_type] if piece.color == chess.WHITE else -piece_values[piece.piece_type] for piece in board.piece_map().values())

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

def random_move(board, depth):
    return random.choice(list(board.legal_moves))

def get_user_move(board, depth):
    move = None
    selected_square = None
    while move not in board.legal_moves:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                square = chess.square(col, 7 - row)
                if selected_square is None:
                    selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if board.is_legal(move):
                        return move
                    selected_square = None
    return move

def stockfish_move(board, depth):
    if stockfish_engine:
        result = stockfish_engine.play(board, chess.engine.Limit(time=2.0))
        return result.move
    else:
        print("Stockfish engine is not available.")
        return random_move(board, depth)

def grok_move(board, depth, url, headers=None):
    headers = headers or {"Content-Type": "application/json"}
    data = {"fen": board.fen(), "depth": depth}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        move_uci = response.json().get("best_move")
        if move_uci:
            return chess.Move.from_uci(move_uci)
    except requests.RequestException as e:
        print(f"Error fetching move from Grok: {e}")
    return random_move(board, depth)

def chatgpt_move(board, depth, headers):
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a chess engine."},
            {"role": "user", "content": f"Given the FEN {board.fen()}, what is the best move?"}
        ],
        "max_tokens": 50
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        move_uci = response.json().get("choices")[0]["message"]["content"].strip()
        return chess.Move.from_uci(move_uci)
    except requests.RequestException as e:
        print(f"Error fetching move from ChatGPT: {e}")
    return random_move(board, depth)

def load_trash_talk():
    trash_talk_white, trash_talk_black = [], []
    if os.path.exists("trash_talk.txt"):
        with open("trash_talk.txt", "r") as file:
            for line in file:
                if line.startswith("white:"):
                    trash_talk_white.append(line.replace("white:", "").strip())
                elif line.startswith("black:"):
                    trash_talk_black.append(line.replace("black:", "").strip())
    return trash_talk_white, trash_talk_black

def speak(text, voice_id, delay=0):
    tts_engine.setProperty('voice', voice_id)
    time.sleep(delay)
    tts_engine.say(text)
    tts_engine.runAndWait()

def display_winner(screen, winner, white_wins, black_wins, draws):
    font = pygame.font.SysFont(None, 36)
    text_winner = font.render(winner, True, BLUE)
    screen.fill(WHITE, (0, 800, WIDTH, 200))
    screen.blit(text_winner, (10, 870))
    pygame.display.flip()
    time.sleep(30)
    pygame.quit()
    sys.exit()

def display_scores(screen, scores):
    screen.fill(BLACK, (0, 800, WIDTH, 200))  # Fill the area under the game board with black
    pygame.display.flip()

def input_box(screen, prompt, width=200):
    font = pygame.font.SysFont(None, 36)
    input_box = pygame.Rect(10, 250, width, 30)  # Adjusted width for the input box
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        text += pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8')
                    else:
                        text += event.unicode

        screen.fill(WHITE)
        prompt_surface = font.render(prompt, True, BLUE)
        screen.blit(prompt_surface, (10, 150))
        txt_surface = font.render(text, True, color)
        width = max(width, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

    return text

def select_ai_methods(screen):
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)  # Large font for "AI Chess"
    mythic_font = pygame.font.Font(None, 100)  # Mythic font for "AI Chess"
    options = ["Grok", "ChatGPT", "Zenkay", "Stockfish", "Quantum", "Example", "User Move", "Minimax", "Random Move", "Custom URL"]
    ai_methods = [grok_move, chatgpt_move, grok_move, stockfish_move, grok_move, grok_move, get_user_move, get_best_move_minimax, random_move, grok_move]
    urls = {
        "Grok": "https://x.com/i/grok?focus=1",
        "ChatGPT": "https://api.openai.com/v1/chat/completions",
        "Quantum": "https://quantumai.google/cirq/experiments/unitary/quantum_chess/quantum_chess_rest_api",
        "Example": "https://www.chess.com/callback/board/game",
        "Zenkay": "https://py-chess-api.zenkay.dev/move"
    }

    background_image = pygame.image.load("chess.jpg")  # Load the background image
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    def draw_options():
        screen.blit(background_image, (0, 0))  # Draw the background image
        ai_chess_text = mythic_font.render("AI Chess", True, LIGHT_GRAY)
        screen.blit(ai_chess_text, (WIDTH // 2 - ai_chess_text.get_width() // 2, 50))  # Center the "AI Chess" text

        # Draw the AI options
        box_width = max(font.size(option)[0] for option in options) + 20
        box_height = font.get_height() + 10
        box_y = 200
        box_padding = 10
        boxes = []
        
        for i, option in enumerate(options):
            box_x = (i % 2) * (box_width + box_padding) + (WIDTH - 2 * box_width - box_padding) // 2
            if i % 2 == 0 and i > 0:
                box_y += box_height + box_padding
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            boxes.append(box_rect)
            pygame.draw.rect(screen, BLACK, box_rect)
            text = font.render(option, True, LIGHT_GRAY)
            screen.blit(text, (box_x + 10, box_y + 5))
        
        instructions = [
            "Instructions:",
            "1. Select AI method for White by clicking or pressing a number key.",
            "2. Select AI method for Black by clicking or pressing a number key.",
            "3. If 'Custom URL' is selected, enter the URL when prompted."
        ]
        
        for i, line in enumerate(instructions):
            text = font.render(line, True, WHITE)
            screen.blit(text, (10, HEIGHT - (len(instructions) - i) * 30))

        pygame.display.flip()
        return boxes

    def get_choice(boxes):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, box in enumerate(boxes):
                        if box.collidepoint(event.pos):
                            return ai_methods[i], options[i]
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]:
                        return ai_methods[event.key - pygame.K_1], options[event.key - pygame.K_1]

    screen.fill(WHITE)
    text = font.render("Select AI method for White:", True, BLUE)
    screen.blit(text, (10, 10))
    boxes = draw_options()
    white_choice, white_option = get_choice(boxes)

    if white_option == "Custom URL":
        custom_url_white = input_box(screen, "Enter URL for White AI:", width=400)
        openai_api_key = input_box(screen, "Enter API Key for White AI:", width=400)
        headers_white = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        print(f"Selected White AI: {white_option}, URL: {custom_url_white}")
    else:
        custom_url_white = urls.get(white_option, None)
        headers_white = None

    screen.fill(WHITE)
    text = font.render("Select AI method for Black:", True, BLUE)
    screen.blit(text, (10, 10))
    boxes = draw_options()
    black_choice, black_option = get_choice(boxes)

    if black_option == "Custom URL":
        custom_url_black = input_box(screen, "Enter URL for Black AI:", width=400)
        openai_api_key = input_box(screen, "Enter API Key for Black AI:", width=400)
        headers_black = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        print(f"Selected Black AI: {black_option}, URL: {custom_url_black}")
    else:
        custom_url_black = urls.get(black_option, None)
        headers_black = None

    return white_choice, black_choice, custom_url_white, custom_url_black, headers_white, headers_black

def main():
    global win_counters

    scores = load_scores()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    images = load_images()

    background_image = pygame.image.load("chess.jpg")  # Load the background image from root
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    background_image.set_alpha(128)  # Set image transparency to 50%

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
    turn = 'w'
    move_count = 0
    next_trash_talk = random.randint(1, 5)
    trash_talk_white, trash_talk_black = load_trash_talk()
    ai_white, ai_black, custom_url_white, custom_url_black, headers_white, headers_black = select_ai_methods(screen)
    voices = tts_engine.getProperty('voices')
    white_voice_id = voices[0].id
    black_voice_id = voices[1].id

    
    screen.blit(background_image, (0, 0)) # Draw the background image with 50% visibility

    draw_board(screen)
    draw_pieces(screen, board, images)
    screen.blit(background_image, (0, 800))  # Draw the background image behind the display at the bottom
    pygame.display.flip()
    time.sleep(5)

    start_time = time.time()

    while not chess_board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if turn == 'w' and ai_white:
            move = grok_move(chess_board, 3, custom_url_white, headers_white) if custom_url_white else ai_white(chess_board, 3)
            if move:
                chess_board.push(move)
                board = chess_to_pygame_board(chess_board)
                turn = 'b'
                move_count += 1
                if move_count >= next_trash_talk:
                    speak(random.choice(trash_talk_white), white_voice_id, delay=0.5)
                    next_trash_talk += random.randint(1, 5)
            time.sleep(1)

        if turn == 'b' and ai_black:
            move = grok_move(chess_board, 3, custom_url_black, headers_black) if custom_url_black else ai_black(chess_board, 3)
            if move:
                chess_board.push(move)
                board = chess_to_pygame_board(chess_board)
                turn = 'w'
                move_count += 1
                if move_count >= next_trash_talk:
                    speak(random.choice(trash_talk_black), black_voice_id, delay=0.5)
                    next_trash_talk += random.randint(1, 5)
            time.sleep(1)

        draw_board(screen)
        draw_pieces(screen, board, images)
        screen.blit(background_image, (0, 800))  # Draw the background image behind the display at the bottom
        pygame.display.flip()
        clock.tick(FPS)

    match_time = time.time() - start_time

    if chess_board.is_checkmate():
        winner = "White" if chess_board.turn == chess.BLACK else "Black"
    elif chess_board.is_stalemate() or chess_board.is_insufficient_material() or chess_board.is_seventyfive_moves() or chess_board.is_variant_draw():
        winner = "Draw"
    else:
        winner = "Game Over"

    record_match(scores, ai_white.__name__, ai_black.__name__, winner, match_time, move_count)
    display_winner(screen, winner, win_counters[ai_white.__name__]["white_wins"], win_counters[ai_black.__name__]["black_wins"], 0)

if __name__ == "__main__":
    main()

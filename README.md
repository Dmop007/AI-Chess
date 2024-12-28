# AI-Chess
# AI playing Chess against another AI.  
# Grok Vs ChatGPT currently.

```markdown
# AI Chess Game

This is an AI-based chess game implemented using Python and Pygame. The game features two AI players (GROK and ChatGPT) that play against each other, with built-in trash-talking capabilities.

## Table of Contents

- [System Specifications](#system-specifications)
- [Dependencies](#dependencies)
- [Setup Instructions](#setup-instructions)
- [Running the Game](#running-the-game)
- [Code Explanation](#code-explanation)
- [Contributing](#contributing)
- [License](#license)

## System Specifications

- **Operating System**: Windows 10 or later
- **Processor**: Intel Core i5 or equivalent
- **RAM**: 4GB or more
- **Python Version**: Python 3.8 or later

## Dependencies

The project relies on the following dependencies:

- `pygame`: A set of Python modules designed for writing video games.
- `python-chess`: A chess library for Python, with move generation, move validation, and support for common formats.
- `pyttsx3`: A text-to-speech conversion library in Python.

You can install these dependencies using `pip`:

```sh
pip install pygame python-chess pyttsx3
```

## Setup Instructions

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/Dmop007/AI-Chess.git
    cd AI-Chess
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the Game**:
    ```sh
    python ai_chess_game.py
    ```

## Running the Game

To start the game, run the `ai_chess_game.py` script:

```sh
python ai_chess_game.py
```

The game window will open, and the AI players will start playing against each other. The game will display the board and the current score, and you will hear the AI players trash-talking each other after the first four moves.

## Code Explanation

### Main Components

1. **Game Initialization**:
    The game is initialized using Pygame, and the main window is set up with the specified dimensions.

2. **Loading Images**:
    The chess piece images are loaded and scaled to fit the board squares.

3. **Game Loop**:
    The game loop handles the AI moves, updates the board, and plays trash-talking messages after the first four moves.

4. **AI Logic**:
    The AI players use a minimax algorithm with alpha-beta pruning to determine the best move.

5. **Text-to-Speech**:
    The `pyttsx3` library is used to convert text to speech for the trash-talking messages.

### Key Functions

- `load_images()`: Loads and scales the chess piece images.
- `draw_board(screen)`: Draws the chess board on the screen.
- `draw_pieces(screen, board, images)`: Draws the chess pieces on the board.
- `minimax(board, depth, alpha, beta, maximizing_player)`: Implements the minimax algorithm with alpha-beta pruning.
- `speak(text, voice_id)`: Uses `pyttsx3` to convert text to speech.
- `display_ai_names(screen, ai_white, ai_black, grok_wins, chatgpt_wins, draws)`: Displays the AI names and scores.
- `display_winner(screen, winner, ai_white, ai_black, grok_wins, chatgpt_wins, draws)`: Displays the winner and final scores.

## Contributing

We welcome contributions from the community. To contribute:

1. **Fork the repository**.
2. **Create a new branch** for your feature or bug fix:
    ```sh
    git checkout -b feature-name
    ```
3. **Commit your changes**:
    ```sh
    git commit -m "Description of your changes"
    ```
4. **Push to the branch**:
    ```sh
    git push origin feature-name
    ```
5. **Open a pull request** on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

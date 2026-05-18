"""
╔══════════════════════════════════════════════════════════════╗
║                   HANGMAN GAME - Project 1                   ║
║              EDC Paris Business School - Group 4             ║
╚══════════════════════════════════════════════════════════════╝

Rules:
  - One player (or computer) chooses a word.
  - The other player guesses one letter at a time.
  - Wrong guesses reduce lives (hangman drawing grows).
  - Win when all letters are guessed; lose when lives reach zero.

Extras implemented:
  ✔ Handle invalid input (numbers, special chars, repeated letters)
  ✔ Player chooses how many games to play
  ✔ Player can input a custom word (human vs human mode)
  ✔ Player can choose drawing detail level (number of lives)
  ✔ Score tracker across multiple games
"""

import random
import os
import sys

# ─────────────────────────────────────────────
#  WORD BANK
# ─────────────────────────────────────────────
WORD_BANK = [
    "python", "hangman", "computer", "programming", "developer",
    "keyboard", "algorithm", "variable", "function", "database",
    "network", "interface", "framework", "chocolate", "university",
    "elephant", "adventure", "challenge", "frequency", "democracy",
    "invisible", "knowledge", "laboratory", "management", "narrative",
    "objective", "paragraph", "quarterly", "resources", "telescope",
    "underline", "volunteer", "warehouse", "xylophone", "yesterday",
]

# ─────────────────────────────────────────────
#  HANGMAN DRAWING STAGES
#  10 body-part stages (index 0 = empty gallows)
#  sliced/mapped dynamically based on chosen lives
# ─────────────────────────────────────────────
STAGES = [
    # 0 – empty gallows
    """
   +----+
   |    |
        |
        |
        |
        |
  =======""",
    # 1 – head
    """
   +----+
   |    |
   O    |
        |
        |
        |
  =======""",
    # 2 – body
    """
   +----+
   |    |
   O    |
   |    |
        |
        |
  =======""",
    # 3 – left arm
    """
   +----+
   |    |
   O    |
  /|    |
        |
        |
  =======""",
    # 4 – right arm
    """
   +----+
   |    |
   O    |
  /|\\   |
        |
        |
  =======""",
    # 5 – left leg
    """
   +----+
   |    |
   O    |
  /|\\   |
  /     |
        |
  =======""",
    # 6 – right leg
    """
   +----+
   |    |
   O    |
  /|\\   |
  / \\   |
        |
  =======""",
    # 7 – left hand
    """
   +----+
   |    |
   O    |
 -/|\\   |
  / \\   |
        |
  =======""",
    # 8 – right hand
    """
   +----+
   |    |
   O    |
 -/|\\-  |
  / \\   |
        |
  =======""",
    # 9 – left foot
    """
   +----+
   |    |
   O    |
 -/|\\-  |
  / \\   |
 /      |
  =======""",
    # 10 – right foot (fully drawn)
    """
   +----+
   |    |
   O    |
 -/|\\-  |
  / \\   |
 /   \\  |
  =======""",
]

# Detail level menu: maps choice number to lives allowed
DETAIL_LEVELS = {
    1: {"label": "Very Easy  (10 lives - full detailed drawing)", "lives": 10},
    2: {"label": "Easy       ( 8 lives - hands & feet included)", "lives": 8},
    3: {"label": "Medium     ( 6 lives - classic hangman)",       "lives": 6},
    4: {"label": "Hard       ( 4 lives - arms & legs only)",      "lives": 4},
    5: {"label": "Brutal     ( 2 lives - head & body only)",      "lives": 2},
}


# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def divider(char="-", width=54):
    """Print a horizontal divider."""
    print(char * width)


def header():
    """Print the game header banner."""
    clear()
    print()
    divider("=")
    print("           H A N G M A N")
    divider("=")
    print()


def get_hangman_drawing(wrong_guesses, max_lives):
    """
    Return the correct drawing stage based on wrong_guesses and max_lives.
    Stages are distributed evenly across the available lives so the drawing
    always progresses smoothly regardless of the chosen detail level.
    """
    total_stages = len(STAGES) - 1          # 10 possible stages (1..10)
    # Map wrong_guesses (0 -> max_lives) to a stage index (0 -> total_stages)
    stage_index = round((wrong_guesses / max_lives) * total_stages)
    stage_index = max(0, min(stage_index, total_stages))
    return STAGES[stage_index]


def display_game_state(word_display, wrong_letters, correct_letters,
                       wrong_guesses, max_lives, hint_letter=None):
    """
    Print the current game state:
      - hangman drawing
      - word with blanks
      - lives remaining
      - used letters
      - hint (if just used)
    """
    print(get_hangman_drawing(wrong_guesses, max_lives))
    print()

    # Word display (spaced out for readability)
    print("  Word:  " + "  ".join(word_display))
    print()

    # Lives bar
    lives_left = max_lives - wrong_guesses
    hearts     = "* " * lives_left + "x " * wrong_guesses
    print(f"  Lives: {hearts}({lives_left}/{max_lives})")
    print()

    # Used letters
    if wrong_letters:
        print(f"  [WRONG]   {', '.join(sorted(wrong_letters))}")
    if correct_letters:
        print(f"  [CORRECT] {', '.join(sorted(correct_letters))}")

    # Hint (shown for one turn only)
    if hint_letter:
        print(f"\n  >> HINT: The letter '{hint_letter.upper()}' is in the word!")

    print()
    divider()


# ─────────────────────────────────────────────
#  SETUP FUNCTIONS
# ─────────────────────────────────────────────

def choose_detail_level():
    """
    Ask the player how detailed the hangman drawing should be.
    Returns the number of lives (wrong guesses allowed).
    """
    header()
    print("  How detailed should the hangman drawing be?\n")
    for key, val in DETAIL_LEVELS.items():
        print(f"  [{key}]  {val['label']}")
    print()

    while True:
        choice = input("  Your choice (1-5): ").strip()
        if choice.isdigit() and int(choice) in DETAIL_LEVELS:
            return DETAIL_LEVELS[int(choice)]["lives"]
        print("  Please enter a number between 1 and 5.")


def choose_word_mode():
    """
    Ask whether the computer or a human player picks the word.
    Returns (word, mode_label) as a tuple.
    """
    header()
    print("  Who chooses the secret word?\n")
    print("  [1]  Computer  - random word from the word bank")
    print("  [2]  Player    - a friend types a secret word (human vs human)")
    print()

    while True:
        choice = input("  Your choice (1 or 2): ").strip()

        if choice == "1":
            # Computer picks a random word from the word bank
            word = random.choice(WORD_BANK)
            return word.lower(), "Computer"

        elif choice == "2":
            # Player 2 types a custom word – screen is cleared so Player 1 cannot see it
            clear()
            print("\n  Player 2: type a secret word (letters only, no spaces).")
            print("  Player 1, look away!\n")
            while True:
                word = input("  Secret word: ").strip().lower()
                if not word:
                    print("  The word cannot be empty.")
                elif not word.isalpha():
                    print("  Only letters please - no numbers or spaces.")
                else:
                    # Clear screen before returning so Player 1 cannot see the word
                    clear()
                    return word, "Player 2"
        else:
            print("  Please enter 1 or 2.")


def choose_number_of_games():
    """
    Ask how many games to play in this session.
    Returns an integer between 1 and 10.
    """
    header()
    print("  How many games would you like to play?\n")
    while True:
        choice = input("  Number of games (1-10): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 10:
            return int(choice)
        print("  Please enter a number between 1 and 10.")


# ─────────────────────────────────────────────
#  CORE GAME LOOP
# ─────────────────────────────────────────────

def play_game(max_lives, game_number, total_games):
    """
    Run a single game of Hangman.

    Parameters
    ----------
    max_lives    : int  – number of wrong guesses before losing
    game_number  : int  – current game index (for display)
    total_games  : int  – total games in session (for display)

    Returns
    -------
    bool – True if the player won, False if they lost.
    """
    # ── Choose word ──────────────────────────────────────
    word, word_source = choose_word_mode()
    word_letters      = set(word)   # unique letters in the secret word

    # ── Initialise game state ────────────────────────────
    guessed_letters = set()    # all letters the player has tried
    wrong_letters   = []       # letters NOT in the word (sorted for display)
    correct_letters = []       # letters found in the word (sorted for display)
    wrong_guesses   = 0        # counter of wrong attempts

    hint_used   = False        # each game allows one hint
    hint_letter = None         # set to a letter when hint is triggered

    # Build initial display: '_' for every unguessed letter
    word_display = ["_"] * len(word)

    # ── Round loop ───────────────────────────────────────
    while wrong_guesses < max_lives and "_" in word_display:

        header()
        print(f"  Game {game_number}/{total_games}  |  Word provided by: {word_source}\n")
        display_game_state(word_display, wrong_letters, correct_letters,
                           wrong_guesses, max_lives, hint_letter)
        hint_letter = None   # hint message shown only for one turn

        print("  Enter a letter  |  HINT = reveal a letter  |  QUIT = abandon\n")
        raw = input("  Your guess: ").strip().lower()

        # ── Special commands ─────────────────────────────
        if raw == "quit":
            # Player quits mid-game; counts as a loss
            print(f"\n  You quit. The word was: {word.upper()}")
            input("\n  Press Enter to continue...")
            return False

        if raw == "hint":
            if hint_used:
                input("  You already used your hint! Press Enter to continue...")
                continue
            # Reveal one random letter that has not been guessed yet
            remaining = [l for l in word_letters if l not in guessed_letters]
            if remaining:
                hint_letter = random.choice(remaining)
                hint_used = True
            continue

        # ── Input validation ─────────────────────────────

        # Must be exactly one character
        if len(raw) != 1:
            input("  Please enter exactly ONE letter. Press Enter to continue...")
            continue

        # Extra: numbers are not allowed – give a specific message
        if raw.isdigit():
            input("  Numbers are not valid guesses. Letters only! Press Enter to continue...")
            continue

        # Extra: special characters are not allowed
        if not raw.isalpha():
            input("  Special characters are not valid. Letters only! Press Enter to continue...")
            continue

        # Extra: repeated guess – do not count as wrong, just warn
        if raw in guessed_letters:
            input(f"  You already guessed '{raw.upper()}'. Try a different letter. Press Enter...")
            continue

        # ── Process valid guess ───────────────────────────
        guessed_letters.add(raw)

        if raw in word_letters:
            # Correct guess: reveal all occurrences in word_display
            correct_letters.append(raw.upper())
            for i, letter in enumerate(word):
                if letter == raw:
                    word_display[i] = raw
        else:
            # Wrong guess: add to wrong list and increment counter
            wrong_letters.append(raw.upper())
            wrong_guesses += 1

    # ── End-of-round result ───────────────────────────────
    header()
    print(f"  Game {game_number}/{total_games}\n")

    if "_" not in word_display:
        # Player guessed the word
        display_game_state(word_display, wrong_letters, correct_letters,
                           wrong_guesses, max_lives)
        print(f"  YOU WIN! The word was: {word.upper()}")
        result = True
    else:
        # Player ran out of lives – show fully drawn hangman
        print(STAGES[-1])   # always show the complete drawing on loss
        print()
        print(f"  GAME OVER! The word was: {word.upper()}")
        result = False

    input("\n  Press Enter to continue...")
    return result


# ─────────────────────────────────────────────
#  SCOREBOARD
# ─────────────────────────────────────────────

def show_scoreboard(wins, losses, total):
    """Display the final session scoreboard with a performance message."""
    header()
    print("  --- SESSION RESULTS ---\n")
    print(f"  Games played : {total}")
    print(f"  Wins         : {wins}")
    print(f"  Losses       : {losses}")
    win_rate = (wins / total * 100) if total > 0 else 0
    print(f"  Win rate     : {win_rate:.0f}%\n")
    divider()

    # Performance feedback
    if win_rate == 100:
        print("  PERFECT SCORE! Outstanding!")
    elif win_rate >= 70:
        print("  Great performance!")
    elif win_rate >= 40:
        print("  Not bad, keep practising!")
    else:
        print("  Tough session - you'll do better next time!")
    print()


# ─────────────────────────────────────────────
#  MAIN SESSION CONTROLLER
# ─────────────────────────────────────────────

def main():
    """
    Entry point.
    Handles the full session: welcome, setup, game loop, scoreboard, replay.
    """
    # Welcome screen
    header()
    print("  Welcome to Hangman!\n")
    print("  Guess the hidden word letter by letter.")
    print("  Wrong guesses build the hangman drawing.")
    print("  Guess all letters before the drawing is complete to win!\n")
    divider()
    input("  Press Enter to start...")

    # Session setup – choose difficulty and number of games
    max_lives   = choose_detail_level()
    total_games = choose_number_of_games()

    wins   = 0
    losses = 0

    # Play each game in sequence
    for game_number in range(1, total_games + 1):
        won = play_game(max_lives, game_number, total_games)
        if won:
            wins += 1
        else:
            losses += 1

    # Show final scoreboard
    show_scoreboard(wins, losses, total_games)

    # Offer to play again
    print("  Play again? [Y] Yes  [N] No\n")
    replay = input("  Your choice: ").strip().lower()
    if replay == "y":
        main()   # restart the whole session
    else:
        header()
        print("  Thanks for playing Hangman!")
        print("  See you next time!\n")
        divider()
        sys.exit(0)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()

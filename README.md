# Hangman Game
EDC Paris Business School - Project 1 | Group 4

## Description
Hangman is a word-guessing game where one player (or the computer) picks a secret word, and the other player tries to reveal it letter by letter before a stick figure is fully drawn on a gallows.

## Rules
- The secret word is shown as a row of blanks, one per letter
- Each turn, the guesser picks one letter
- A correct guess reveals every occurrence of that letter in the word
- A wrong guess adds one body part to the hangman drawing
- Win by revealing all letters before running out of lives
- Lose when the drawing is complete (lives reach zero)

## Features
- 5 difficulty levels (2 to 10 lives)
- Human vs Computer or Human vs Human mode
- Invalid input handling (numbers, symbols, repeated letters)
- Hint system (1 per game)
- Score tracker across multiple games

## How to run
python src/hangman.py

## Project structure
hangman-game/
├── src/
│   └── hangman.py
└── README.md

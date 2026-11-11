# Hamvod Learning Bot

A Telegram learning bot for Web Development, Cyber Security, Networking, Viral Video Content, and Robotics with Arduino.

## Features

- Welcome screen with a language/topic menu
- Topic-based lesson navigation
- Unit-by-unit course flow
- Built for Telegram from the lesson content you supplied

## Setup

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   - Windows: .venv\Scripts\activate
   - macOS/Linux: source .venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Copy environment file:
   copy .env.example .env
5. Replace the token value with your actual bot token from BotFather.
6. Run the bot:
   python learning_bot.py

## Bot behavior

- `/start` shows the Hamvod welcome message and topic menu
- Each topic contains units that can be opened one by one
- Navigation buttons allow moving between units and back to the main menu

## Notes

The course content is embedded in the bot so it can be served directly without copying text into multiple places.

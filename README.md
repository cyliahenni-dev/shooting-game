2D Shooting Game 🎮

Welcome to the 2D Shooting Game repository! This project is a Python-based 2D arcade-style shooting game designed using Object-Oriented Programming (OOP) principles.

📁 Project Structure

Here is an overview of the core files included in this project:

main.py: The main execution entry point to run the game.

game.py: Contains the core game loop, event handling, and rendering routines.

game_board.py: Manages the game grid, boundaries, and layout.

game_object.py: Parent base class for all entities in the game.

player.py: Defines player attributes, movements, and actions.

monster.py: Implements enemy/monster behavior and AI logic.

bullet.py: Controls projectile creation, trajectory, and collision logic.

reward.py: Handles collectibles, power-ups, and score rewards.

settings.py: Stores global configuration variables (screen dimensions, frame rates, colors, key bindings).

requirements.txt: Lists all external Python dependencies required to run the game.

pytest.ini / tests/: Automated test configurations and test suites.

🚀 How to Run the Game

Follow these instructions to set up and run the game on your local machine:

1. Prerequisites

Ensure you have Python 3.x installed on your system.

2. Install Dependencies

Open a terminal or command prompt in the project directory and install the necessary packages using:

pip install -r requirements.txt


3. Launch the Game

To start playing, run the main entry point file:

python main.py


🧪 Running Unit Tests

To run the project test suite using pytest, execute:

pytest


🛠️ Features & Highlights

OOP Architecture: Clean, modular structure utilizing inheritance and encapsulation (game_object.py extended by player.py, monster.py, etc.).

Dynamic Gameplay: Move around, dodge enemies, shoot projectiles, and collect rewards.

Customizable Settings: Easily adjust screen parameters and game balance in settings.py.

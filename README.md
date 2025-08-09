# Project 2: Wumpus World Agent - Class of Introduction to Artificial Intelligence
## Project structure

```
ai-project02-23clc01/
├── assets/                  # All visual assets for the GUI
│   ├── buttons/             # Button sprites
│   ├── font/                # Bitmap font for text rendering
│   └── images/              # Game sprites
├── gui/                     # Pygame-based GUI
│   ├── board/               # Modules for rendering the game board
│   │   ├── background_renderer.py
│   │   ├── board_compositor.py
│   │   ├── entity_renderer.py
│   │   ├── image_manager.py
│   │   └── knowledge_renderer.py
│   ├── menu/                # Modules for the main menu and UI elements
│   │   ├── button.py
│   │   ├── menu_compositor.py
│   │   ├── menu_logic.py
│   │   └── menu_ui.py
│   ├── game_controller.py   # Main game loop and event handling
│   └── info_panel.py        # UI panel for displaying game state and percepts
├── agent_knowledge.py       # Represents the agent's beliefs about the world
├── environment.py           # Wumpus World simulator
├── hybrid_agent.py          # The main intelligent agent logic
├── inference_engine.py      # Inference engine using propositional logic
├── planning.py              # Pathfinding module (A*, Dijkstra)
├── random_agent.py          # Random-moving agent
├── main.py                  # Entry-point that launches the GUI
└── README.md                # You are here
```
### Key modules & classes (high-level)

* `environment.py` – WumpusWorld class that models the N×N grid, manages game elements (Pits, Wumpus, Gold), and provides percepts to the agent.
* `hybrid_agent.py` – The main HybridAgent that integrates inference and planning to make intelligent decisions.
* `inference_engine.py` – Implements the agent's logic for deducing the status of cells (safe, dangerous, unknown) based on known rules and incoming percepts.
* `planning.py` – Implements search algorithms to find the safest and most efficient path.
* `gui/game_controller.py` – The central component of the GUI, orchestrating the main game loop, rendering, and user input.
* `gui/board/` & `gui/menu/` – Specialized sub-packages that handle all visual aspects of the game board and user interface menus, respectively.
* `assets/` – Contains all the necessary visual components (sprites, fonts, buttons) required by the GUI.

---

## Installation & Running

> Requires **Python ≥ 3.10**

1. Clone the repository:
   ```bash
   git clone https://github.com/nhquana2/ai-project01-23clc01.git
   cd ai-project01-23clc01
   ```
2. (Optional) create a virtual environment with python venv or conda:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

   ```bash
   conda create -n rush_hour python==3.10
   conda activate rush_hour
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the GUI:
   ```bash
   python main.py
   ```

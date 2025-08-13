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
├── map/                     # Map configuration files
│   └── map.json             # Environment configurations for testing
├── results/                 # Test results and performance analysis
│   ├── comparison_results.csv        # Performance comparison data
│   ├── comparison_summary.json       # Summary of agent comparisons
│   ├── testcases_results_hybrid.csv  # Hybrid agent test results
│   ├── testcases_results_summary.json # Test summary statistics
│   ├── final_map_state_*.txt        # Final game states for each map
│   └── log_*.txt                    # Action logs for each test map
├── testcases/               # Predefined test cases
│   └── map*.json            # A test map
├── agent_knowledge.py       # Represents the agent's knowledge about the world
├── environment.py           # Wumpus World Environment simulator
├── hybrid_agent.py          # The main intelligent agent 
├── inference_engine.py      # Inference engine using propositional logic
├── inference.py             # DPLL algorithm and knowledge base implementation
├── planning.py              # Pathfinding module using A*
├── random_agent.py          # Random agent
├── run_comparison.py        # Script to compare hybrid vs random agent performance
├── run_hybrid_testcases.py  # Script to run hybrid agent on predefined test cases
├── test.py                  # For testing, debugging code
├── main.py                  # Entry-point that launches the GUI
├── requirements.txt         # Python dependencies
└── README.md                # You are here
```
### Key modules & classes (high-level)

* `environment.py` – WumpusWorld class that models the N×N grid, manages game elements (Pits, Wumpus, Gold), and provides percepts to the agent.
* `hybrid_agent.py` – The main HybridAgent that integrates inference and planning to make intelligent decisions.
* `inference_engine.py` – Implements the agent's logic for deducing the status of cells (safe, dangerous, unknown) based on known rules and incoming percepts.
* `inference.py` – Core inference module implementing the DPLL algorithm for satisfiability checking and knowledge base operations.
* `planning.py` – Implements search algorithms to find the safest and most efficient path.
* `random_agent.py` – A baseline agent that makes random moves for performance comparison.
* `agent_knowledge.py` – Manages the agent's beliefs and knowledge representation about the world state.
* `run_comparison.py` – Performance comparison script that benchmarks the hybrid agent against the random agent across multiple randomized environments (using map/map.json config file).
* `run_hybrid_testcases.py` – Test runner for evaluating the hybrid agent on predefined scenarios with action logging and final map state output.
* `test.py` – Development and debugging script for testing individual components and functionality.
* `gui/game_controller.py` – The central component of the GUI: the main game loop, rendering, and user input.
* `gui/board/` & `gui/menu/` – Specialized sub-packages that handle all visual aspects of the game board and user interface menus.
* `assets/` – Contains all the necessary visual components (sprites, fonts, buttons) required by the GUI.
* `map/` – Contains environment configuration files for different testing scenarios.
* `testcases/` – Predefined test maps with specific layouts for consistent evaluation.
* `results/` – Generated output directory containing performance metrics, logs, and analysis data from test runs.

---

## Installation & Running

> Requires **Python ≥ 3.10**

1. Clone the repository:
   ```bash
   git clone https://github.com/nhquana2/ai-project02-23clc01.git
   cd ai-project02-23clc01
   ```
2. (Optional) create a virtual environment with python venv or conda:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

   ```bash
   conda create -n wumpusworld python==3.10
   conda activate wumpusworld
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the GUI:
   ```bash
   python main.py
   ```

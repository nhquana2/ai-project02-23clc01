from agent_knowledge import MapKnowledge, CellStatus
from inference import KnowledgeBase
from typing import Optional, Set, Tuple

class InferenceEngine:
    def __init__(self, knowledge: MapKnowledge):
        self.knowledge = knowledge
        self.kb: Optional[KnowledgeBase] = None
        self.processed_cells: Set[Tuple[int, int]] = set()

    @staticmethod
    def _pos_to_symbol(prefix: str, x: int, y: int) -> str:
        return f"{prefix}_{x}_{y}"

    def _add_biconditional(self, kb: KnowledgeBase, percept_prefix: str, x: int, y: int, cause_prefix: str, has_percept: bool):
        p_sym = self._pos_to_symbol(percept_prefix, x, y)
        neighbors = self.knowledge.get_neighbors(x, y)
        cause_symbols = [self._pos_to_symbol(cause_prefix, nx, ny) for nx, ny in neighbors]
        
        # Add P <=> (C1 v C2 v ...)
        if has_percept:
            kb.tell(frozenset([(p_sym, True)])) # P is true
            # P => (C1 v C2 v ...)  is  ~P v C1 v C2 v ...
            kb.tell(frozenset([(p_sym, False)] + [(c, True) for c in cause_symbols]))
        else:
            kb.tell(frozenset([(p_sym, False)])) # P is false
            # ~P => ~(C1 v C2 v ...) is ~P => (~C1 ^ ~C2 ^ ...)
            # which means (~P => ~C1), (~P => ~C2), ...
            # which gives (P v ~C1), (P v ~C2), ...
            for cause_sym in cause_symbols:
                kb.tell(frozenset([(p_sym, True), (cause_sym, False)]))

    def _initialize_kb(self):
        if self.kb is None:
            self.kb = KnowledgeBase()
            # initial value
            self.kb.tell(frozenset([(self._pos_to_symbol("P", 0, 0), False)]))
            self.kb.tell(frozenset([(self._pos_to_symbol("W", 0, 0), False)]))

    def run_inference(self, agent_pos: tuple = None, action_count: int = 0, moving_wumpus_mode: bool = False):
        # In moving wumpus mode, reset KB every 5 actions (when wumpus moves)
        print(f"Action count: {action_count}")
        if moving_wumpus_mode and action_count > 0 and action_count % 5 == 0:
            self.kb = None
            self.processed_cells.clear()
            print("Resetting KB")
        
        self._initialize_kb()
        
        # Add facts from visited cells
        for (x, y), cell in self.knowledge.grid.items():
            if cell.visited and (x, y) not in self.processed_cells:
                self.kb.tell(frozenset([(self._pos_to_symbol("P", x, y), False)]))
                self.kb.tell(frozenset([(self._pos_to_symbol("W", x, y), False)]))
                self._add_biconditional(self.kb, "B", x, y, "P", cell.breeze)
                self._add_biconditional(self.kb, "S", x, y, "W", cell.stench)
                self.processed_cells.add((x, y))
        
        if agent_pos is not None:
            query_cells = self.knowledge.get_neighbors(agent_pos[0], agent_pos[1])
            query_cells.append(agent_pos)
        else:
            query_cells = [(x, y) for (x, y), cell in self.knowledge.grid.items() if not cell.visited]
        
        # Query adjacent cells
        for (x, y) in query_cells:
            cell = self.knowledge.get_cell(x, y)
            if cell is None or cell.visited:
                continue
                
            # Check for confirmed pit
            if self.kb.ask(frozenset([(self._pos_to_symbol("P", x, y), True)])):
                self.knowledge.update_cell_status(x, y, CellStatus.PIT)
                continue
            # Check for confirmed wumpus
            if self.kb.ask(frozenset([(self._pos_to_symbol("W", x, y), True)])):
                self.knowledge.update_cell_status(x, y, CellStatus.WUMPUS)
                continue

            # Check for safety (~P ∧ ~W)
            is_not_pit = self.kb.ask(frozenset([(self._pos_to_symbol("P", x, y), False)]))
            is_not_wumpus = self.kb.ask(frozenset([(self._pos_to_symbol("W", x, y), False)]))
            if is_not_pit and is_not_wumpus:
                self.knowledge.update_cell_status(x, y, CellStatus.SAFE)
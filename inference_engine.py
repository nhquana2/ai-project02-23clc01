from agent_knowledge import MapKnowledge, CellStatus
from inference import KnowledgeBase

class InferenceEngine:
    def __init__(self, knowledge: MapKnowledge):
        self.knowledge = knowledge

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

    def run_inference(self):
        kb = KnowledgeBase()
        
        # Add initial facts: (0,0) is safe
        kb.tell(frozenset([(self._pos_to_symbol("P", 0, 0), False)]))
        kb.tell(frozenset([(self._pos_to_symbol("W", 0, 0), False)]))

        # Add facts from visited cells
        for (x, y), cell in self.knowledge.grid.items():
            if cell.visited:
                kb.tell(frozenset([(self._pos_to_symbol("P", x, y), False)]))
                kb.tell(frozenset([(self._pos_to_symbol("W", x, y), False)]))
                self._add_biconditional(kb, "B", x, y, "P", cell.breeze)
                self._add_biconditional(kb, "S", x, y, "W", cell.stench)
        
        # Query every unvisited cell
        for (x, y), cell in self.knowledge.grid.items():
            if not cell.visited:
                # Check for confirmed pit
                if kb.ask(frozenset([(self._pos_to_symbol("P", x, y), True)])):
                    self.knowledge.update_cell_status(x, y, CellStatus.PIT)
                    continue
                # Check for confirmed wumpus
                if kb.ask(frozenset([(self._pos_to_symbol("W", x, y), True)])):
                    self.knowledge.update_cell_status(x, y, CellStatus.WUMPUS)
                    continue

                # Check for safety (~P ∧ ~W)
                is_not_pit = kb.ask(frozenset([(self._pos_to_symbol("P", x, y), False)]))
                is_not_wumpus = kb.ask(frozenset([(self._pos_to_symbol("W", x, y), False)]))
                if is_not_pit and is_not_wumpus:
                    self.knowledge.update_cell_status(x, y, CellStatus.SAFE)
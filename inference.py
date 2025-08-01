from typing import Set, Tuple, List, FrozenSet, Optional, Dict, Union

Literal = Tuple[str, bool] # (symbol, truth-value)
Clause = FrozenSet[Literal] # Disjunction of literals
Clauses = Set[Clause] # Set of clauses (CNF)
Model = Dict[str, bool] # Model (assignment of symbols to truth values)

def negate_literal(lit: Literal) -> Literal:
    """Negates a literal."""
    sym, val = lit
    return (sym, not val)

def dpll_satisfiable(clauses: Clauses) -> Union[Model, bool]:
    """
    Checks if a set of CNF clauses is satisfiable using the DPLL algorithm.
    Returns a satisfying model if satisfiable, otherwise returns False.
    """
    symbols = list(set(sym for clause in clauses for sym, _ in clause))
    return dpll(clauses, symbols, {})

def dpll(clauses: Clauses, symbols: List[str], model: Model) -> Union[Model, bool]:
    """
    DPLL recursive helper func
    """
    simplified_clauses = set()
    unknown_clauses = [] # Clauses that are not yet true

    for clause in clauses:
        is_clause_true = False
        new_clause = set()
        for literal in clause:
            symbol, value = literal
            if symbol in model:
                if model[symbol] == value:
                    is_clause_true = True # Literal true -> clause true
                    break
            else:
                new_clause.add(literal) # This literal is unassigned

        if is_clause_true:
            continue # Clause is satisfied, no further checks needed
        
        if not new_clause:
            return False # Contradiction: clause is false
            
        unknown_clauses.append(frozenset(new_clause))

    clauses = set(unknown_clauses)
    
    if not clauses:
        return model # All clauses were satisfied

    # Heuristic: Pure Symbol Elimination
    all_symbols_in_unknown = set(s for c in clauses for s, v in c)
    for symbol in all_symbols_in_unknown:
        is_positive, is_negative = False, False
        for clause in clauses:
            for s, v in clause:
                if s == symbol:
                    if v: is_positive = True
                    else: is_negative = True
        
        if is_positive != is_negative: # It's a pure symbol
            new_model = model.copy()
            new_model[symbol] = is_positive
            remaining_symbols = [s for s in symbols if s != symbol]
            return dpll(clauses, remaining_symbols, new_model)

    # Heuristic: Unit Clause Propagation
    for clause in clauses:
        if len(clause) == 1:
            literal = next(iter(clause))
            symbol, value = literal
            new_model = model.copy()
            new_model[symbol] = value
            remaining_symbols = [s for s in symbols if s != symbol]
            return dpll(clauses, remaining_symbols, new_model)

    # Branching: Pick a symbol and try both True/ False
    if not all_symbols_in_unknown:
        return model

    p = next(iter(all_symbols_in_unknown))
    remaining_symbols = [s for s in symbols if s != p]

    # Try p = True
    model_true = model.copy()
    model_true[p] = True
    res = dpll(clauses, remaining_symbols, model_true)
    if res:
        return res

    # Try p = False
    model_false = model.copy()
    model_false[p] = False
    return dpll(clauses, remaining_symbols, model_false)


class KnowledgeBase:
    def __init__(self):
        self.clauses: Clauses = set()

    def tell(self, clause: Clause):
        """Add one CNF clause (a frozenset of literals)."""
        self.clauses.add(clause)

    def tell_all(self, clauses: List[Clause]):
        """Add multiple clauses at once."""
        self.clauses.update(clauses)

    def ask(self, query: Clause) -> bool:
        """
        Return True if KB ENTAILS query using DPLL.
        This checks if (KB AND ~query) is unsatisfiable.
        """
        # Negate query: ~(L1 ∧ … ∧ Ln) = ~L1 ∨ … ∨ ~Ln
        negated_query_clause = frozenset(negate_literal(lit) for lit in query)

        # Combine KB clauses with the negated query (KB AND ~query)
        clauses_to_check = set(self.clauses)
        clauses_to_check.add(negated_query_clause)

        # If dpll_satisfiable returns False -> clause is unsatisfiable.
        # SO KB entails query.
        return not dpll_satisfiable(clauses_to_check)
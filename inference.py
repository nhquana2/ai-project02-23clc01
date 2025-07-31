from typing import Set, Tuple, List, FrozenSet

Literal   = Tuple[str, bool]         # literal = (symbol, truth-value)
Clause    = FrozenSet[Literal]       # disjunction of literals
Clauses   = Set[Clause]              # set of clauses (CNF)


def negate_literal(lit: Literal) -> Literal:
    sym, val = lit
    return (sym, not val)


def pl_resolve(c1: Clause, c2: Clause) -> List[Clause]:
    """Return list of resolvent clauses for c1 and c2."""
    resolvents: List[Clause] = []
    for sym, val in c1:
        complement = (sym, not val)
        if complement in c2:
            new_clause = (c1 - {(sym, val)}) | (c2 - {complement})
            resolvents.append(frozenset(new_clause))
    return resolvents


def pl_resolution(clauses: Clauses) -> bool:
    """Run PL-Resolution on given clauses; return True if contradiction found."""
    new: Set[Clause] = set()
    clause_list = list(clauses)
    n = len(clause_list)
    for i in range(n):
        for j in range(i+1, n):
            for resolvent in pl_resolve(clause_list[i], clause_list[j]):
                if not resolvent:    # empty clause
                    return True
                new.add(resolvent)
    if new.issubset(clauses):
        return False
    clauses |= new
    return pl_resolution(clauses)

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
        Return True if KB ENTAILS query.
        query is L1 ∧ … ∧ Ln (conjunction of literals).
        Implements PL-Resolution: KB AND ~(L1 ∧ … ∧ Ln) ENTAILS empty.
        """
        # negate the conjunction of query literals as a single clause: ¬(L1∧...∧Ln) = ¬L1 ∨ ... ∨ ¬Ln
        negated_query_clause = frozenset(negate_literal(lit) for lit in query)
        clauses = set(self.clauses)
        clauses.add(negated_query_clause)
        return pl_resolution(clauses)

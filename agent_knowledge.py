from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
from environment import Percept, Direction

class CellStatus(Enum):
    UNKNOWN = "?"
    WUMPUS = "W"
    PIT = "P"
    SAFE = "OK"


@dataclass
class Cell:
    status: CellStatus = CellStatus.UNKNOWN
    visited: bool = False
    stench: Optional[bool] = None
    breeze: Optional[bool] = None
    glitter: Optional[bool] = None
    

class MapKnowledge:
    def __init__(self, size: int, num_wumpus: int):
        self.size = size
        self.num_wumpus = num_wumpus

        # Grid mapping (x, y) -> Cell object
        self.grid: Dict[Tuple[int, int], Cell] = {
            (x, y): Cell() for x in range(size) for y in range(size)
        }

        start_cell = self.get_cell(0, 0)
        start_cell.status = CellStatus.SAFE
    
    def get_cell(self, x: int, y: int) -> Cell: 
        return self.grid.get((x, y))
    
    # Get neighbor coordinates
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = []
        for direction in Direction:
            dx, dy = direction.value 
            nx, ny= x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors
    
    def update_after_visit(self, x: int, y: int, percept: Percept):
        cell = self.get_cell(x, y)
        if not cell.visited:
            cell.visited = True
            cell.status = CellStatus.SAFE
            cell.stench = percept.stench
            cell.breeze = percept.breeze
            cell.glitter = percept.glitter

    def update_cell_status(self, x: int, y: int, status: CellStatus):
        cell = self.get_cell(x, y)
        cell.status = status

    def wumpus_is_dead(self):
        self.num_wumpus -= 1
    
    def reset_wumpus_knowledge(self):
        for (x, y), cell in self.grid.items():
            if cell.visited:
                cell.stench = None
                # cell.visited = False
            
            if cell.status == CellStatus.WUMPUS:
                cell.status = CellStatus.UNKNOWN

            if cell.status == CellStatus.SAFE:
                cell.status = CellStatus.UNKNOWN
    
    def display_agent_view(self, agent_pos: Tuple[int, int], agent_dir: Enum):
        print("\n" + "="*20 + " Agent's Knowledge " + "="*20)
        for y in range(self.size - 1, -1, -1):
            row = []
            for x in range(self.size):
                if (x, y) == agent_pos:
                    if agent_dir == agent_dir.NORTH: cell_char = "^"
                    elif agent_dir == agent_dir.EAST: cell_char = ">"
                    elif agent_dir == agent_dir.SOUTH: cell_char = "v"
                    else: cell_char = "<"
                    row.append(f" {cell_char} ")
                else:
                    cell = self.get_cell(x, y)
                    row.append(f" {cell.status.value} ")
            print(" ".join(row))


    def smart_reset(self):
        """
        Thực hiện reset kiến thức một cách thông minh khi Wumpus di chuyển.
        Không thay đổi cờ 'visited'.
        """
        # 1. Tìm tất cả các ô có thể có Wumpus (là các ô UNKNOWN)
        potential_wumpus_neighbors = set()
        for (x, y), cell in self.grid.items():
            # Quên vị trí Wumpus cũ và tất cả dữ liệu stench
            if cell.status == CellStatus.WUMPUS:
                cell.status = CellStatus.UNKNOWN
            cell.stench = None

            # Nếu một ô là UNKNOWN, các hàng xóm của nó cần được xem xét lại
            if cell.status == CellStatus.UNKNOWN:
                neighbors = self.get_neighbors(x, y)
                for nx, ny in neighbors:
                    potential_wumpus_neighbors.add((nx, ny))

        # 2. "Hạ cấp" các ô SAFE liền kề với khu vực UNKNOWN
        # Đây là bước then chốt!
        for x, y in potential_wumpus_neighbors:
            cell = self.get_cell(x, y)
            # Nếu một ô đã từng được cho là an toàn (SAFE) nhưng bây giờ nó lại
            # nằm cạnh một ô UNKNOWN, thì sự an toàn của nó không còn chắc chắn 100%.
            # Chúng ta hạ cấp nó về UNKNOWN để hệ suy luận và lập kế hoạch xử lý lại.
            if cell.status == CellStatus.SAFE:
                cell.status = CellStatus.UNKNOWN

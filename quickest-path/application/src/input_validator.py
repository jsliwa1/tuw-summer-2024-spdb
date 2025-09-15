import networkx as nx
from src.graph_utils import calculate_bbox

# klasa mająca na celu walidację danych wprowadzonych przez użytkownika
# sprawdza m.in. to, czy liczba podanych punktów nie przekracza dopuszczalnej wartości max
# oraz czy podane punkty znajdują się w bbox stworzonego grafu
class InputValidator:
    
    def __init__(self, max_points_allowed: int = 7):
        self._max_points_allowed = max_points_allowed
        self._bbox = ()
        
    
    def validate_number_of_points(self, points: list) -> bool:
        return len(points) <= self._max_points_allowed
    
    
    def validate_points_within_bbox(self, G: nx.MultiDiGraph, points: list) -> bool:
        if len(self._bbox) == 0:
            self._bbox = calculate_bbox(G)
        
        for point in points:
            lon = point[0]
            lat = point[1]
            if lon < self._bbox[0] or lon > self._bbox[2] or lat < self._bbox[1] or lat > self._bbox[3]:
                return False
            
        return True
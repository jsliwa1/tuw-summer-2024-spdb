import osmnx as ox
import networkx as nx
from typing import Tuple


# klasa ma na celu umożliwienie usługi geomapowania
# otrzymując adres w formie tekstowej, zwraca jego współrzędne geograficzne
# dla zadanych współrzędnych, znajduje najbliższy możliwy węzeł w grafie
class GeoMapper:
    
    def map_to_coordinates(self, address: str) -> Tuple[float, float]:
        y, x = ox.geocode(address) # throws InsufficientResponseError
        return (y, x)
    
    def map_to_node(self, G: nx.MultiDiGraph, coordinates: tuple) -> int:
        return ox.distance.nearest_nodes(G, coordinates[1], coordinates[0])
    

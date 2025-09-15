import networkx as nx
import heapq as h
from src.left_turn_handler import LeftTurnHandler
from src.graph_utils import calculate_heuristic


# klasa ma na celu umożliwić znajdowanie najszybszej ścieżki przejazdu między dwoma (!) węzłami w grafie
# wykorzystywany jest algorytm A* z ustaloną wcześniej heurystyką
# zakładającą maksymalny dopuszczlny maxspeed od następnego węzła w linii prostej do celu
# można modyfikować heurystykę poprzez zmianę wartości maksymalnej dopuszczalnej prędkości
class BestPathFinder:
    
    def __init__(self, left_turn_handler: LeftTurnHandler, heur_maxspeed: int = 120):
        self._left_turn_handler = left_turn_handler
        self._heur_maxspeed = heur_maxspeed

    
    def find_shortest_path(self, G: nx.MultiDiGraph, source: int, dest: int) -> list:
        # inicjalizacja:
        # definiujemy kolejkę priorytetową węzłów do przetworzenia
        priority_queue = []
        h.heappush(priority_queue, (0, source))
        # definiujemy słownik przechowujący poprzedników na najkrótszej dotychczas znanej ścieżce
        predecessors = {source: -1}
        # definiujemy słownik rzeczywistych długości na najkrótszej znalezionej ścieżce
        real_dist = {node: float('inf') for node in G.nodes}
        real_dist[source] = 0
        # definiujemy zbiór przetworzonych węzłów, aby żaden węzeł nie był przetworzony 2 razy
        visited_nodes = set()
        
        # przetwarzamy kolejne węzły do momentu znalezienia węzła końcowego lub wyczerpania kolejki
        while len(priority_queue) > 0:
            
            # wyciągnij z kolejki priorytetowej węzeł o najniższym oczekiwanym koszcie
            _, current_node = h.heappop(priority_queue)
            
            # jeżeli węzeł był już wcześniej odwiedzony, przejdź dalej
            if current_node in visited_nodes:
                continue
            
            # jeśli doszliśmy do celu - zwracamy ścieżkę
            if current_node == dest:
                return self._reconstruct_path(predecessors, current_node)#, real_dist[dest]
            
            # następnie badamy wszystkie sąsiednie węzły osiągalne z obecnego
            for edge in nx.edges(G, [current_node]):
                
                # zapisz id sąsiedniego węzła
                neighbor = G.edges[(edge[0], edge[1], 0)]["v"]
                
                # zapisz dystans pomiędzy węzłami (czyli oczekiwany czas przejazdu)
                edge_length = G.edges[(edge[0], edge[1], 0)]["estimated_time"]
                
                # sprawdź, czy rozpatrywany jest skręt w lewo
                # jeśli tak, dolicz odpowiednią karę
                if current_node != source:
                    if self._left_turn_handler.is_turn_left(G, predecessors[current_node], current_node, neighbor):
                        edge_length += self._left_turn_handler.calculate_penalty(G, predecessors[current_node], current_node, neighbor)
                    
                # oblicz oczekiwany koszt dojazdu ze startu do sąsiada przez current_node
                dist_start_neighbor = real_dist[current_node] + edge_length
                
                # jeśli czas dojazdu do sąsiada przez obecny punkt jest mniejszy niż najlepszy dotychczas wykryty,
                # zapisz informację o znalezieniu lepszej trasy
                if dist_start_neighbor < real_dist[neighbor]:
                    
                    # uaktualnij poprzednika
                    predecessors[neighbor] = current_node
                    
                    # uaktualnij rzeczywisty czas dojazdu od startu do sąsiada
                    real_dist[neighbor] = dist_start_neighbor
                    
                    # dodaj sąsiada do kolejki priorytetowej z estymowanym czasem dojazdu
                    # na który składa się suma dotychczasowego czasu dojazdu do węzła oraz wyniku heurystyki
                    heur_est = calculate_heuristic(G, neighbor, dest, self._heur_maxspeed)
                    h.heappush(priority_queue, (dist_start_neighbor + heur_est, neighbor))
                
            # dodaj właśnie przetwrzony węzeł do zbioru, aby nie był on przetwrzony ponownie
            visited_nodes.add(current_node)
        
        # nie znaleziono ścieżki
        raise RuntimeError(f"Algorytmowi nie udało się znaleźć ścieżki pomiędzy {source} a {dest}.")
        
        
        
    def _reconstruct_path(self, predecessors: dict, current_node: int) -> list:
        path = [current_node]
        while current_node in predecessors:
            current_node = predecessors[current_node]
            if current_node != -1:
                path.insert(0, current_node)
        return path
    
    
    
    

import networkx as nx
import pickle
import sys
from pyrosm import OSM, get_data
from src.graph_utils import fill_max_speed, clean_edges_data

# klasa ta ma za zadanie dostarczyć gotowy graf przedstawiający sieć drogową
# na podstawie wartości parametru albo wczytuje graf z wcześniej zapisanego pliku
# albo tworzy go od nowa, pobierając dane z OSM przy użyciu biblioteki pyrosm
# zwracany graf jest grafem sierowanym, który pomiędzy dwoma węzłami może mieć więcej niż jedną krawędź
# implementacja grafu, z której korzystamy, pochodzi z biblioteki networkx
class GraphProvider:
    
    
    # główna metoda udostępniana na zewnątrz
    # pozwala wywołującemu ją zbudować gotowy graf, na którym można puszczać algorytmy
    def build_graph(self, region: str = "Warsaw") -> nx.MultiDiGraph:
        
        # pobieramy dane, tworzymy tabelę węzłów oraz krawędzi
        osm = OSM(get_data(region, directory="."))
        nodes, edges = osm.get_network(nodes=True, network_type="driving")
        
        # usuwamy zbędne kolumny z tabeli reprezentującej węzły
        nodes.drop(columns=["visible", "timestamp", "changeset", "version"], inplace=True)
        
        # z tabeli zawierających krawędzie usuwamy rzędy, o których wiemy, że będą nieprzydatne
        # usprawni to proces tworzenia grafu
        clean_edges_data(edges)
        
        # tam, gdzie brakuje info o limicie prędkości, uzupełniamy je na podstawie kategorii drogi
        edges["maxspeed"] = edges.apply(fill_max_speed, axis=1)
        
        # wyliczamy estymowany czas przejazdu daną krawędzią, co będzie stanowiło wagi w naszym grafie
        edges["estimated_time"] = edges.apply(lambda x: x["length"] / (x["maxspeed"] / 3.6), axis=1)
        
        # zbudowanie grafu na podstawie tabel z węzłami i krawędziami
        G = osm.to_graph(nodes, edges, graph_type="networkx", network_type="driving") # TODO if not suitable change to "driving+service"
        
        return G
    
    
    # w celu usprawnienia startu aplikacji przy wielokrotnym jej uruchamianiu
    # możliwe jest szybkie wczytanie gotowego grafu z pickle'a
    def read_graph_from_pickle(self, filepath: str = "graph.pkl") -> nx.MultiDiGraph:
        with open(filepath, "rb") as f:
            G_loaded = pickle.load(f)
        return G_loaded
    
    def save_graph_to_pickle(self, G: nx.MultiDiGraph, filepath: str = "graph.gpickle") -> bool:
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
                return True
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
        except:
            print("Unexpected Error: ", sys.exc_info()[0])
        finally:
            return False
import pandas as pd
import geopandas as gpd
import networkx as nx
import numpy as np


# metoda definiująca heurystykę obliczającą najbardziej optymistyczny czas przejazdu między dwoma punktami w grafie
# wyznacza odległość euklidesową między węzłami na podstawie ich współrzędnych
# a następnie wyznacza optymistyczny oczekiwany czas dojazdu przy założeniu,
# że istnieje droga w linii prostej o wysokim limicie prędkości 
def calculate_heuristic(G: nx.MultiDiGraph, current_node: int, destination_node: int, heur_maxspeed: int) -> float:

    # oblicz odległość euklidesową
    euclid_dist = calculate_euclid_dist(G, current_node, destination_node)
    
    # zwróć oczekiwany bardzo optymistyczny czas przejazdu
    return euclid_dist / (heur_maxspeed / 3600)
    

# metoda ma na celu wyznaczenie odległości euklidesowej pomiędzy dwoma węzłami w grafie
# wykorzystywane w tym celu są współrzędne geograficzne obu węzłów
# wynik zwracany jest w [km]
def calculate_euclid_dist(G: nx.MultiDiGraph, first_node: int, second_node: int) -> float:
    
    # pobierz dane o współrzędnych geogr. obu punktów
    lon_current = G.nodes[first_node]["x"]
    lat_current = G.nodes[first_node]["y"]
    lon_dest = G.nodes[second_node]["x"]
    lat_dest = G.nodes[second_node]["y"]
    R = 6371 # promień Ziemi w km 

    # zamień współrzędne w stopniach na radiany, a następnie oblicz współrzędne kartezjańskie
    x_curr = R * np.cos(np.radians(lat_current)) * np.cos(np.radians(lon_current))
    y_curr = R * np.cos(np.radians(lat_current)) * np.sin(np.radians(lon_current))
    z_curr = R * np.sin(np.radians(lat_current))
    
    x_dest = R * np.cos(np.radians(lat_dest)) * np.cos(np.radians(lon_dest))
    y_dest = R * np.cos(np.radians(lat_dest)) * np.sin(np.radians(lon_dest))
    z_dest = R * np.sin(np.radians(lat_dest))
    
    # oblicz i zwróć odległość euklidesową
    return np.sqrt((x_dest - x_curr)**2 + (y_dest - y_curr)**2 + (z_dest - z_curr)**2)
    

# metoda definiująca liniowy porządek dla dróg różnego typu (atrybut 'highway')
# w celu rozpoznawania zmiany kategorii drogi przy skręcie w lewo
# metoda zwraca -1, jeśli skręcamy w gorszą drogę, 0 jeśli w taką samą, 1 jeśli na lepszą
def compare_highways(from_highway: str, to_highway: str) -> int:
    custom_highway_order = {
            'motorway': 1,
            'trunk': 2,
            'primary': 3,
            'secondary': 4,
            'motorway_link': 5,
            'primary_link': 5,
            'trunk_link': 5,
            'tertiary': 6,
            'unclassified': 6,
            'secondary_link': 6
        }
    if custom_highway_order.get(from_highway, 7) < custom_highway_order.get(to_highway, 7):
        return -1
    elif custom_highway_order.get(from_highway, 7) == custom_highway_order.get(to_highway, 7):
        return 0
    else:
        return 1
    

# metoda wyznaczająca kąt w stopniach na podstawie sin i cos
def calculate_angle(sin: float, cos: float) -> float:
    return np.degrees(np.arctan2(sin, cos))

# metoda wyznaczająca cosinus kąta pomiędzy wektorami
def calculate_cos(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# metoda wyznaczająca sinus kąta pomiędzy wektorami
def calculate_sin(a: np.ndarray, b: np.ndarray) -> float:
    return (a[0]*b[1] - a[1]*b[0]) / (np.linalg.norm(a) * np.linalg.norm(b))


# metoda tworząca wektor pomiędzy dwoma węzłami w grafie
# dokonuje ona mapowania współrzędnych geograficznych (kątów) na płaszczyznę 2D
def get_vector_between_nodes(G: nx.MultiDiGraph, node_from: int, node_to: int) -> np.ndarray:
    R = 6371000 # promień Ziemi
    
    # wydobądź informacje o wsp. geograficznych obu punktów
    lon_from = G.nodes[node_from]['x']
    lat_from = G.nodes[node_from]['y']
    lon_to = G.nodes[node_to]['x']
    lat_to = G.nodes[node_to]['y']
    
    # zmapuj je na płaszczyznę 2D [m]
    x_from = R * np.radians(lon_from)
    y_from = R * np.radians(lat_from)
    x_to = R * np.radians(lon_to)
    y_to = R * np.radians(lat_to)
    
    # oblicz różnice między punktami na obu współrzęnych
    dx = x_to - x_from
    dy = y_to - y_from
    
    return np.array([dx, dy])


# metoda pozwalająca na wyznaczenie bbox na podstawie posiadanego grafu G
# ma to na celu późniejsze eliminowanie zapytań spoza obszaru objętego naszą mapą
def calculate_bbox(G: nx.MultiDiGraph) -> (float, float, float, float):
    min_lon = float("inf")
    min_lat = float('inf')
    max_lon = float('-inf')
    max_lat = float('-inf')
    
    for _, data in G.nodes(data=True):
        lon = data.get("y", None)
        lat = data.get("x", None)
        
        if lon is not None and lat is not None:
            if lon < min_lon:
                min_lon = lon
            if lon > max_lon:
                max_lon = lon
            if lat < min_lat:
                min_lat = lat
            if lat > max_lat:
                max_lat = lat
                
    return (min_lon, min_lat, max_lon, max_lat)
    

# metoda ma na celu uzupełnienie wartości "maxspeed", dla którego wiele krawędzi ma brakujące info
# na podstawie atrybutu "highway", który zawsze jest obecny
def fill_max_speed(row: pd.Series) -> int:
    if row["maxspeed"] == "PL:urban":
        return 50
    elif row["maxspeed"] == "30 mph":
        return 30
    elif row["maxspeed"] != None:
        return int(row["maxspeed"])
    elif row["highway"] == "motorway":
        return 140
    elif row["highway"] == "trunk":
        return 120
    elif row["highway"] == "primary":
        return 90
    elif row["highway"] == "secondary":
        return 70
    elif row["highway"] in ["motorway_link", "primary_link", "trunk_link"]:
        return 60
    elif row["highway"] in ["tertiary", "unclassified", "secondary_link"]:
        return 50
    else:
        return 30
    
    
# metoda mająca na celu oczyścić nasz zbiór potencjalnych krawędzi z punktów niebędących drogami
# pozbywamy się również wielu niepotrzebnych w naszym zastosowaniu atrybutów
# ma to na celu przyspieszenie generowania grafu    
def clean_edges_data(edges: gpd.geodataframe.GeoDataFrame):
        
    # wyznaczamy indeksy rzędów, które prawdopodobnie zawierają błędne dane
    index_1 = edges.index[edges["access"].isin(["no", "emergency", "military", "bus", "employees", "forestry"])]
    index_2 = edges.index[edges["area"].isin(["no", "yes"])]
    index_3 = edges.index[edges["bicycle"].isin(["designated", "destination", "dismount", "official", "permit"])]
    index_4 = edges.index[edges["foot"].isin(["designated", "destination", "permit"])]
    index_5 = edges.index[edges["highway"].isin(["bridleway", "cyclist_waiting_aid", "road", "steps", "cycleway", "path"])]
    index_6 = edges.index[edges["motorcar"].isin(["delivery", "destination", "forestry", "agricultural"])]
    index_7 = edges.index[edges["motor_vehicle"].isin(["delivery", "destination", "forestry", "agricultural", "official", "forestry"])]
    index_8 = edges.index[edges["service"].isin(["yard", "*", "da", "spur", "fire_road", "droga_wewnetrzna"])]
    index_9 = edges.index[edges["surface"].isin(["grass", "grass_paver", "rock", "paving_stones:30", "wood", "woodchips"])]
    index_10 = edges.index[edges["tracktype"].isin(["grade1", "grade2", "grade3", "grade4", "grade5"])] 
    
    # łączymy znalezione indeksy w jeden i dokonujemy usunięcia wątpliwej jakości rekordów
    indexes = index_1.union(index_2).union(index_3).union(index_4).union(index_5).union(index_6).union(index_7).union(index_8).union(index_9).union(index_10)
    edges.drop(indexes, inplace=True)
    
    # skorzystawszy z zawartych w danych kolumnach informacji, możemy się ich pozbyć
    edges.drop(columns=["access", "area", "bicycle", "busway", "cycleway", "est_width",
                        "foot", "footway", "int_ref", "lit", "motorcar", "motorroad",
                        "motor_vehicle", "overtaking", "passing_places", "psv", "service",
                        "segregated", "sidewalk", "smoothness", "surface", "tracktype", "turn",
                        "width", "timestamp", "version", "osm_type"], inplace=True)

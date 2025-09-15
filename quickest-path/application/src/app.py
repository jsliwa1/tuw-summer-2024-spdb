from src.graph_provider import GraphProvider
from src.left_turn_handler import LeftTurnHandler
from src.input_validator import InputValidator
from src.geo_mapper import GeoMapper
from src.a_star import BestPathFinder
from src.travel_sales_solver import TravelSalesmanSolver
from osmnx._errors import InsufficientResponseError

# klasa reprezentująca działanie aplikacji
# jest to obiekt, którego publiczne metody są docelowo udostępnianie na zewnątrz
# na starcie inicjalizowany jest stan obiektu, tzn tworzone są różne obiekty składające się na apkę
# gdy stan już został zainicjalizowany, udostępniona jest metoda wywoływana w celu rozwiązania TSP
class App:
    
    # parametry podawane aplikacji na starcie:
        
    # read_graph_from_pickle - czy graf ma być wczytany z pliku pkl (True), czy budowany od zera (False)
    # pickle_filepath - ścieżka do pliku .pkl w przypadku czytania z pliku
    # region - region, dla którego budujemy graf (domyślnie Warszawa w naszym zastosowaniu)
    # min_angle_left_turn - minimalny kąt odchylenia od kierunku jazdy, aby skręt klasyfikowany był jako skręt w lewo
    # penalty_to_better_road - kara za skręt w lewo w drogę o wyższym standardzie [s]
    # penalty_to_equal_road - kara za skręt w lewo w drogę o równym standardzie [s]
    # penalty_to_worse_road - kara za skręt w lewo w drogę o niższym standardzie [s]
    # heur_maxspeed - maksymalna prędkość hipotetycznej drogi wykorzystywana w heurystyce A* (jak bardzo eksplorujemy graf)
    
    def __init__(self,
                 read_graph_from_pickle: bool = False,
                 pickle_filepath: str = "",
                 region: str = "Warsaw",
                 max_points_allowed: int = 7,
                 min_angle_left_turn: float = 45.0,
                 penalty_to_better_road: float = 30.0,
                 penalty_to_equal_road: float = 20.0,
                 penalty_to_worse_road: float = 10.0,
                 heur_maxspeed: int = 140):
        
        self._is_state_initialized = False
        self._read_graph_from_pickle = read_graph_from_pickle
        self._pickle_filepath = pickle_filepath
        self._region = region
        self._max_points_allowed = max_points_allowed
        self._min_angle_left_turn = min_angle_left_turn
        self._penalty_to_better_road = penalty_to_better_road
        self._penalty_to_equal_road = penalty_to_equal_road
        self._penalty_to_worse_road = penalty_to_worse_road
        self._heur_maxspeed = heur_maxspeed
        
        self._G = None
        self._geo_mapper = None
        self._input_validator = None
        self._left_turn_handler = None
        self._best_path_finder = None
        self._travel_sales_solver = None
        self._last_query_coordinates = None
        
    
    # metoda odpowiedzialna za inicjalizację stanu na starcie aplikacji
    def initialize_state(self):
        
        # jeśli stan został już wcześniej zainicjalizowany, nie rób nic
        if self._is_state_initialized:
            return 
        
        # wczytaj / stwórz graf reprezentujący sieć drogową
        graph_provider = GraphProvider()
        if self._read_graph_from_pickle:
            self._G = graph_provider.read_graph_from_pickle(self._pickle_filepath)
        else:
            self._G = graph_provider.build_graph(self._region)
        
        # zainicjalizuj obiekty wymagane do funkcjonowania aplikacji
        
        # obiekt odpowiedzialny za geomapowanie
        self._geo_mapper = GeoMapper()
        
        # obiekt odpowiedzialny za walidację danych wprowadzanych przy zapytaniu
        self._input_validator = InputValidator(self._max_points_allowed)
        
        # obiekt odpowiedzialny za rozpoznawanie i naliczanie kary za skręty w lewo
        self._left_turn_handler = LeftTurnHandler(self._penalty_to_better_road, self._penalty_to_equal_road, 
                                                  self._penalty_to_worse_road, self._min_angle_left_turn)
        
        # obiekt odpowiedzialny za obliczanie najszybszej ścieżki pomiędzy dwoma punktami (A*)
        self._best_path_finder = BestPathFinder(self._left_turn_handler, self._heur_maxspeed)
        
        # obiekt odpowiedzialny za zachłanny algorytm aproksymacyjny rozwiązujący TSP
        self._travel_sales_solver = TravelSalesmanSolver(self._best_path_finder)
        
        # zaktualizuj info o poprawnej inicjalizacji stanu
        self._is_state_initialized = True
        
        
    # metoda udostępniana na zewnątrz, by móc wykonywać zapytania o najkrótszą ścieżkę
    # jako parametr przyjmuje listę adresów punktów, które należy odwiedzić
    # pierwszy punkt w liście jest punktem startowym, kolejność odwiedzania pozostałych jest wyznaczana przez algorytm
    def run_query(self, addresses: list) -> list:
        
        # jeśli stan nie został zainicjalizowany, przerwij działanie
        if not self._is_state_initialized:
            raise RuntimeError("Nie można wykonywać zapytań bez uprzedniego zainicjalizowania stanu.")
        
        # sprawdź, czy nie podano zbyt wielu punktów
        if not self._input_validator.validate_number_of_points(addresses):
            raise RuntimeError("Podano zbyt wiele punktów do odwiedzenia!")
    
        # zmapuj adresy na współrzędne geograficzne punktów w formie (szerokość geo., długość geo.)
        points_coordinates = []
        try:
            points_coordinates = [self._geo_mapper.map_to_coordinates(address) for address in addresses]
        except InsufficientResponseError as e:
            raise RuntimeError(f"Nie udało się zrealizować geomapowania jednego z punktów: {str(e).replace("'", "")}")
        
        # sprawdź, czy każdy z punktów znajduje się w bbox wczytanej mapy
        if not self._input_validator.validate_points_within_bbox(self._G, points_coordinates):
            raise RuntimeError("Przynajmniej jeden z zadanych adresów nie znajduje się w zasięgu posiadanej mapy.")
        
        # zapisz info o ostatnim przetwarzanym zapytaniu
        self._last_query_coordinates = points_coordinates
        
        # wiedząc, że adresy są w zasięgu naszej mapy, mapujemy każdy z nich na najbliższy mu geograficznie węzeł w grafie
        nodes_to_visit = [self._geo_mapper.map_to_node(self._G, point_coor) for point_coor in points_coordinates]
        
        # mające listę węzłów do odwiedzenia, szukamy rozwiązania zadanego TSP
        discovered_path = self._travel_sales_solver.solve(self._G, nodes_to_visit)
        
        # zwracamy znalezioną ścieżkę
        return discovered_path
        

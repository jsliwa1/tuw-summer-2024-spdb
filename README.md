# SPDB – Znajdowanie najlepszej trasy

## Autorzy
- Jakub Śliwa
- Jakub Dzięgielewski

## Opis projektu
Projekt został zrealizowany w ramach przedmiotu **Przestrzenne Bazy Danych** na Politechnice Warszawskiej.  
Celem aplikacji jest **wyznaczanie najszybszej trasy przejazdu pomiędzy wieloma adresami**, przy jednoczesnym **minimalizowaniu liczby skrętów w lewo**.  

Rozwiązanie korzysta z danych **OpenStreetMap** i obejmuje:
- geomapowanie adresów przy użyciu **osmnx** i **Nominatim API**,  
- budowę grafu sieci drogowej w oparciu o **pyrosm** i **networkx**,  
- wyszukiwanie trasy za pomocą algorytmu **A\***,  
- rozwiązywanie problemu komiwojażera przy pomocy heurystyki **Nearest Neighbor**,  
- mechanizm naliczania kar czasowych za wykonywanie skrętów w lewo.  

Projekt udostępnia prosty **frontend webowy (Django + Leaflet)**, który umożliwia wprowadzanie adresów i wizualizację wyznaczonej trasy.

## Architektura
Aplikacja składa się z dwóch głównych modułów:
- **Core** – odpowiedzialny za logikę obliczeniową (grafy, algorytmy, wyznaczanie tras).
- **Frontend** – interfejs webowy dla użytkownika, umożliwiający podanie adresów i wizualizację trasy.  

W ramach prac projektowych moją odpowiedzialnością była implementacja części **Core**.

## Wykorzystywane biblioteki
- **Core**: `pyrosm`, `networkx`, `osmnx`, `geopandas`, `numpy`  
- **Frontend**: `Django`, `Leaflet` (JS)  

## Wyniki
W ramach eksperymentów:
- zbadano wpływ kar za skręty w lewo na kształt wyznaczanej trasy,  
- zweryfikowano dopuszczalność heurystyki w algorytmie A\*,  
- porównano wyniki algorytmu **Nearest Neighbor** z algorytmem brutalnym,  
- oceniono jakość i czas działania aplikacji dla różnych zestawów punktów.  

Politechnika Warszawska, 2024  

---

## How to run the app

Follow the steps below to set up and run the application locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/jsliwa1/tuw-summer-2024-spdb.git
2. **Navigate to the quickest-path directory**
    ```bash
    cd ./quickest-path
3. **Install the necessary requirements**
    ```bash
    pip install -r requirements.txt
4. **Navigate to the application directory**
    ```bash
    cd ./qickest-path/application
5. **Apply database migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
6. **Start the development server**
    ```bash
    python manage.py runserver
7. **Wait until the application starts**
8. **Open the app in your browser**
9. **Go to http://127.0.0.1:8000**

## How to use the app
Enter your starting address (Note: all addresses must be located within the Warsaw agglomeration)

Add additional addresses to build the route.

Click the "Find route" button.

Wait a few moments – the application will compute and draw the optimal path on the map.

Notes:
- The app is optimized for the Warsaw region and may not work correctly for addresses outside the agglomeration.
- Make sure you have Python 3.10+ installed before running the project.

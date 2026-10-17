import sqlite3
from datetime import datetime

locations = {
    "A": "Центр",
    "B": "Університет",
    "C": "Лікарня",
    "D": "Парк",
    "E": "Вокзал",
    "F": "Торговий центр",
    "G": "Аеропорт"
}

graph = {
    "A": {
        "B": {"distance": 5, "time": 8, "traffic": 2, "difficulty": 1},
        "D": {"distance": 6, "time": 9, "traffic": 1, "difficulty": 2}
    },
    "B": {
        "A": {"distance": 5, "time": 8, "traffic": 2, "difficulty": 1},
        "C": {"distance": 3, "time": 5, "traffic": 2, "difficulty": 1},
        "E": {"distance": 4, "time": 6, "traffic": 3, "difficulty": 2}
    },
    "C": {
        "B": {"distance": 3, "time": 5, "traffic": 2, "difficulty": 1},
        "E": {"distance": 5, "time": 8, "traffic": 2, "difficulty": 1}
    },
    "D": {
        "A": {"distance": 6, "time": 9, "traffic": 1, "difficulty": 2},
        "F": {"distance": 5, "time": 7, "traffic": 1, "difficulty": 1}
    },
    "E": {
        "B": {"distance": 4, "time": 6, "traffic": 3, "difficulty": 2},
        "C": {"distance": 5, "time": 8, "traffic": 2, "difficulty": 1},
        "G": {"distance": 9, "time": 11, "traffic": 2, "difficulty": 1}
    },
    "F": {
        "D": {"distance": 5, "time": 7, "traffic": 1, "difficulty": 1},
        "G": {"distance": 7, "time": 11, "traffic": 1, "difficulty": 1}
    },
    "G": {
        "E": {"distance": 9, "time": 11, "traffic": 2, "difficulty": 1},
        "F": {"distance": 7, "time": 11, "traffic": 1, "difficulty": 1}
    }
}

def dijkstra(graph, start):
    distances = {}
    previous = {}
    visited = set()
    # Початкові значення для всіх вершин
    for vertex in graph:
        distances[vertex] = float("inf")
        previous[vertex] = None
    distances[start] = 0
    # Поки є необроблені вершини
    while len(visited) < len(graph):
        current = None
        # Шукаємо вершину з найменшим часом
        for vertex in graph:
            if vertex not in visited:
                if current is None or distances[vertex] < distances[current]:
                    current = vertex
        # Якщо до решти вершин неможливо дістатися
        if current is None or distances[current] == float("inf"):
            break
        # Перевіряємо сусідні вершини
        for neighbor, data in graph[current].items():
            new_time = distances[current] + data["time"]
            if new_time < distances[neighbor]:
                distances[neighbor] = new_time
                previous[neighbor] = current
        visited.add(current)
    return distances, previous

def restore_route(previous, start, finish):
    route = []
    current = finish
    # Рухаємось від кінцевої точки до початкової
    while current is not None:
        route.append(current)
        current = previous[current]
    # Змінюємо порядок вершин
    route.reverse()
    # Перевіряємо, чи знайдено маршрут
    if route[0] != start:
        return []
    return route

def calculate_distance(graph, route):
    total_distance = 0
    for i in range(len(route) - 1):
        start = route[i]
        finish = route[i + 1]
        total_distance += graph[start][finish]["distance"]
    return total_distance

def find_all_routes(graph, start, finish, path=None):
    # Створюємо список відвіданих вершин
    if path is None:
        path = []
    # Додаємо поточну вершину до маршруту
    path = path + [start]
    # Якщо досягли кінцевої точки
    if start == finish:
        return [path]
    all_routes = []
    # Перевіряємо сусідні вершини
    for neighbor in graph[start]:
        # Не відвідуємо одну вершину двічі
        if neighbor not in path:
            new_routes = find_all_routes(
                graph, neighbor, finish, path
            )
            all_routes.extend(new_routes)
    return all_routes

def create_database():
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_point TEXT NOT NULL,
            finish_point TEXT NOT NULL,
            route TEXT NOT NULL,
            distance REAL,
            time REAL,
            traffic REAL,
            actual_time REAL,
            actual_distance REAL,
            created_at TEXT
        )
    """)
    connection.commit()
    connection.close()

def save_route(start, finish, route, distance, travel_time, graph):
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    # Перетворення списку маршруту на рядок
    route_text = ",".join(route)
    # Обчислення середнього рівня заторів на маршруті
    total_traffic = 0
    for i in range(len(route) - 1):
        point1 = route[i]
        point2 = route[i + 1]
        total_traffic += graph[point1][point2]["traffic"]
    if len(route) > 1:
        average_traffic = total_traffic / (len(route) - 1)
    else:
        average_traffic = 0
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO routes (
            start_point,
            finish_point,
            route,
            distance,
            time,
            traffic,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        start,
        finish,
        route_text,
        distance,
        travel_time,
        average_traffic,
        created_at
    ))
    connection.commit()
    connection.close()

def show_route_history():
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    # Отримання історії поїздок
    cursor.execute("""
        SELECT id, route, distance, time,
               actual_time, actual_distance, created_at
        FROM routes
        ORDER BY id
    """)
    routes = cursor.fetchall()
    connection.close()
    print("\n      ІСТОРІЯ МАРШРУТІВ")
    if not routes:
        print("Історія маршрутів порожня.")
        return
    for route in routes:
        route_id, path, distance, travel_time, actual_time, actual_distance, date = route
        print(f"\nЗапис №{route_id}")
        print("Маршрут:", path.replace(",", " → "))
        print(f"Прогнозований час: {travel_time:g} хв")
        print(f"Прогнозована відстань: {distance:g} км")
        # Перевірка фактичного часу
        if actual_time is not None:
            difference = actual_time - travel_time
            print(f"Фактичний час: {actual_time:g} хв")
            print(f"Різниця: {difference:+g} хв")
        else:
            print("Фактичний час: ще не вказано")
        # Перевірка фактичної відстані
        if actual_distance is not None:
            print(f"Фактична відстань: {actual_distance:g} км")
        else:
            print("Фактична відстань: ще не вказано")
        print(f"Дата: {date}")
        print("-" * 35)

def add_actual_result():
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    print("\n      РЕЗУЛЬТАТ ПОЇЗДКИ")
    try:
        route_id = int(input("Введіть номер запису: "))
    except ValueError:
        print("Помилка! Номер запису має бути цілим числом.")
        connection.close()
        return
    # Пошук маршруту за його номером
    cursor.execute("""
        SELECT route, time, distance
        FROM routes
        WHERE id = ?
    """, (route_id,))
    route = cursor.fetchone()
    if route is None:
        print("Маршрут із таким номером не знайдено.")
        connection.close()
        return
    print("\nМаршрут:", route[0].replace(",", " → "))
    print("Прогнозований час:", route[1], "хв")
    print("Прогнозована відстань:", route[2], "км")
    try:
        actual_time = float(
            input("\nВведіть фактичний час (хв): ").replace(",", ".")
        )
        actual_distance = float(
            input("Введіть фактичну відстань (км): ").replace(",", ".")
        )
        if actual_time <= 0 or actual_distance < 0:
            print("Помилка! Введено некоректні значення.")
            connection.close()
            return
    except ValueError:
        print("Помилка! Необхідно ввести числові значення.")
        connection.close()
        return
    # Оновлення результатів поїздки в базі даних
    cursor.execute("""
        UPDATE routes
        SET actual_time = ?, actual_distance = ?
        WHERE id = ?
    """, (actual_time, actual_distance, route_id))
    connection.commit()
    connection.close()
    print("\nФактичний результат поїздки успішно збережено!")

def find_route():
    print("\n      ПОШУК МАРШРУТУ")
    print("\nДоступні локації:")
    for key, name in locations.items():
        print(f"{key} - {name}")
    start = input("\nВведіть початкову точку: ").strip().upper()
    finish = input("Введіть кінцеву точку: ").strip().upper()
    if start not in graph or finish not in graph:
        print("\nПомилка! Такої локації не існує.")
        return
    # Пошук найшвидшого маршруту
    distances, previous = dijkstra(graph, start)
    # Відновлення маршруту
    route = restore_route(previous, start, finish)
    if not route:
        print("\nМаршрут не знайдено.")
        return
    total_distance = calculate_distance(graph, route)
    print("\n      ЗНАЙДЕНИЙ МАРШРУТ")
    print("Маршрут:", " → ".join(route))
    print(f"Відстань: {total_distance:g} км")
    print(f"Час: {distances[finish]:g} хв")
    # Збереження результату в базі даних
    save_route(
        start,
        finish,
        route,
        total_distance,
        distances[finish],
        graph
    )
    print("\nМаршрут успішно збережено в базі даних!")

def show_statistics():
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            route,
            COUNT(*),
            COUNT(actual_time),
            AVG(time),
            AVG(actual_time),
            AVG(distance),
            AVG(actual_distance),
            AVG(actual_time - time)
        FROM routes
        GROUP BY route
        ORDER BY COUNT(*) DESC
    """)
    statistics = cursor.fetchall()
    connection.close()
    print("\n      СТАТИСТИКА МАРШРУТІВ")
    if not statistics:
        print("Дані для статистики відсутні.")
        return
    for row in statistics:
        (
            route,
            total_count,
            actual_count,
            average_time,
            average_actual_time,
            average_distance,
            average_actual_distance,
            time_difference
        ) = row
        print("\n" + "-" * 40)
        print("Маршрут:", route.replace(",", " → "))
        print(f"Кількість збережених маршрутів: {total_count}")
        print(f"Кількість завершених поїздок: {actual_count}")
        print(f"Середній прогнозований час: {average_time:.2f} хв")
        print(f"Середня прогнозована відстань: {average_distance:.2f} км")
        if actual_count > 0:
            print(f"Середній фактичний час: {average_actual_time:.2f} хв")
            print(f"Середня фактична відстань: {average_actual_distance:.2f} км")
            print(f"Середня різниця часу: {time_difference:+.2f} хв")
        else:
            print("Фактичні результати поїздок відсутні.")
    # Порівняння маршрутів за однаковими напрямками
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            start_point,
            finish_point,
            route,
            COUNT(actual_time),
            AVG(actual_time)
        FROM routes
        WHERE actual_time IS NOT NULL
        GROUP BY start_point, finish_point, route
        ORDER BY start_point, finish_point
    """)
    route_data = cursor.fetchall()
    connection.close()
    print("\n      ПОРІВНЯННЯ МАРШРУТІВ")
    # Групування маршрутів за початковою та кінцевою точками
    directions = {}
    for start, finish, route, count, avg_time in route_data:
        direction = (start, finish)
        if direction not in directions:
            directions[direction] = []
        directions[direction].append((route, count, avg_time))
    # Визначення найшвидшого та найповільнішого маршруту
    for direction, routes in directions.items():
        if len(routes) < 2:
            continue
        fastest = min(routes, key=lambda x: x[2])
        slowest = max(routes, key=lambda x: x[2])
        print(f"\nНапрямок: {direction[0]} → {direction[1]}")
        print("Найшвидший маршрут:", fastest[0].replace(",", " → "))
        print(f"Середній час: {fastest[2]:.2f} хв")
        print(f"Кількість поїздок: {fastest[1]}")
        print("Найповільніший маршрут:", slowest[0].replace(",", " → "))
        print(f"Середній час: {slowest[2]:.2f} хв")
        print(f"Кількість поїздок: {slowest[1]}")

def calculate_ai_time(predicted_time, actual_time, trip_count):
    # Якщо історії поїздок немає, залишаємо початковий прогноз
    if trip_count == 0 or actual_time is None:
        return predicted_time
    # Обчислення коефіцієнта довіри до історії
    alpha = trip_count / (trip_count + 5)
    # Коригування прогнозованого часу
    ai_time = (
        (1 - alpha) * predicted_time
        + alpha * actual_time
    )
    return ai_time

def get_route_statistics(route):
    # Перетворення списку вершин на рядок
    route_text = ",".join(route)
    connection = sqlite3.connect("navigator.db")
    cursor = connection.cursor()
    # Отримання кількості поїздок і середнього фактичного часу
    cursor.execute("""
        SELECT COUNT(actual_time), AVG(actual_time)
        FROM routes
        WHERE route = ?
    """, (route_text,))
    result = cursor.fetchone()
    connection.close()
    trip_count, average_actual_time = result
    return trip_count, average_actual_time

def analyze_routes(graph, start, finish):
    # Пошук усіх можливих маршрутів
    routes = find_all_routes(graph, start, finish)
    results = []
    # Аналіз кожного знайденого маршруту
    for route in routes:
        predicted_time = 0
        # Обчислення прогнозованого часу
        for i in range(len(route) - 1):
            point1 = route[i]
            point2 = route[i + 1]
            predicted_time += graph[point1][point2]["time"]
        # Отримання статистики з бази даних
        trip_count, average_time = get_route_statistics(route)
        # Коригування прогнозу на основі історії
        ai_time = calculate_ai_time(
            predicted_time,
            average_time,
            trip_count
        )
        # Збереження результатів аналізу
        results.append((
            route,
            predicted_time,
            ai_time,
            trip_count,
            average_time
        ))
    # Сортування за скоригованим прогнозом
    results.sort(key=lambda x: x[2])
    return results

def show_ai_recommendation():
    print("\n      AI-РЕКОМЕНДАЦІЯ")
    print("\nДоступні локації:")
    for key, name in locations.items():
        print(f"{key} - {name}")
    start = input("\nВведіть початкову точку: ").strip().upper()
    finish = input("Введіть кінцеву точку: ").strip().upper()
    if start not in graph or finish not in graph:
        print("Помилка! Такої локації не існує.")
        return
    if start == finish:
        print("Початкова та кінцева точки збігаються.")
        return
    # Пошук маршруту алгоритмом Дейкстри
    distances, previous = dijkstra(graph, start)
    dijkstra_route = restore_route(previous, start, finish)
    if not dijkstra_route:
        print("Маршрут не знайдено.")
        return
    # Аналіз усіх альтернативних маршрутів
    results = analyze_routes(graph, start, finish)
    if not results:
        print("Альтернативні маршрути відсутні.")
        return
    # Перший маршрут має найменший скоригований час
    best_route, predicted_time, ai_time, trip_count, average_time = results[0]
    print("\n      ПОРІВНЯННЯ")
    print("\nМаршрут Дейкстри:")
    print(" → ".join(dijkstra_route))
    print(f"Прогнозований час: {distances[finish]:.2f} хв")
    print("\nРекомендований маршрут:")
    print(" → ".join(best_route))
    print(f"Скоригований час: {ai_time:.2f} хв")
    print(f"Кількість завершених поїздок: {trip_count}")
    print("\nПричина:")
    if best_route == dijkstra_route:
        print("Маршрут Дейкстри залишається найвигіднішим")
        print("за скоригованим прогнозом часу.")
    else:
        print("За результатами аналізу історії")
        print("альтернативний маршрут має менший")
        print("скоригований прогнозований час.")
    if trip_count == 0:
        print("Для цього маршруту ще немає фактичної історії.")
    elif trip_count < 5:
        print("Кількість завершених поїздок поки невелика.")
    print("\n      УСІ МОЖЛИВІ МАРШРУТИ")
    # Сортування за початковим прогнозованим часом
    routes_by_time = sorted(results, key=lambda x: x[1])
    for number, (route, predicted, corrected, count, average) in enumerate(routes_by_time, 1):
        distance = calculate_distance(graph, route)
        print(f"\nМаршрут №{number}")
        print("Шлях:", " → ".join(route))
        print(f"Відстань: {distance:g} км")
        print(f"Прогнозований час: {predicted:.2f} хв")
        print(f"Скоригований час: {corrected:.2f} хв")
        print(f"Кількість завершених поїздок: {count}")
    try:
        number = int(input(
            "\nВведіть номер маршруту для збереження "
            "(0 — пропустити): "
        ))
        if number == 0:
            print("Збереження маршруту пропущено.")
        elif 1 <= number <= len(routes_by_time):
            selected_route, predicted, corrected, count, average = routes_by_time[number - 1]
            distance = calculate_distance(graph, selected_route)
            # Збереження вибраного маршруту
            save_route(
                start,
                finish,
                selected_route,
                distance,
                predicted,
                graph
            )
            print("\nМаршрут успішно збережено в базі даних!")
        else:
            print("Помилка! Невірний номер маршруту.")
    except ValueError:
        print("Помилка! Необхідно ввести ціле число.")

def main_menu():
    while True:
        print("\n      AI NAVIGATOR")
        print("1. Знайти маршрут")
        print("2. Додати результат поїздки")
        print("3. Історія маршрутів")
        print("4. Статистика")
        print("5. AI-рекомендація")
        print("0. Вихід")
        choice = input("\nОберіть дію: ").strip()
        if choice == "1":
            find_route()
        elif choice == "2":
            add_actual_result()
        elif choice == "3":
            show_route_history()
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            show_ai_recommendation()
        elif choice == "0":
            print("\nРоботу програми завершено.")
            break
        else:
            print("\nПомилка! Оберіть пункт від 0 до 5.")

# Запуск програми
if __name__ == "__main__":
    create_database()
    main_menu()
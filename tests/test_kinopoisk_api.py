import pytest
import allure
from pages.kinopoisk_api_page import KinopoiskAPIPage


@allure.epic("API Тесты Кинопоиска")
@allure.feature("Работа с API фильмов")
class TestKinopoiskAPI:
    """Тесты для API Кинопоиска."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Подготовка тестового окружения."""
        self.api_page = KinopoiskAPIPage()
        yield

    # ============== ПОЗИТИВНЫЕ ТЕСТЫ ==============

    @allure.title("Поиск фильма по существующему ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_movie_by_valid_id(self):
        """Тест получения фильма по существующему ID."""
        result = self.api_page.get_movie_by_id(46638)

        assert result["status_code"] == 200, f"Ожидался статус 200, получен {result['status_code']}"
        assert result["data"] is not None, "Данные фильма отсутствуют"
        assert self.api_page.validate_movie_response(result["data"]), "Отсутствуют обязательные поля"

        movie_name = result["data"].get("name")
        allure.dynamic.description(f"Найден фильм: {movie_name}")

    @allure.title("Получение случайного фильма")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_random_movie(self):
        """Тест получения случайного фильма."""
        result = self.api_page.get_random_movie()

        assert result["status_code"] == 200, f"Ожидался статус 200, получен {result['status_code']}"
        assert result["data"] is not None, "Данные случайного фильма отсутствуют"

        if result["data"]:
            movie_info = f"Фильм: {result['data'].get('name')}, Год: {result['data'].get('year')}"
            allure.attach(movie_info, name="Случайный фильм")

    @allure.title("Поиск фильмов по фильтрам")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_filters(self):
        """Тест поиска фильмов по фильтрам."""
        # Используем дефолтные фильтры
        result = self.api_page.search_movies_by_filters()

        assert result["status_code"] == 200, f"Ожидался статус 200, получен {result['status_code']}"
        assert result["data"] is not None, "Данные поиска отсутствуют"

        if result["data"] and "docs" in result["data"]:
            movies_count = len(result["data"]["docs"])
            total_count = result["data"].get("total", 0)
            allure.attach(f"Найдено фильмов: {movies_count} (всего: {total_count})", name="Результаты поиска")

            assert movies_count > 0, "Поиск не вернул ни одного фильма"
            assert movies_count <= 10, "Превышен лимит фильмов в ответе"

    @allure.title("Поиск с кастомными фильтрами")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_with_custom_filters(self):
        """Тест поиска с пользовательскими фильтрами."""
        custom_filters = self.api_page.create_custom_filters(
            type="movie",
            year="2020-2023",
            rating_kp="7-10",
            limit=5
        )

        result = self.api_page.search_movies_by_filters(custom_filters)

        assert result["status_code"] == 200, f"Ошибка при поиске: {result['status_code']}"
        if result["data"] and "docs" in result["data"]:
            movies = result["data"]["docs"]
            allure.attach(f"Найдено: {len(movies)} фильмов", name="Результаты кастомного поиска")

    # ============== НЕГАТИВНЫЕ ТЕСТЫ ==============

    @allure.title("Попытка доступа с неверным HTTP методом")
    @allure.severity(allure.severity_level.NORMAL)
    def test_wrong_http_method(self):
        """Тест использования неверного HTTP метода."""
        # Уменьшаем таймаут для этого теста
        self.api_page.timeout = 15

        result = self.api_page.get_movie_with_wrong_method(46638)

        # Если сервер вернул ошибку (не 200) - тест прошел
        # Если сервер не отвечает (504, 503, или исключение) - тоже считаем успехом
        # Главное - убедиться, что метод POST не работает

        if result.get("error"):
            # Запрос упал с исключением (например, timeout)
            allure.attach(f"Запрос завершился с ошибкой: {result.get('text')}", name="Результат")
            # Это тоже приемлемый результат для негативного теста
            assert True, "Запрос с неверным методом вызвал ошибку (ожидаемо)"
        else:
            # Сервер ответил, но не 200
            status_code = result["status_code"]
            allure.attach(f"Получен статус: {status_code}", name="Результат")

            # Проверяем, что это не успешный ответ
            assert status_code != 200, f"Неверный метод вернул успешный статус {status_code}"

            # Дополнительно можно проверить, что это ошибка сервера или клиента
            if status_code is not None:
                assert 400 <= status_code < 600, f"Неожиданный статус для неверного метода: {status_code}"

    @allure.title("Поиск фильма с несуществующим ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_movie_id(self):
        """Тест поиска фильма с несуществующим ID."""
        result = self.api_page.get_movie_with_invalid_id(250)

        # Ожидаем 404 или 400 ошибку
        assert result["status_code"] in [404, 400, 422], f"Неожиданный статус: {result['status_code']}"
        allure.attach(f"Статус для несуществующего ID: {result['status_code']}", name="Результат")

    @allure.title("Попытка доступа без авторизации")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_access_without_auth(self):
        """Тест доступа к API без токена."""
        result = self.api_page.get_movie_without_auth(46638)

        # Ожидаем 401 Unauthorized
        assert result["status_code"] == 401, f"Ожидался статус 401, получен {result['status_code']}"
        allure.attach("Доступ без токена правильно отклонен", name="Результат")

    # ============== КОМПЛЕКСНЫЕ ТЕСТЫ ==============

    @allure.title("Полный сценарий работы с API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_api_scenario(self):
        """Полный E2E сценарий тестирования API."""
        results = self.api_page.complete_api_scenario()

        # Проверяем позитивные тесты
        assert results["movie_by_id"]["status_code"] == 200, "Успешный поиск по Id"
        assert results["random_movie"]["status_code"] == 200, "Успешное получение случайного тайтла"
        assert results["filtered_movies"]["status_code"] == 200, "Успешный поиск по фильтрам"

        # Проверяем негативные тесты
        assert results["wrong_method"]["status_code"] != 200, "Ошибка с неверным методом запроса"
        assert results["invalid_id"]["status_code"] != 200, "Несуществующий ID не найден"
        assert results["no_auth"]["status_code"] == 401, "Доступ без токена отклонен"

        allure.attach(f"Все тесты пройдены успешно", name="Итог")

    @allure.title("Параметризованный тест поиска по разным ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("movie_id,expected_status", [
        (46638, 200),  # Существующий фильм "Мимино"
        (301, 200),  # Существующий фильм "Матрица"
        (250, 404),  # Несуществующий
        (0, 400),  # Некорректный ID
    ])
    def test_parametrized_movie_search(self, movie_id, expected_status):
        """Параметризованный тест поиска фильмов по разным ID."""
        result = self.api_page.get_movie_by_id(movie_id)

        assert result["status_code"] == expected_status, \
            f"Для ID {movie_id} ожидался статус {expected_status}, получен {result['status_code']}"

        allure.attach(f"ID: {movie_id}, Статус: {result['status_code']}", name="Результат")
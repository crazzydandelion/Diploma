import requests
import json
import allure
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class KinopoiskAPIPage:
    """Page Object для работы с API Кинопоиска."""

    # Конфигурация API
    BASE_URL = "https://api.poiskkino.dev/v1.4/movie"
    API_KEY = "Y8NYG7M-GT4MYE9-NKQ9794-YSDZWK4"

    # Дефолтные фильтры
    DEFAULT_FILTERS = {
        "selectFields": "name",
        "type": "cartoon",
        "limit": 10
    }

    def __init__(self):
        """Инициализация API клиента."""
        self.headers = {
            "X-API-KEY": self.API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.timeout = 30  # Таймаут в секундах

    def _safe_json_parse(self, response):
        """Безопасный парсинг JSON ответа."""
        try:
            if response.text and response.text.strip():
                return response.json()
            return None
        except json.JSONDecodeError:
            logger.warning(f"Не удалось распарсить JSON: {response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при парсинге ответа: {e}")
            return None

    def _make_request(self, method, url, **kwargs):
        """Универсальный метод для выполнения запросов с обработкой ошибок."""
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout

            response = requests.request(method, url, **kwargs)
            logger.info(f"{method} {url} - Status: {response.status_code}")

            # Прикрепляем информацию в Allure
            allure.attach(f"URL: {url}", name="Request URL")
            allure.attach(f"Method: {method}", name="HTTP Method")
            allure.attach(f"Status: {response.status_code}", name="Response Status")

            if response.text:
                # Ограничиваем размер лога
                log_text = response.text[:1000] if len(response.text) > 1000 else response.text
                allure.attach(log_text, name="Response Body")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"Таймаут запроса: {url}")
            allure.attach(f"Таймаут при запросе к {url}", name="Timeout Error")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {e}")
            allure.attach(f"Ошибка запроса: {e}", name="Request Error")
            raise

    # ============== ПОЗИТИВНЫЕ ТЕСТЫ ==============

    @allure.step("Поиск фильма по ID: {movie_id}")
    def get_movie_by_id(self, movie_id: int) -> Dict[str, Any]:
        """
        Получить информацию о фильме по ID.

        Args:
            movie_id: ID фильма

        Returns:
            Словарь с данными фильма
        """
        url = f"{self.BASE_URL}/{movie_id}"
        response = self._make_request("GET", url, headers=self.headers)

        return {
            "status_code": response.status_code,
            "data": self._safe_json_parse(response),
            "response": response,
            "text": response.text
        }

    @allure.step("Получение случайного фильма")
    def get_random_movie(self) -> Dict[str, Any]:
        """
        Получить случайный фильм.

        Returns:
            Словарь с данными случайного фильма
        """
        url = f"{self.BASE_URL}/random"
        response = self._make_request("GET", url, headers=self.headers)

        return {
            "status_code": response.status_code,
            "data": self._safe_json_parse(response),
            "response": response,
            "text": response.text
        }

    @allure.step("Поиск фильмов по фильтрам")
    def search_movies_by_filters(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Поиск фильмов по заданным фильтрам.

        Args:
            filters: Словарь с фильтрами. Если None, используются DEFAULT_FILTERS

        Returns:
            Словарь с результатами поиска
        """
        if filters is None:
            filters = self.DEFAULT_FILTERS

        allure.attach(f"Filters: {json.dumps(filters, indent=2, ensure_ascii=False)}", name="Filters")

        response = self._make_request("GET", self.BASE_URL, headers=self.headers, params=filters)

        return {
            "status_code": response.status_code,
            "data": self._safe_json_parse(response),
            "response": response,
            "text": response.text
        }

    # ============== НЕГАТИВНЫЕ ТЕСТЫ ==============

    @allure.step("Попытка получения фильма по ID с неверным методом")
    def get_movie_with_wrong_method(self, movie_id: int) -> Dict[str, Any]:
        """
        Попытка получить фильм с использованием неверного HTTP метода.

        Args:
            movie_id: ID фильма

        Returns:
            Словарь с результатом запроса
        """
        url = f"{self.BASE_URL}/{movie_id}"

        try:
            response = self._make_request("POST", url, headers=self.headers)
        except requests.exceptions.RequestException as e:
            # Если запрос упал с исключением (например, timeout)
            logger.error(f"Запрос с неверным методом завершился ошибкой: {e}")
            return {
                "status_code": None,
                "data": None,
                "response": None,
                "text": str(e),
                "error": True
            }

        return {
            "status_code": response.status_code,
            "data": self._safe_json_parse(response),
            "response": response,
            "text": response.text
        }

    @allure.step("Поиск фильма с несуществующим ID: {movie_id}")
    def get_movie_with_invalid_id(self, movie_id: int) -> Dict[str, Any]:
        """
        Попытка получить фильм с несуществующим ID.

        Args:
            movie_id: Несуществующий ID фильма

        Returns:
            Словарь с результатом запроса
        """
        return self.get_movie_by_id(movie_id)

    @allure.step("Попытка получения фильма без авторизации")
    def get_movie_without_auth(self, movie_id: int) -> Dict[str, Any]:
        """
        Попытка получить фильм без API ключа.

        Args:
            movie_id: ID фильма

        Returns:
            Словарь с результатом запроса
        """
        url = f"{self.BASE_URL}/{movie_id}"

        allure.attach("Headers: No API key", name="Request Headers")

        try:
            response = self._make_request("GET", url, timeout=10)  # Без headers!
        except requests.exceptions.RequestException as e:
            logger.error(f"Запрос без авторизации завершился ошибкой: {e}")
            return {
                "status_code": None,
                "data": None,
                "response": None,
                "text": str(e),
                "error": True
            }

        return {
            "status_code": response.status_code,
            "data": self._safe_json_parse(response),
            "response": response,
            "text": response.text
        }

    # ============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==============

    @allure.step("Создание кастомных фильтров")
    def create_custom_filters(self, **kwargs) -> Dict[str, Any]:
        """
        Создать кастомные фильтры для поиска.

        Args:
            **kwargs: Параметры фильтров

        Returns:
            Словарь с фильтрами
        """
        filters = self.DEFAULT_FILTERS.copy()
        filters.update(kwargs)
        return filters

    @allure.step("Проверка наличия обязательных полей в ответе")
    def validate_movie_response(self, response_data: Dict) -> bool:
        """
        Проверить, что в ответе есть обязательные поля.

        Args:
            response_data: Данные фильма

        Returns:
            True если все обязательные поля присутствуют
        """
        if not response_data:
            return False

        required_fields = ["id", "name", "year"]
        for field in required_fields:
            if field not in response_data:
                logger.warning(f"Отсутствует обязательное поле: {field}")
                return False
        return True

    @allure.step("Проверка, что ответ содержит валидный JSON")
    def is_valid_json_response(self, result: Dict) -> bool:
        """
        Проверить, что ответ содержит валидный JSON.

        Args:
            result: Результат запроса

        Returns:
            True если ответ содержит валидный JSON
        """
        return result.get("data") is not None

    @allure.step("Выполнение полного сценария работы с API")
    def complete_api_scenario(self) -> Dict[str, Any]:
        """
        Выполнить полный сценарий работы с API.

        Returns:
            Словарь с результатами всех операций
        """
        results = {}

        # 1. Поиск конкретного фильма
        results["movie_by_id"] = self.get_movie_by_id(46638)

        # 2. Получение случайного фильма
        results["random_movie"] = self.get_random_movie()

        # 3. Поиск по фильтрам
        results["filtered_movies"] = self.search_movies_by_filters()

        # 4. Негативные тесты
        # Для негативных тестов уменьшаем таймаут
        original_timeout = self.timeout
        self.timeout = 15

        try:
            results["wrong_method"] = self.get_movie_with_wrong_method(46638)
            results["invalid_id"] = self.get_movie_with_invalid_id(250)
            results["no_auth"] = self.get_movie_without_auth(46638)
        finally:
            self.timeout = original_timeout

        return results
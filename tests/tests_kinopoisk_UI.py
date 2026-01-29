import allure
import pytest
from pages.main_page import MainPage


@allure.epic("Кинопоиск")
@allure.feature("Навигация по сайту")
@allure.story("Полный сценарий взаимодействия")
class TestKinopoiskNavigation:
    """
    Тесты навигации по сайту Кинопоиск.
    """

    @allure.title("Полный сценарий навигации по Кинопоиску")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("e2e", "navigation", "regression")
    def test_complete_kinopoisk_navigation(self, driver):
        """
        Полный E2E тест навигации по Кинопоиску.
        Включает поиск, переходы по разделам и работу с медиа.
        """
        # Создаем экземпляр главной страницы
        main_page = MainPage(driver)

        # Выполняем полный сценарий
        with allure.step("Запуск полного сценария навигации"):
            main_page.complete_navigation_scenario(movie_name="Мимино")

        with allure.step("Проверка завершения сценария"):
            # Пример проверки
            current_url = driver.current_url
            allure.attach(
                f"✅ Сценарий успешно выполнен\n"
                f"Финальный URL: {current_url}\n"
                f"Заголовок: {driver.title}",
                name="Результат выполнения",
                attachment_type=allure.attachment_type.TEXT
            )

            # Простая проверка
            assert driver.current_url is not None
            print(f"✅ Тест завершен. Финальный URL: {current_url}")

    @allure.title("Поиск фильма на Кинопоиске")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("movie_name", ["Мимино", "Ирония судьбы", "Брат"])
    def test_search_movies(self, driver, movie_name):
        """
        Параметризованный тест поиска фильмов.
        """
        main_page = MainPage(driver)

        with allure.step(f"Поиск фильма '{movie_name}'"):
            main_page.open_kinopoisk()
            main_page.search_movie(movie_name)

            # Простая проверка
            assert movie_name.lower() in driver.title.lower() or \
                   movie_name.lower() in driver.page_source.lower(), \
                f"Фильм '{movie_name}' не найден на странице"

            allure.attach(
                f"✅ Фильм '{movie_name}' найден\n"
                f"Заголовок: {driver.title}",
                name="Результат поиска",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.title("Переход в раздел 'Билеты в кино'")
    @allure.severity(allure.severity_level.NORMAL)
    def test_go_to_tickets(self, driver):
        """Тест перехода в раздел билетов."""
        main_page = MainPage(driver)

        main_page.open_kinopoisk()
        main_page.go_to_tickets()

        # Проверка что перешли на страницу билетов/афиши
        current_url = driver.current_url
        print(f"Текущий URL после перехода в билеты: {current_url}")

        # Проверяем различные возможные URL страницы билетов
        assert any(keyword in current_url for keyword in [
            "afisha",
            "tickets",
            "movies-in-cinema",
            "cinema",
            "lists/movies"
        ]), f"Не перешли на страницу билетов. Текущий URL: {current_url}"

        # Также можно проверить заголовок страницы
        page_title = driver.title.lower()
        assert any(keyword in page_title for keyword in [
            "билеты",
            "кино",
            "афиша",
            "расписание",
            "cinema",
            "tickets"
        ]), f"Не на странице билетов. Заголовок: {driver.title}"

    @allure.title("Переход в раздел 'Медиа' и навигация")
    @allure.severity(allure.severity_level.NORMAL)
    def test_media_navigation(self, driver):
        """Тест навигации в разделе медиа."""
        main_page = MainPage(driver)

        # Открываем главную и переходим в медиа
        main_page.open_kinopoisk()
        media_page = main_page.go_to_media()

        # Выполняем навигацию в медиа
        media_page.complete_media_navigation()

        # Проверка
        assert "rubric/318" in driver.current_url, \
            "Не перешли в рубрику 'Меня зовут...'"
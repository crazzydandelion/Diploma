from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage
import allure
import time


class MainPage(BasePage):
    """
    Page Object для главной страницы Кинопоиска.
    """

    # Локаторы
    SEARCH_INPUT = (By.NAME, "kp_query")

    # Несколько вариантов для "Билеты в кино"
    TICKETS_LINKS = [
        (By.XPATH, "//a[text()='Билеты в кино']"),
        (By.XPATH, "//a[contains(text(), 'Билеты')]"),
        (By.CSS_SELECTOR, "a[href*='afisha']"),
        (By.CSS_SELECTOR, "a[data-tid*='tickets']"),
    ]

    VACANCIES_LINK = (By.LINK_TEXT, "Вакансии")
    SUPPORT_BUTTON = (By.XPATH, "//button[@type='button' and normalize-space(text())='Служба поддержки']")
    MEDIA_LINK = (By.XPATH, "//a[@data-tid='de7c6530' and @href='/media/']")

    @allure.step("Открыть главную страницу Кинопоиска")
    def open_kinopoisk(self):
        self.open("https://www.kinopoisk.ru/")
        self.wait_for_page_load()
        return self

    @allure.step("Выполнить поиск фильма: {movie_name}")
    def search_movie(self, movie_name):
        element = self.find_element(self.SEARCH_INPUT)
        element.clear()
        element.send_keys(movie_name)
        element.send_keys(Keys.RETURN)
        time.sleep(2)
        return self

    @allure.step("Перейти в раздел 'Билеты в кино'")
    def go_to_tickets(self):
        for i, locator in enumerate(self.TICKETS_LINKS, 1):
            try:
                element = self.find_element(locator, timeout=3)
                if element.is_displayed():
                    print(f"✅ Нашли 'Билеты' локатором {i}")
                    element.click()
                    time.sleep(2)
                    return self
            except:
                continue

        # Если не нашли стандартными методами
        self.take_screenshot("tickets_not_found")
        raise Exception("Не удалось найти ссылку 'Билеты в кино'")

    @allure.step("Перейти в раздел 'Вакансии'")
    def go_to_vacancies(self):
        self.scroll_to_bottom()
        time.sleep(1)

        try:
            self.click(self.VACANCIES_LINK)
        except:
            # Альтернативный поиск
            elements = self.find_elements(By.TAG_NAME, "a")
            for element in elements:
                if "Вакансии" in element.text:
                    element.click()
                    break

        time.sleep(2)
        return self

    @allure.step("Перейти в 'Службу поддержки'")
    def go_to_support(self):
        self.scroll_to_bottom()
        time.sleep(1)

        try:
            self.click(self.SUPPORT_BUTTON)
        except:
            # Ищем любую кнопку с текстом "поддержки"
            buttons = self.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "поддержки" in button.text.lower():
                    button.click()
                    break

        time.sleep(2)
        return self

    @allure.step("Перейти в раздел 'Медиа'")
    def go_to_media(self):
        try:
            self.click(self.MEDIA_LINK)
            print("Успешно кликнули по MEDIA_LINK")
        except Exception as e:
            print(f"Ошибка при клике по MEDIA_LINK: {e}")
            print("Пытаемся найти альтернативную ссылку...")
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/media/']")
            print(f"Найдено {len(elements)} элементов с медиа-ссылками")
            if elements:
                elements[0].click()
                print("Кликнули по альтернативной ссылке")
            else:
                raise Exception("Ссылка на 'Медиа' не найдена")

        # Импорт MediaPage здесь, чтобы избежать циклического импорта
        from pages.media_page import MediaPage
        return MediaPage(self.driver)

    @allure.step("Выполнить полный сценарий навигации")
    def complete_navigation_scenario(self, movie_name="Мимино"):
        try:
            with allure.step("1. Открыть Кинопоиск"):
                self.open_kinopoisk()

            with allure.step("2. Выполнить поиск фильма"):
                self.search_movie(movie_name)
                self.take_screenshot("after_search")

            with allure.step("3. Перейти в 'Билеты в кино'"):
                self.go_to_tickets()

            with allure.step("4. Перейти в 'Вакансии'"):
                self.go_to_vacancies()

            with allure.step("5. Перейти в 'Службу поддержки'"):
                self.go_to_support()

            with allure.step("6. Перейти в 'Медиа'"):
                self.go_to_media()

            return self

        except Exception as e:
            self.take_screenshot("error")
            raise
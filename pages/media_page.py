from selenium.webdriver.common.by import By
from .base_page import BasePage
import allure
import time

class MediaPage(BasePage):
    """
    Page Object для страницы медиа Кинопоиска.
    """

    # Локаторы
    RUBRICS_BUTTON = (By.CLASS_NAME, "media-rubrics-navigation__button")
    MY_NAME_IS_LINK = (By.XPATH, "//a[@class='media-rubrics-navigation__item-link' and @href='/media/rubric/318/']")

    @allure.step("Открыть рубрики медиа")
    def open_rubrics(self):
        self.click(self.RUBRICS_BUTTON)
        time.sleep(2)

    @allure.step("Перейти в рубрику 'Меня зовут...'")
    def go_to_my_name_is(self):
        self.click(self.MY_NAME_IS_LINK)
        time.sleep(2)
        return self

    @allure.step("Полный сценарий навигации по медиа")
    def complete_media_navigation(self):
        """
        Полный сценарий навигации по разделу медиа.
        """
        with allure.step("1. Открыть рубрики медиа"):
            self.open_rubrics()

        with allure.step("2. Перейти в рубрику 'Меня зовут...'"):
            self.go_to_my_name_is()

        return self
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import allure
import time


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ========== ОСНОВНЫЕ МЕТОДЫ ==========

    @allure.step("Открыть URL: {url}")
    def open(self, url):
        self.driver.get(url)
        time.sleep(2)
        return self

    @allure.step("Найти элемент: {locator}")
    def find_element(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"Ошибка поиска {locator}",
                attachment_type=allure.attachment_type.PNG
            )
            raise

    @allure.step("Найти все элементы: {locator}")
    def find_elements(self, locator):
        return self.driver.find_elements(*locator)

    @allure.step("Кликнуть элемент: {locator}")
    def click(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            element.click()
            time.sleep(1)
            return self
        except Exception as e:
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"Ошибка клика {locator}",
                attachment_type=allure.attachment_type.PNG
            )
            raise

    @allure.step("Ввести текст '{text}' в элемент: {locator}")
    def send_keys(self, locator, text):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        return self

    @allure.step("Нажать Enter в элементе: {locator}")
    def send_enter(self, locator):
        element = self.find_element(locator)
        element.send_keys(Keys.RETURN)
        time.sleep(1)
        return self

    # ========== МЕТОДЫ ПРОКРУТКИ ==========

    @allure.step("Прокрутить страницу до конца")
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        return self

    @allure.step("Прокрутить страницу до верха")
    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        return self

    @allure.step("Прокрутить на {pixels} пикселей")
    def scroll_by(self, pixels):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(0.5)
        return self

    # ========== МЕТОДЫ ОЖИДАНИЯ ==========

    @allure.step("Ждать загрузки страницы")
    def wait_for_page_load(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)
        return self

    @allure.step("Ожидание {seconds} секунд")
    def wait(self, seconds):
        time.sleep(seconds)
        return self

    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========

    @allure.step("Получить текущий URL")
    def get_current_url(self):
        return self.driver.current_url

    @allure.step("Получить заголовок страницы")
    def get_title(self):
        return self.driver.title

    @allure.step("Сделать скриншот")
    def take_screenshot(self, name="screenshot"):
        screenshot = self.driver.get_screenshot_as_png()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        return self

    @allure.step("Переключиться на последнюю вкладку")
    def switch_to_new_tab(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return self

    @allure.step("Закрыть текущую вкладку")
    def close_current_tab(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return self
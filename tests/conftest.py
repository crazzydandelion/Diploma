import pytest
from selenium import webdriver

@pytest.fixture
def driver():
    """Простая фикстура драйвера."""
    driver = webdriver.Edge()
    driver.maximize_window()
    yield driver
    driver.quit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
driver = webdriver.Edge()
driver.maximize_window()
driver.get("https://www.kinopoisk.ru/")

search = driver.find_element(By.NAME, "kp_query")
search.send_keys("Мимино")
search.send_keys(Keys.RETURN)

tickets_link = driver.find_element(
    By.XPATH,
    "//a[text()='Билеты в кино']"
).click()

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
vacancies = driver.find_element(By.LINK_TEXT, "Вакансии").click()

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
support_button = driver.find_element(
    By.XPATH,
    "//button[@type='button' and normalize-space(text())='Служба поддержки']"
).click()

media = driver.find_element(By.XPATH,"//a[@data-tid='de7c6530' and @href='/media/']").click()
sleep(2)
rubrics = driver.find_element(By.CLASS_NAME, "media-rubrics-navigation__button").click()
sleep(2)
my_name_is = driver.find_element(By.XPATH,"//a[@class='media-rubrics-navigation__item-link' and @href='/media/rubric/318/']").click()

sleep (5)
driver.quit()
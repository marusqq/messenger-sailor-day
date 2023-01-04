import random
import time
from typing import List

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common_selenium_methods import log_in_to_messenger


def random_sleep(min_secs=3, max_secs=8):
    sleep_for = random.randint(min_secs, max_secs)
    print(f'Sleep randomly for {min_secs}-{max_secs} seconds (this time: {sleep_for})')
    time.sleep(sleep_for)


def wait_until_found_and_return_elements(
        driver: webdriver,
        look_by: By,
        look_for: str,
        time_to_wait: int = 20
) -> List[WebElement]:
    try:
        elements = WebDriverWait(driver, time_to_wait).until(
            expected_conditions.presence_of_all_elements_located((look_by, look_for))
        )
        return elements

    except TimeoutException:
        return []


# launch firefox and messenger on TAB 0
driver = log_in_to_messenger(headless=True, maximise=False, disable_gpu=True)
driver.get("https://www.messenger.com/t/4792185507482409")

# LAUNCH HLTV
driver.execute_script("window.open('');")
# Switch to the new window and open new URL
driver.switch_to.window(driver.window_handles[1])
driver.get("https://www.hltv.org/news/archive/2023/january")

cookies_btn = wait_until_found_and_return_elements(
    driver,
    look_by=By.ID,
    look_for="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
    time_to_wait=20
)
if len(cookies_btn):
    cookies_btn[0].click()

# confirmed cookies and ready to check
# url: text
top20_found = {}

while len(top20_found.keys()) < 21:

    top20_found_in_this_run = {}
    new_top20_found = {}

    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://www.hltv.org/news/archive/2023/january")

    # get all news articles: HLTV
    news_articles = driver.find_elements(by=By.XPATH, value="//a[@class='newsline article']")
    news_articles.reverse()

    for news_article in news_articles:
        news_article_text = news_article.find_element(by=By.XPATH, value=".//div[@class='newstext']").text
        if "Top 20 players of 2022:" in news_article_text:
            top20_found_in_this_run[news_article.get_attribute('href')] = news_article_text

    # check for new top20 posts
    for top20_url, top20_news_article_text in top20_found_in_this_run.items():
        if top20_url not in top20_found.keys():
            top20_found[top20_url] = top20_news_article_text
            new_top20_found[top20_url] = top20_news_article_text

    driver.switch_to.window(driver.window_handles[0])
    driver.get("https://www.messenger.com/t/4792185507482409")
    # send to fb newly found top20
    message_box = wait_until_found_and_return_elements(
        driver, look_by=By.XPATH, look_for="//div[@aria-label='Message']")
    message_box[0].click()

    for new_link, new_article_text in new_top20_found.items():
        message = f"New HLTV top 20 post: {new_article_text}: {new_link}"
        ActionChains(driver).send_keys_to_element(message_box[0], message).perform()
        send_buttons = wait_until_found_and_return_elements(
            driver, look_by=By.XPATH, look_for="//div[@aria-label='Press enter to send']")
        send_buttons[0].click()

        time.sleep(2)

    # random wait after writing
    random_sleep(300, 600)

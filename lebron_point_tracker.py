import json
import time

from typing import List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common_selenium_methods import log_in_to_messenger

from datetime import datetime

GROUP_IDS = ["4792185507482409", "1969824719777612", "100000139826158"]
TEST_GROUP_IDS = ["100000105556453"]


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


def parse_nba_page(driver):
    parsed_data = {}

    time.sleep(5)

    # wait for a page to load by waiting for one of the lists to load
    _ = wait_until_found_and_return_elements(
        driver,
        look_by=By.XPATH,
        look_for="//ul[@data-stringify-type='unordered-list']",
        time_to_wait=30
    )

    # left points
    pts_left_element = driver.find_element(by=By.XPATH, value="//p/span[@style='color: #ff0000;']/strong")
    pts_left = pts_left_element.text.split(' career')[0]
    parsed_data['lebron_pts_left'] = pts_left

    # kareem career pts
    kareem_points_element = driver.find_element(by=By.XPATH, value="//table/tbody/tr[2]/td[3]/span")
    parsed_data['kareem_career_pts'] = kareem_points_element.text.replace(',', ' ')

    # lebron career pts
    lebron_points_element = driver.find_element(by=By.XPATH, value="//table/tbody/tr[3]/td[3]/span")
    parsed_data['lebron_career_pts'] = lebron_points_element.text.replace(',', ' ')

    # lebron ppg and prediction
    prediction_element = driver.find_element(by=By.XPATH, value="//div[@class='p-rich_text_section']/p[2]")

    lebron_ppg = prediction_element.text.split('of ')[1].split(' points')[0]
    parsed_data['lebron_ppg'] = lebron_ppg

    lebron_games_left_prediction = prediction_element.text.split('need ')[1].split(' more')[0]
    parsed_data['lebron_games_left_prediction'] = lebron_games_left_prediction

    # predicted games to reach record
    predicted_games = []
    predicted_games_list_element = driver.find_element(by=By.XPATH, value="//ul[@data-stringify-type='unordered-list']")
    list_elements = predicted_games_list_element.find_elements(by=By.XPATH, value="./li")
    for list_element in list_elements:
        predicted_game = {}

        date, enemy_team = list_element.text.split(': ')

        predicted_game[date] = enemy_team.split(' (')[0]
        predicted_games.append(predicted_game)

    parsed_data['predicted_games'] = predicted_games

    # last games
    last_games = []
    list_hyperlink_elements = driver.find_elements(by=By.XPATH, value=".//a[contains(text(),'Lakers')]")
    for list_hyperlink_element in list_hyperlink_elements:
        last_game = {}

        list_element = list_hyperlink_element.find_element(by=By.XPATH, value="./..")
        date, other_data = list_element.text.split(': ')
        game_score, lebron_pts_scored = other_data.split(' | ')

        last_game[date] = {
            'game_score': game_score,
            'lebron_pts_scored': lebron_pts_scored.split(' points')[0]
        }
        last_games.append(last_game)

    parsed_data['last_games'] = last_games

    # upcoming 5 games
    upcoming_games_list_element = driver.find_element(
        by=By.XPATH,
        value="//strong[contains(text(),'LeBron’s next 5 games')]/../../following-sibling::ul")
    # for upcoming_games_list_element in upcoming_games_list_elements:
    upcoming_games = []
    list_elements = upcoming_games_list_element.find_elements(by=By.XPATH, value="./li")
    for list_element in list_elements:
        upcoming_game = {}

        date, enemy_team = list_element.text.split(': ')

        upcoming_game[date] = enemy_team.split(' (')[0]
        upcoming_games.append(upcoming_game)

    parsed_data['upcoming_games'] = upcoming_games

    return parsed_data


def collect_message(information):
    message_list = []

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    msg_headline = f"{dt_string} update:"

    msg_prediction = f"With PPG of {information['lebron_ppg']} Lebron would need " \
                     f"{information['lebron_games_left_prediction']} games to reach Kareem"

    # ----- next games -----
    next_games = []
    for next_game in information['upcoming_games']:
        for date, enemy_team in next_game.items():
            game_str = f"{date} - {enemy_team}"
            next_games.append(game_str)

    next_games_str = ", ".join(next_games)
    msg_next_games = f"Next games for LBJ: {next_games_str}"

    # ----- predicted games -----
    predicted_games = []
    for predicted_game in information['predicted_games']:
        for date, enemy_team in predicted_game.items():
            game_str = f"{date} - {enemy_team}"
            predicted_games.append(game_str)

    predicted_games_str = ", ".join(predicted_games)
    msg_predicted_games = f"Predicted games for LBJ to reach record: {predicted_games_str}"

    # ----- last games -----
    last_games = []
    game_str = ""
    for last_game in information['last_games']:
        for date, last_game_data in last_game.items():
            game_str = f"{date} - {last_game_data['game_score']} (LBJ: {last_game_data['lebron_pts_scored']} pts)"
            last_games.append(game_str)

    last_games_str = ", ".join(last_games)
    msg_last_games = f"Last games for LBJ: {last_games_str}"

    last_game = information['last_games'][0]
    last_game_date = list(last_game.keys())[0]
    lebron_scored_last_game = information['last_games'][0][last_game_date]['lebron_pts_scored']

    msg_lebron_pts_left = f"{information['lebron_pts_left']} points left for LeBron James " \
                          f"({information['lebron_career_pts']}) " \
                          f"to reach Kareem Abdul-Jabbar ({information['kareem_career_pts']}). " \
                          f"Last game LeBron scored: {lebron_scored_last_game}"

    # message_list.append(msg_headline)
    message_list.append(msg_lebron_pts_left)
    message_list.append(msg_prediction)
    # message_list.append(msg_last_games)
    # message_list.append(msg_next_games)
    # message_list.append(msg_predicted_games)

    return message_list


# login to messenger
driver = log_in_to_messenger(headless=True, maximise=False, disable_gpu=True)

# for tests:
# ---------------
# headless = True
# disable_gpu = False
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
#
# options = FirefoxOptions()
# if headless:
#     options.add_argument("--headless")
# if disable_gpu:
#     options.add_argument("--disable-gpu")
# driver = webdriver.Firefox(options=options)

# go to nba counter

driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[1])
driver.get("https://www.nba.com/news/lebron-james-scoring-tracker")

# accept cookies
cookies_btn = wait_until_found_and_return_elements(
    driver,
    look_by=By.ID,
    look_for="onetrust-accept-btn-handler",
    time_to_wait=20
)
if len(cookies_btn):
    cookies_btn[0].click()

information_dict = parse_nba_page(driver)

from pprint import pprint

pprint(information_dict)

driver.switch_to.window(driver.window_handles[0])

# collect message
message_lines = collect_message(information_dict)

# check if lebron pts difference changed, if changed, send the messages!!!!!
lebron_diff_changed = False

with open("lebron_pts_diff.json", "r") as lebron_diff_json:
    lebron_diff_dict = json.load(lebron_diff_json)

if lebron_diff_dict['lebron_pts_left'] != information_dict['lebron_pts_left']:
    lebron_diff_changed = True

if lebron_diff_changed:

    print('LEBRON HAS SCORED MORE POINTS LESSSGOOOOOO')

    # save the diff
    lebron_diff_dict = {'lebron_pts_left': information_dict['lebron_pts_left']}
    with open("lebron_pts_diff.json", "w") as lebron_diff_json:
        json.dump(lebron_diff_dict, lebron_diff_json)

    # send messages
    for group_id in GROUP_IDS:

        # load messenger window
        driver.get(f"https://www.messenger.com/t/{group_id}")

        # press on write message
        message_box = wait_until_found_and_return_elements(driver, look_by=By.XPATH,
                                                           look_for="//div[@aria-label='Message']")
        message_box[0].click()

        # write message lines
        for message in message_lines:
            ActionChains(driver).send_keys_to_element(message_box[0], message).perform()

            send_buttons = wait_until_found_and_return_elements(
                driver, look_by=By.XPATH, look_for="//div[@aria-label='Press enter to send']")
            send_buttons[0].click()

            time.sleep(1)

        time.sleep(3)

driver.quit()

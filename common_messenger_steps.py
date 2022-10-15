import util
from common_selenium_methods import (
    wait_for_element_to_load,
    find_and_get_element,
    find_and_get_elements,
    press_element,
    clear_element,
    enter_input
)
from logger import logger


def get_group_names_from_ids(driver, group_ids):
    group_ids_with_names = {}

    logger.info("[Scraping group name for every group ID]: Started")

    for group_id, group_name in group_ids.items():
        driver.get(f"https://www.messenger.com/t/{group_id}")
        # if the group didn't load in 20 secs, go to next group id
        if not wait_for_element_to_load(driver, element_to_find="//a[starts-with(@aria-label, 'Chats')]"):
            logger.info(f"[Scraping group name for every group ID]: "
                        f"Group ID failed to load in 20 seconds. Maybe bad group ID? {group_id}")
            continue

        # try to find a single person (PM) name
        href_xpath = f"https://www.facebook.com/{group_id}/"
        group_name_element = find_and_get_element(driver, element_to_find=f"//a[@href='{href_xpath}']")
        if group_name_element:
            if group_name_element.get_attribute('aria-label'):
                group_name_found = group_name_element.get_attribute('aria-label')
                logger.info(f"[Scraping group name for every group ID]: "
                            f"Found name for groupID({group_id}): {group_name_found}")
                group_ids_with_names[group_id] = group_name_found

        # if not found - try looking for a group name
        if group_name_element is None:
            group_name_element = find_and_get_element(
                driver, element_to_find="//div[starts-with(@aria-label, 'Conversation titled')]")
            if group_name_element:
                if group_name_element.get_attribute('aria-label'):
                    if "Conversation titled " in group_name_element.get_attribute('aria-label'):
                        group_name_found = \
                            group_name_element.get_attribute('aria-label').split("Conversation titled ")[1]
                        logger.info(f"[Scraping group name for every group ID]: "
                                    f"Found name for groupID({group_id}): {group_name_found}")
                        group_ids_with_names[group_id] = group_name_found

    logger.info(f"[Scraping group name for every group ID]: Names: {group_ids_with_names}")
    logger.info("[Scraping group name for every group ID]: Done")
    return group_ids_with_names


def find_correct_video_and_start_forwarding(driver, video_group_id):
    # 1. Get today's weekday number
    weekday = util.get_weekday()
    weekday_str = util.get_day_name_from_weekday_int(weekday)
    logger.info(f"[Find video and Forward]: Today is: {weekday_str}")

    # 2. Load up group that has all the videos
    driver.get(f"https://www.messenger.com/t/{video_group_id}")
    logger.info("[Find video and Forward]: Opened group with videos")

    # if the group didn't load in 20 secs, go to next group id
    if not wait_for_element_to_load(driver, element_to_find="//a[starts-with(@aria-label, 'Chats')]"):
        raise SystemExit(f"[Find video and Forward]: "
                         f"Group that has videos failed to load. Group_id: {video_group_id}")

    # find all the possible forwards
    logger.info("[Find video and Forward]: Search for MrCrabs videos: Started")
    video_forward_elements = find_and_get_elements(
        driver, element_to_find="//div[@aria-label='Forward']")

    logger.info(f"[Find video and Forward]: Search for MrCrabs videos: "
                f"{len(video_forward_elements)} found")

    # forward elements are found in this order:
    # 0    1    2    3    4    5    6
    # sun  sat  fri  thu  wed  tue  mon
    video_forward_elements[7 - weekday].click()
    logger.info("[Find video and Forward]: Searching for MrCrabs videos: Clicking forward on the correct video")


def forward_to_group_names(driver, group_ids_with_names):
    logger.info("[Forwarding to groups]: Start")

    for _, group_name in group_ids_with_names.items():
        press_element(driver, element_to_find="//input[@aria-label='Search for people and groups']", time_to_wait=30)
        logger.info("[Forwarding to groups]: Pressed on search tab")

        clear_element(driver, element_to_find="//input[@aria-label='Search for people and groups']")
        logger.info("[Forwarding to groups]: Cleaned search tab")

        enter_input(driver, input_element="//input[@aria-label='Search for people and groups']", input_text=group_name)
        logger.info(f"[Forwarding to groups]: Entering {group_name}")

        press_element(driver, element_to_find="//div[@aria-label='Send']")
        logger.info("[Forwarding to groups]: Pressing first send")

        wait_for_element_to_load(driver, element_to_find="//div[@aria-label='Sent']", time_to_wait=40)
        logger.info("[Forwarding to groups]: Sent loaded")

    logger.info("[Forwarding to groups]: Done")

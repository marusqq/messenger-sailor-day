import util
import argparse
from common_selenium_methods import log_in_to_messenger
from common_messenger_steps import (
    get_group_names_from_ids,
    find_correct_video_and_start_forwarding,
    forward_to_group_names
)
from logger import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument(
        'env', metavar='env', choices=['prod', 'test'], type=str, default='prod',
        help="if env test is specified, testing environment is chosen")

    args = parser.parse_args()
    logger.info("[SETUP]: Command line arguments: Read")
    logger.info(f"[SETUP]: Using {args.env.upper()} environment")

    driver = log_in_to_messenger(headless=True, maximise=True)

    # -------------------------------------------------------------------
    # 0. Setup IDs
    video_group_id, group_ids = util.read_group_ids(args.env)

    # 1. Get actual names for IDs
    group_ids_with_names = get_group_names_from_ids(driver, group_ids)

    # 2. Find correct video on video_group_id
    find_correct_video_and_start_forwarding(driver, video_group_id)

    # 3. Forward to everyone that is in group_ids_with_names
    forward_to_group_names(driver, group_ids_with_names)

    driver.quit()

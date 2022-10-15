import json
import os
import platform
from datetime import datetime
import time
import pyotp
from cryptography.fernet import Fernet
import getpass
import calendar

from typing import Tuple

from logger import logger

if platform.system() == 'Windows':
    import py_setenv


def wait_seconds(seconds: int):
    time.sleep(seconds)


def make_screenshot(driver, name=None):
    if name is None:
        now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        name = f"screenshot_{now}"
    driver.save_screenshot(f'{os.getcwd()}/screenshots/{name}.png')


def get_weekday() -> int:
    """
    Returns weekday as int
    :return: weekday, 1 -> monday, 7 -> sunday
    """
    dt = datetime.now()
    return dt.isoweekday()


def get_day_name_from_weekday_int(weekday: int) -> str:
    day_strings = list(calendar.day_name)
    return day_strings[weekday-1]


def get_user_credential(credential_name, sensitive=True):
    if sensitive:
        return getpass.getpass(prompt=f"{credential_name}: ")
    else:
        return input(f"{credential_name}: ")


def set_environment_value(env_path: str, env_value: str):
    if platform.system() == 'Linux':
        bash_path = "~/.bashrc"
        with open(os.path.expanduser(bash_path), "a") as outfile:
            outfile.write(f"export {env_path}={env_value}")
    elif platform.system() == 'Windows':
        py_setenv.setenv(name=env_path, value=env_value)
    else:
        print("Setting environment value is not supported in mac. "
              f"Please set it yourself. {env_path}={env_value}")


def get_environment_value(env_path: str):
    encode = False
    # it's easier to store fernet_key as string,
    # but use it is used with bytes
    if env_path == "fernet_key":
        encode = True

    try:
        env_variable = os.environ[env_path]
        if encode:
            env_variable = env_variable.encode()
        return env_variable

    except KeyError:
        raise SystemExit(f"No such env variable found ({env_path}). "
                         f"If fernet_key was not found, run setup_credentials.py "
                         f"if you didn't yet")


def generate_fernet_key() -> bytes:
    return Fernet.generate_key()


def read_group_ids(env: str) -> Tuple[int, dict]:
    logger.info("[Setup group IDs]: Started")

    with open("group_ids.json") as json_file:
        json_data = json.load(json_file)

    # some checks
    if 'video_group_id' not in json_data:
        raise SystemExit('[Setup group IDs]: video_group_id not found in group_ids.json')

    if env == 'prod':
        expected_group_ids = 'send_group_ids'
    else:
        expected_group_ids = 'test_group_ids'

    if expected_group_ids not in json_data:
        raise SystemExit(f'[Setup group IDs]: {expected_group_ids} not found in group_ids.json')

    video_group_id = json_data['video_group_id']
    group_ids = json_data[expected_group_ids]

    logger.info(f"[Setup group IDs]: Video group ID: {video_group_id}")
    logger.info(f"[Setup group IDs]: Group IDs used: {group_ids}")

    logger.info("[Setup group IDs]: Done")

    return video_group_id, group_ids


def read_credentials() -> dict:
    with open("credentials.json") as json_file:
        json_data = json.load(json_file)

    return json_data


def write_credentials(credentials: dict):
    with open("credentials.json", 'w') as fp:
        json.dump(credentials, fp, indent=2)


def decode_credentials(credentials: dict, fernet_key: bytes) -> dict:
    decoded_credentials = {}
    for credential_name, credential in credentials.items():
        decoded_credentials[credential_name] = fernet_decrypt(credential, fernet_key)

    return decoded_credentials


def get_fernet_key() -> bytes:
    try:
        fernet_key = get_environment_value('fernet_key')
    except KeyError:
        raise SystemExit("'fernet_key' environmental variable is not set.\n"
                         "Run setup_credentials.py to setup environment")

    return fernet_key


def fernet_encrypt(message_to_encrypt: bytes, key: bytes) -> str:
    return Fernet(key).encrypt(message_to_encrypt).decode()


def fernet_decrypt(message_to_decrypt: bytes, key: bytes) -> str:
    return Fernet(key).decrypt(message_to_decrypt).decode()


def get_current_2fa_code(base32_code: str) -> str:
    totp = pyotp.TOTP(base32_code)
    return totp.now()

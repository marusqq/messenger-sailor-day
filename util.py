import json
import os
import platform
from datetime import datetime

if platform.system() == 'Windows':
    import py_setenv

import pyotp
from cryptography.fernet import Fernet
import getpass


def make_screenshot(driver):
    now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    driver.save_screenshot(f'screenshots/screenshot_{now}.png')


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

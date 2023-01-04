import time
from typing import Optional, List
import util
from logger import logger

from selenium_statics import XPathElements, SeleniumPage

from selenium.common import TimeoutException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebElement


def enter_credentials_and_login(driver, credentials_dict, page, check_keep_signed_in=False):
    _method = "Enter credentials and login"
    #       2.1. Enter login
    login_entered = enter_input(
        driver, element_xpath=XPathElements.MESSENGER_LOGIN_INPUT, input_text=credentials_dict['login'])
    util.log(method=_method, msg="Entered email", page=page, status=login_entered)

    #       2.2. Enter pass
    pass_entered = enter_input(
        driver, element_xpath=XPathElements.MESSENGER_PASS_INPUT, input_text=credentials_dict['password'])
    util.log(method=_method, msg="Entered password", page=page, status=pass_entered)

    if check_keep_signed_in:
        #       2.2.5. Keep me signed in
        keep_me_signed_in_pressed = press_element(
            driver, element_xpath=XPathElements.MESSENGER_KEEP_SIGNED_IN_CHECKBOX)
        util.log(method=_method, msg="Keep me signed in pressed", page=page, status=keep_me_signed_in_pressed)

    #       2.3. Press log in
    login_button_pressed = press_element(driver, element_xpath=XPathElements.MESSENGER_LOGIN_BUTTON)
    util.log(method=_method, msg="Login button pressed", page=page, status=login_button_pressed)


def log_in_to_messenger(headless: bool = False, maximise: bool = False, disable_gpu: bool = True) -> WebDriver:
    """
    Method that logs in to messenger
    :return: True if logging in was successful
    """
    _method = "Log_in_to_Messenger"

    util.log(method=_method, msg="Starting", status=True)
    # 0. Check env
    #       0.1. Check that fernet_key exits
    fernet_key = util.get_fernet_key()
    util.log(method=_method, msg="Fernet key found", status=bool(fernet_key))

    #       0.2. Read credentials.json
    credentials_dict = util.read_credentials()
    util.log(method=_method, msg="Credentials found", status=bool(credentials_dict.keys()))

    #       0.3. Setup FirefoxOptions
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    if disable_gpu:
        options.add_argument("--disable-gpu")

    util.log(method=_method, status=bool(options),
             msg=f"Created options for Firefox (headless={headless}, maximised={maximise})")

    # 1. Open messenger.com
    driver = webdriver.Firefox(options=options)
    util.log(method=_method, msg="Booting up Firefox", status=bool(driver))

    driver.get('https://messenger.com')
    _status = 'messenger.com' in driver.current_url
    util.log(method=_method, msg="Loading up messenger.com", status=_status)

    if maximise:
        driver.fullscreen_window()
        util.log(method=_method, msg="Maximising window", status=True)

    #       1.1. Accept basic cookies
    cookies_accepted = press_element(driver, time_to_wait=10, element_xpath=XPathElements.MESSENGER_COOKIES)
    _page = get_page(driver)
    util.log(method=_method, msg="Confirming messenger.com cookies",
             page=_page, status=bool(cookies_accepted))

    # 2. Enter login details
    #       2.0. Decode credentials
    credentials_dict = util.decode_credentials(credentials=credentials_dict, fernet_key=fernet_key)
    util.log(method=_method, msg="Decoding credentials with fernet_key",
             page=_page, status=bool(credentials_dict.keys()))

    time.sleep(2)
    #       2.1 Use them to enter login
    enter_credentials_and_login(
        driver, check_keep_signed_in=True, credentials_dict=credentials_dict, page=_page)

    # -------------------------------------
    # 3. Go through 2fa process
    #       3.1. Accept 2fa process
    _page = get_page(driver)
    accepted_2fa_challenge = press_element(driver, element_xpath=XPathElements.FACEBOOK_2FA_CHALLENGE_START)
    util.log(method=_method, msg="Accepted 2fa challenge", page=_page, status=accepted_2fa_challenge)

    #       3.2. Confirm cookies on facebook.com now
    _page = get_page(driver)
    accepted_fb_cookies = press_element(driver, time_to_wait=10, element_xpath=XPathElements.MESSENGER_COOKIES)
    util.log(method=_method, msg="Accepted facebook cookies", page=_page, status=accepted_fb_cookies)

    #       3.2.1 It is possible that login details need to be written again,
    #             so first check if 'approvals_code' exists
    approval_2fa_code_input_found = find_and_get_element(
        driver, element_xpath=XPathElements.FACEBOOK_2FA_APPROVAL_CODE_INPUT)
    util.log(method=_method, msg="Approval 2FA code input found",
             page=_page, status=bool(approval_2fa_code_input_found))

    if approval_2fa_code_input_found is None:
        enter_credentials_and_login(driver, credentials_dict=credentials_dict, page=_page)

    #       3.3. Enter 2fa code
    current_2fa_code = util.get_current_2fa_code(credentials_dict['totp_code'])
    approval_code_entered = enter_input(
        driver, element_xpath=XPathElements.FACEBOOK_2FA_APPROVAL_CODE_INPUT, input_text=current_2fa_code)
    util.log(
        method=_method, msg=f"Approval code entered [{current_2fa_code}]", status=approval_code_entered, page=_page)

    # 4. Make messenger trust the driver
    _page = get_page(driver)
    in_checkpoint = True
    while in_checkpoint:
        in_checkpoint = press_element(driver, element_xpath=XPathElements.MESSENGER_MOVE_THROUGH_CHECKPOINT)
        util.log(method=_method, msg="Pressed found checkpoint to move through", status=in_checkpoint, page=_page)
        time.sleep(2)

    # 5. Check if driver's url changed to something like: https://www.messenger.com/t/xxxxxxxxxxxxxxxxxx/
    #    if it changed to facebook.com => stupid META logged us into facebook and not into messenger
    if 'messenger.com/t/' not in driver.current_url:
        if 'facebook.com' in driver.current_url:
            util.log(method=_method, page=_page,
                     msg=f"facebook.com loaded instead of messenger.com, current url: {driver.current_url}")

            driver.get("https://messenger.com")
            util.log(method=_method, page=_page,
                     msg="Loaded messenger.com")

            # I don't know, had occurrences of needing to retry logging in few times - need to debug
            enter_credentials_and_login(driver, credentials_dict=credentials_dict, page=_page)

            enter_credentials_and_login(driver, credentials_dict=credentials_dict, page=_page)

        else:
            util.log(method=_method, page=_page, msg="Driver's current url is not messenger and not facebook.com"
                                                     f"Doing a screenshot. Current URL: {driver.current_url}")
            util.make_screenshot(driver, name="NO_CORRECT_URL_FOUND")
            driver.quit()
            raise SystemExit(f"messenger.com/facebook.com did not load in {_method}")

    if not wait_for_element_to_load(driver, element_xpath=XPathElements.MESSENGER_CHATS_LABEL):
        util.log(method=_method, page=_page, msg="Did not find messenger chat label. Connection failed")
        util.make_screenshot(driver)
        logger.info("Page source:")
        logger.info(driver.page_source)
        driver.quit()
        raise SystemExit("[Log in to Messenger]: Failed")

    util.log(method=_method, page=_page, msg="OK")
    return driver


def wait_until_found_and_return_element(
        driver: webdriver,
        look_by: By,
        look_for: str,
        time_to_wait: int = 20
) -> Optional[WebElement]:
    try:
        element = WebDriverWait(driver, time_to_wait).until(
            expected_conditions.visibility_of_element_located((look_by, look_for))
        )
        return element

    except TimeoutException:
        return None


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


def press_enter(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()


def press_element(driver: webdriver, element_xpath: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        element_found.click()
        return True

    util.make_screenshot(driver, f"press_element_{util.normalize_filename(element_xpath)}")
    return False


def find_and_get_element(driver: webdriver, element_xpath: str, time_to_wait=20) -> Optional[WebElement]:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        return element_found

    util.make_screenshot(driver, f"find_and_get_element_{util.normalize_filename(element_xpath)}")
    return None


def find_and_get_elements(driver: webdriver, element_xpath: str, time_to_wait=30) -> List[WebElement]:
    elements_found = wait_until_found_and_return_elements(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if len(elements_found):
        return elements_found

    util.make_screenshot(driver, f"find_and_get_elements_failed_{util.normalize_filename(element_xpath)}")
    return []


def wait_for_element_to_load(driver: webdriver, element_xpath: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        return True

    util.make_screenshot(driver, f"wait_for_element_to_load_{util.normalize_filename(element_xpath)}")
    return False


def enter_input(driver: webdriver, element_xpath: str, input_text: str) -> bool:
    _input_element = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath
    )

    if _input_element is not None:
        _input_element.click()
        ActionChains(driver).send_keys_to_element(_input_element, input_text).perform()
        return True

    util.make_screenshot(driver, f"enter_input_failed_{util.normalize_filename(element_xpath)}")
    return False


def clear_element(driver: webdriver, element_xpath: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if element_found:
        element_found.clear()
        return True

    util.make_screenshot(driver, f"clear_element_fail_{util.normalize_filename(element_xpath)}")
    return False


def get_page(driver):
    """
    Very tough method that recognizes the html page and returns string of a page
    """

    # check for default messenger log in page

    return 'idk yet'

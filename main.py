from common_selenium_methods import log_in_to_messenger, enter_input, press_element

logged_in, driver = log_in_to_messenger(headless=True)
my_url = "https://www.messenger.com/t/100000105556453/"

if logged_in:
    if driver.current_url != my_url:
        driver.get(my_url)
    enter_input(driver=driver, input_element="//div[@aria-label='Message']", input_text="test")
    press_element(driver=driver, element_to_find="//div[@aria-label='Press enter to send']")

# driver.quit()

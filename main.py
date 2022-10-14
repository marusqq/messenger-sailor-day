from common_selenium_methods import log_in_to_messenger, _enter_input, _press_element

logged_in, driver = log_in_to_messenger()

if logged_in:
    driver.get("https://www.messenger.com/t/100000105556453/")
    _enter_input(driver=driver, input_element="//div[@aria-label='Message']", input_text="test")
    _press_element(driver=driver, element_to_find="//div[@aria-label='Press enter to send']")

# driver.quit()

from common_selenium_methods import log_in_to_messenger
log_in_to_messenger()


#
# time.sleep(2)

#
# message_box = selenium_methods.wait_until_found_and_return_element(
#     driver=driver,
#     look_by=By.XPATH,
#     look_for="//div[@aria-label='Message']"
# )
# message_box.click()
# ActionChains(driver).send_keys_to_element(message_box, Keys.ENTER).perform()
#
# message_send = selenium_methods.wait_until_found_and_return_element(
#     driver=driver,
#     look_by=By.XPATH,
#     look_for="//div[@aria-label='Press enter to send']"
# )
# message_send.click()
# driver.quit()

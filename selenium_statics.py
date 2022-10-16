from dataclasses import dataclass


@dataclass
class XPathElements:
    MESSENGER_COOKIES = "//button[@data-testid='cookie-policy-manage-dialog-accept-button']"
    MESSENGER_LOGIN_INPUT = "//input[@id='email']"
    MESSENGER_PASS_INPUT = "//input[@id='pass']"
    MESSENGER_LOGIN_BUTTON = "//button[@id='loginbutton']"
    MESSENGER_KEEP_SIGNED_IN_CHECKBOX = "//input[@type='checkbox']/.."
    MESSENGER_MOVE_THROUGH_CHECKPOINT = "//button[@id='checkpointSubmitButton']"
    MESSENGER_CHATS_LABEL = "//a[starts-with(@aria-label, 'Chats')]"
    FACEBOOK_2FA_APPROVAL_CODE_INPUT = "//input[@id='approvals_code']"
    FACEBOOK_2FA_CHALLENGE_START = "//a[@role='button']"



@dataclass
class SeleniumPage:
    BASE_MESSENGER_LOGIN = {
        "name": "base_messenger_login",
        "url": "messenger.com",
        "elements": [
            XPathElements.MESSENGER_LOGIN_INPUT,
            XPathElements.MESSENGER_PASS_INPUT,
            XPathElements.MESSENGER_LOGIN_BUTTON
        ],
        "help": "base messenger.com page that is loaded"
    }

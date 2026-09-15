import os
from ast import literal_eval

import boto3
from aws_synthetics.common import synthetics_configuration
from aws_synthetics.common import synthetics_logger as logger
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from selenium.webdriver.common.by import By

USER_SSM_PARAM = os.getenv("USER_SSM_PARAM")
PASSWORD_SSM_PARAM = os.getenv("PASSWORD_SSM_PARAM")

client = boto3.client("ssm")
user_response = client.get_parameter(Name=USER_SSM_PARAM, WithDecryption=True)
password_response = client.get_parameter(Name=PASSWORD_SSM_PARAM, WithDecryption=True)

GRAFANA_USERNAME = user_response.get("Parameter").get("Value")
GRAFANA_PASSWORD = password_response.get("Parameter").get("Value")
GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_DASHBOARD_URL = os.getenv("GRAFANA_DASHBOARD_URL")
GRAFANA_DASHBOARD_URL_ALERT_SIM = os.getenv("GRAFANA_DASHBOARD_URL_ALERT_SIM")
SCREENSHOT_ON_STEP_START = bool(
    literal_eval(os.getenv("SCREENSHOT_ON_STEP_START", "False"))
)
SCREENSHOT_ON_STEP_SUCCESS = bool(
    literal_eval(os.getenv("SCREENSHOT_ON_STEP_SUCCESS", "False"))
)
SCREENSHOT_ON_STEP_FAILURE = bool(
    literal_eval(os.getenv("SCREENSHOT_ON_STEP_FAILURE", "True"))
)

TIMEOUT_SECONDS = 10


async def main():
    url = GRAFANA_URL
    url_to_dashboard = GRAFANA_DASHBOARD_URL
    browser = syn_webdriver.Chrome()
    browser.set_viewport_size(1024, 768)

    selector_login_button = "//button[normalize-space()='Log in']"
    selector_login_name = "//*[@placeholder='email or username']"
    selector_find_broken_panels = (
        "//button[@data-testid='data-testid Panel status error']"
    )
    selector_login_password = (
        "//*[@id='current-password' or @name='password']"  # nosec B105
    )

    # Set synthetics configuration
    synthetics_configuration.set_config(
        {
            "screenshot_on_step_start": SCREENSHOT_ON_STEP_START,
            "screenshot_on_step_success": SCREENSHOT_ON_STEP_SUCCESS,
            "screenshot_on_step_failure": SCREENSHOT_ON_STEP_FAILURE,
        }
    )

    def navigate_to_page():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(url)

    def navigate_to_page_two():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(url_to_dashboard)

    def navigate_to_alert_sim_dashboard():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(GRAFANA_DASHBOARD_URL_ALERT_SIM)

    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page)

    # Execute customer steps
    def customer_actions_1():
        logger.debug("Enter username")
        browser.find_element(By.XPATH, selector_login_name).send_keys(GRAFANA_USERNAME)

    await syn_webdriver.execute_step("input", customer_actions_1)

    def customer_actions_2():
        logger.debug("Enter password")
        browser.find_element(By.XPATH, selector_login_password).send_keys(
            GRAFANA_PASSWORD
        )

    await syn_webdriver.execute_step("input", customer_actions_2)

    def customer_actions_3():
        logger.debug("Click to login")
        browser.find_element(By.XPATH, selector_login_button).click()

    await syn_webdriver.execute_step("redirection", customer_actions_3)
    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page_two)

    def customer_actions_4():
        browser.find_element(By.CLASS_NAME, "main-view")

    await syn_webdriver.execute_step("click", customer_actions_4)
    await syn_webdriver.execute_step("navigateToUrl", navigate_to_alert_sim_dashboard)

    def customer_actions_5():
        logger.debug("Checking for broken panels...")
        broken_panels = browser.find_elements(By.XPATH, selector_find_broken_panels)
        if len(broken_panels) > 0:
            raise Exception(
                f"Canary failed: Found {len(broken_panels)} broken panels on the dashboard."
            )

    await syn_webdriver.execute_step("checkBrokenPanels", customer_actions_5)

    logger.info("Canary successfully executed")


async def handler(event, context):
    # user defined log statements using synthetics_logger
    logger.info(f'Selenium Python workflow canary with context: "{context}"')
    logger.info(f'Event received from CloudWatch: "{event}"')
    return await main()

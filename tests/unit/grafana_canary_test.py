import asyncio
import importlib
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

MODULE_NAME = "python.grafana_canary"

ENV = {
    "USER_SSM_PARAM": "/canary/username",
    "PASSWORD_SSM_PARAM": "/canary/password",  # nosec B105
    "GRAFANA_URL": "https://grafana.example.com",
    "GRAFANA_DASHBOARD_URL": "https://grafana.example.com/d/dash",
}


def _ssm_client(username="test-user", password="test-pass"):  # nosec B107
    values = {
        ENV["USER_SSM_PARAM"]: username,
        ENV["PASSWORD_SSM_PARAM"]: password,
    }
    client = MagicMock()
    client.get_parameter.side_effect = lambda Name, WithDecryption: {
        "Parameter": {"Value": values[Name]}
    }
    return client


def _import_canary(monkeypatch, ssm_client=None):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop(MODULE_NAME, None)
    with patch("boto3.client", return_value=ssm_client or _ssm_client()):
        return importlib.import_module(MODULE_NAME)


def test_reads_credentials_from_ssm(monkeypatch):
    canary = _import_canary(
        monkeypatch, _ssm_client(username="alice", password="s3cr3t")
    )  # nosec B106
    assert canary.GRAFANA_USERNAME == "alice"
    assert canary.GRAFANA_PASSWORD == "s3cr3t"  # nosec B105


def test_reads_urls_from_env(monkeypatch):
    canary = _import_canary(monkeypatch)
    assert canary.GRAFANA_URL == ENV["GRAFANA_URL"]
    assert canary.GRAFANA_DASHBOARD_URL == ENV["GRAFANA_DASHBOARD_URL"]


def test_screenshot_flags_default(monkeypatch):
    canary = _import_canary(monkeypatch)
    assert canary.SCREENSHOT_ON_STEP_START is False
    assert canary.SCREENSHOT_ON_STEP_SUCCESS is False
    assert canary.SCREENSHOT_ON_STEP_FAILURE is True


def test_screenshot_flags_from_env(monkeypatch):
    monkeypatch.setenv("SCREENSHOT_ON_STEP_START", "True")
    monkeypatch.setenv("SCREENSHOT_ON_STEP_FAILURE", "False")
    canary = _import_canary(monkeypatch)
    assert canary.SCREENSHOT_ON_STEP_START is True
    assert canary.SCREENSHOT_ON_STEP_FAILURE is False


def test_main_drives_browser_through_expected_steps(monkeypatch):
    canary = _import_canary(
        monkeypatch, _ssm_client(username="alice", password="s3cr3t")
    )  # nosec B106

    browser = MagicMock()
    executed_steps = []

    async def fake_execute_step(name, func):
        executed_steps.append(name)
        func()

    monkeypatch.setattr(canary.syn_webdriver, "Chrome", MagicMock(return_value=browser))
    monkeypatch.setattr(canary.syn_webdriver, "execute_step", fake_execute_step)

    asyncio.run(canary.main())

    browser.set_viewport_size.assert_called_once_with(1024, 768)
    assert executed_steps == [
        "navigateToUrl",
        "input",
        "input",
        "redirection",
        "navigateToUrl",
        "click",
        "navigateToUrl",
        "checkBrokenPanels",
    ]
    browser.get.assert_any_call(ENV["GRAFANA_URL"])
    browser.get.assert_any_call(ENV["GRAFANA_DASHBOARD_URL"])
    browser.find_element.return_value.send_keys.assert_any_call("alice")
    browser.find_element.return_value.send_keys.assert_any_call("s3cr3t")  # nosec B105
    browser.find_element.return_value.click.assert_called_once()


def test_handler_awaits_main_and_returns_its_result(monkeypatch):
    canary = _import_canary(monkeypatch)
    calls = []

    async def fake_main():
        calls.append("main")
        return "canary-result"

    monkeypatch.setattr(canary, "main", fake_main)

    result = asyncio.run(canary.handler({"event": True}, {"context": True}))

    assert result == "canary-result"
    assert calls == ["main"]

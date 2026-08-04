import sys
from types import ModuleType
from unittest.mock import MagicMock


def _stub_module(name):
    module = sys.modules.get(name) or ModuleType(name)
    sys.modules[name] = module
    return module


# aws_synthetics is only available inside the AWS Synthetics Lambda runtime
# layer, not on PyPI, so it can't be a real test dependency. Stub it in
# sys.modules so `grafana_canary` can be imported under test.
_common = _stub_module("aws_synthetics.common")
_common.synthetics_configuration = MagicMock()
_common.synthetics_logger = MagicMock()

_selenium = _stub_module("aws_synthetics.selenium")
_selenium.synthetics_webdriver = MagicMock()

_stub_module("aws_synthetics").common = _common
sys.modules["aws_synthetics"].selenium = _selenium

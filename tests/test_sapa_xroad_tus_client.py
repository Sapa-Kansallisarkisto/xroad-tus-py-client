"""Tests for the X-Road test script
"""

from click.testing import CliRunner
from tusclient.scripts.sapa_xroad_tus_client import (
    main)


def test_sapa_xroad_tus_client():
    """Tests that the script sapa_xroad_tus_client does
    something. For real testing we need to mock the X-Road server,
    but that would be overkill.
    """
    runner = CliRunner()

    result = runner.invoke(main, [])
    assert result.exit_code == 0

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from mcp_server.exceptions import ConfigurationError


def test_require_env_helper_success() -> None:
    from mcp_server.server import _require_env, TT_COOKIES_FILE

    with patch.dict(os.environ, {TT_COOKIES_FILE: "/tmp/tt_cookies.txt"}):
        assert (
            _require_env(
                TT_COOKIES_FILE, "a path containing your TikTok cookies.txt file."
            )
            == "/tmp/tt_cookies.txt"
        )


def test_require_env_helper_missing() -> None:
    from mcp_server.server import _require_env, TT_COOKIES_FILE

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="TT_COOKIES_FILE environment variable is not set"
        ):
            _require_env(
                TT_COOKIES_FILE, "a path containing your TikTok cookies.txt file."
            )

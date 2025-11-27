"""Tests for Windows daemon mode handling.

Windows does not support Unix sockets, so daemon mode must be disabled.
When prefer_daemon=True on Windows, the client should fall back to CLI mode
without attempting to use Unix sockets (which would crash with AttributeError
because asyncio.open_unix_connection doesn't exist on Windows).
"""

import sys
from unittest.mock import patch

import pytest


class TestWindowsDaemonHandling:
    """Test that daemon mode is properly disabled on Windows."""

    def test_create_bd_client_skips_daemon_on_windows(self):
        """Test that create_bd_client disables daemon preference on Windows.

        On Windows, Unix sockets are not supported. If prefer_daemon=True,
        the code should detect Windows and fall back to CLI client without
        attempting to check for Unix socket files.
        """
        from beads_mcp.bd_client import create_bd_client, BdCliClient

        # Mock sys.platform to simulate Windows
        with patch.object(sys, "platform", "win32"):
            # Even with prefer_daemon=True, we should get a CLI client on Windows
            # The daemon code path uses Path.exists() to check for socket files,
            # but on Windows we should skip that entirely
            client = create_bd_client(
                prefer_daemon=True,
                bd_path="/usr/bin/bd",
            )

            # Should return CLI client, not daemon client
            assert isinstance(client, BdCliClient), (
                "On Windows, create_bd_client should return BdCliClient even with prefer_daemon=True"
            )

    def test_create_bd_client_returns_cli_without_daemon_preference(self):
        """Test that create_bd_client returns CLI client when prefer_daemon=False."""
        from beads_mcp.bd_client import create_bd_client, BdCliClient

        client = create_bd_client(
            prefer_daemon=False,
            bd_path="/usr/bin/bd",
        )

        assert isinstance(client, BdCliClient)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_actual_windows_platform_skips_daemon(self):
        """Test on actual Windows platform that daemon is skipped."""
        from beads_mcp.bd_client import create_bd_client, BdCliClient

        # On actual Windows, daemon should be skipped
        client = create_bd_client(
            prefer_daemon=True,
            bd_path="/usr/bin/bd",
        )

        assert isinstance(client, BdCliClient), (
            "On Windows, create_bd_client should return BdCliClient"
        )

"""Integration test — spins up MCP server over stdio, sends a tool call, verifies JSON response."""

from __future__ import annotations

import asyncio
import json
import sys

# MCP JSON-RPC message IDs
_INIT_ID = 1
_LIST_ID = 2


async def _read_response(proc: asyncio.subprocess.Process) -> dict:
    """Read one newline-delimited JSON-RPC response from stdout."""
    assert proc.stdout is not None
    line = await asyncio.wait_for(proc.stdout.readline(), timeout=15)
    if not line:
        raise RuntimeError("Server closed stdout without response")
    return json.loads(line)


async def _send(proc: asyncio.subprocess.Process, msg: dict) -> None:
    """Send a JSON-RPC message as a newline-terminated JSON string."""
    assert proc.stdin is not None
    data = json.dumps(msg) + "\n"
    proc.stdin.write(data.encode())
    await proc.stdin.drain()


async def _integration_test() -> None:
    """Spin up server, initialize, call tools/list, verify shape."""
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "mcp_server.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdin is not None

    try:
        # 1. Send initialize request
        init_req = {
            "jsonrpc": "2.0",
            "id": _INIT_ID,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "integration-test", "version": "0.1.0"},
            },
        }
        await _send(proc, init_req)
        init_resp = await _read_response(proc)
        assert init_resp.get("id") == _INIT_ID, f"Bad init response: {init_resp}"
        assert "result" in init_resp, f"Init failed: {init_resp}"
        print(
            f"[integ] Initialize OK — server: {init_resp['result'].get('serverInfo', {}).get('name')}"
        )

        # 2. Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        await _send(proc, initialized_notif)

        # 3. Call tools/list to verify tool registration
        list_req = {
            "jsonrpc": "2.0",
            "id": _LIST_ID,
            "method": "tools/list",
            "params": {},
        }
        await _send(proc, list_req)
        list_resp = await _read_response(proc)
        assert "result" in list_resp, f"tools/list failed: {list_resp}"
        tools = list_resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        assert "scrape_tiktok_user" in tool_names, f"Missing tool. Got: {tool_names}"
        assert "analyze_competitor" in tool_names, f"Missing tool. Got: {tool_names}"
        print(f"[integ] tools/list OK — {len(tools)} tools: {tool_names}")

        print("[integ] PASS — MCP server responds correctly to JSON-RPC")

    finally:
        proc.stdin.close()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except asyncio.TimeoutError:
            proc.kill()


def main() -> None:
    asyncio.run(_integration_test())


if __name__ == "__main__":
    main()

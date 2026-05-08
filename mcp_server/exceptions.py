# mcp_server/exceptions.py
"""Custom exception hierarchy for MCP server."""

from __future__ import annotations


class MCPServerError(ValueError):
    """Base exception for MCP server errors. Inherits ValueError for FastMCP compatibility."""


class ValidationError(MCPServerError):
    """Raised for invalid input validation (handle, limit, URL)."""


class ConfigurationError(MCPServerError):
    """Raised for missing or invalid configuration (env vars)."""


class AnalysisError(MCPServerError):
    """Raised when analysis fails (e.g., empty OpenAI response)."""


__all__ = ["MCPServerError", "ValidationError", "ConfigurationError", "AnalysisError"]

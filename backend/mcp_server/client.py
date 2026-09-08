"""Custom MCP client that connects to the NotesLab MCP server over stdio."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent / "server.py"
PYTHON = Path(__file__).resolve().parents[1] / ".venv" / "bin" / "python"


async def demo() -> None:
    params = StdioServerParameters(
        command=str(PYTHON),
        args=["-m", "mcp_server.server"],
        cwd=str(Path(__file__).resolve().parents[1]),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            resources = await session.list_resources()
            tools = await session.list_tools()

            print("=== NotesLab MCP custom client ===")
            print("Resources:")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name or resource.uri}")

            print("Tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            overview = await session.read_resource("noteslab://app/overview")
            print("\nResource read (overview):")
            for block in overview.contents:
                text = getattr(block, "text", None) or str(block)
                print(f"  {text[:400]}")

            result = await session.call_tool("search_notes", {"query": "note", "limit": 3})
            print("\nTool call (search_notes):")
            for item in result.content:
                text = getattr(item, "text", None) or str(item)
                print(f"  {text}")


def main() -> None:
    try:
        asyncio.run(demo())
    except Exception as exc:  # noqa: BLE001 - CLI surface
        print(f"MCP client failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

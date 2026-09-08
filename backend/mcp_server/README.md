# NotesLab MCP (Cursor)

Add this to your Cursor MCP settings (Cursor Settings → MCP), adjusting the absolute path:

```json
{
  "mcpServers": {
    "noteslab": {
      "command": "/Users/ibrahimali/arbisoft-internship-2026/backend/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/Users/ibrahimali/arbisoft-internship-2026/backend"
    }
  }
}
```

## What it exposes

- **Resource:** `noteslab://app/overview`
- **Tool:** `search_notes(query, limit=5)`

## Custom client demo

```bash
cd backend
source .venv/bin/activate
python -m mcp_server.client
```

Start the FastAPI app at least once so `notes.db` exists if you want live note search results.

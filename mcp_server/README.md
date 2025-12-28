# Stock Analysis MCP Server

This MCP server connects your Claude Desktop to your local Stock Analysis API.

## Prerequisites
1.  **Backend API Running**: Ensure your API is running on port 8000.
    ```bash
    # Open a new terminal
    cd stock
    python -m uvicorn api:app --port 8000
    ```
2.  **Install FastMCP**:
    ```bash
    pip install fastmcp requests
    ```

## Installation for Claude Desktop

1.  Open your Claude Desktop configuration file:
    -   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    -   **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

2.  Add the following configuration (Replace `YOUR_USERNAME` and paths as needed):

    ```json
    {
      "mcpServers": {
        "stock-analysis-local": {
          "command": "python",
          "args": [
            "c:\\Users\\enver\\OneDrive - Kadir Has University\\MIS453\\project_453\\mcp_server\\server.py"
          ]
        }
      }
    }
    ```
    *Note: Make sure the path to `server.py` is the absolute path on your machine.*

3.  Restart Claude Desktop.

## Usage in Claude
Once installed, you can ask Claude questions like:
- "Check the stock prediction for NVDA"
- "Give me a financial analysis of AAPL"
- "Find me 5 undervalued stocks"

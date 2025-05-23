# Browser Use with fastmcp (HTTP/SSE)

This project demonstrates using [browser-use](https://github.com/browser-use/browser-use) controlled via the **fastmcp** framework, utilizing the **HTTP/SSE (Server-Sent Events) transport**. The application can be invoked manually using HTTP clients like `curl` or integrated with AI Agents and other services that can communicate over HTTP.

## Purpose

The purpose of this project is to provide a `browser-use` agent as a service managed by **fastmcp**, running in headless mode (potentially within a Docker container). This service can be consumed as a tool by AI agents or other applications, allowing them to perform web browsing tasks and retrieve results. It uses HTTP for communication, making it suitable for a wide range of integrations. Server-Sent Events (SSE) may be used for streaming responses where applicable.

## Setup Instructions

### Prerequisites

*   Python 3.11+
*   HTTP client tools (optional, for manual interaction), like `curl`.

### Running Locally

1.  Clone the repo: `git clone <URL to this project>`
2.  Navigate to the project directory.
3.  Create a virtual environment: `python3 -m venv .venv`
4.  Activate the virtual environment: `source .venv/bin/activate` (on Linux/macOS) or `.\.venv\Scripts\activate` (on Windows).
5.  Install the dependencies: `pip install -r requirements.txt`
6.  Run the server: `python server.py`
    This will start the `fastmcp` application, which by default listens on `0.0.0.0` at the port specified by the `PORT` environment variable (defaulting to `8000`). The MCP functions are exposed under the `/mcp` path. The application ID is configured via the `APP_ID` environment variable (defaulting to `browser_agent_app_default`).

### Interacting with the Service (using HTTP)

The application uses `fastmcp` and exposes functions over HTTP. The base path for MCP calls is `/mcp`. Tool calls are made via POST requests to `http://<host>:<port>/mcp/call/<tool_name>`.

**1. Using `curl` (Command Line):**

*   **To call the `query` function:**
    The `query` function expects a JSON payload with a "task" key.
    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -d '{"task": "go to google and get me title and responsibilities of two software engineering jobs in phoenix along with their links"}' \
         http://localhost:8000/mcp/call/query
    ```
    The response will be a JSON object containing the result, for example:
    `{"result": "..."}` or `{"error": "...", "status_code": 400}`.

*   **To call the `terminate` function:**
    The `terminate` function currently takes no arguments (or an empty JSON object).
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:8000/mcp/call/terminate
    ```
    The response will be a JSON object, for example:
    `{"message": "Request terminated and browser closed."}`.

**Note on Responses:** For simple tool calls like these, `fastmcp` typically returns a single JSON response. If a tool were designed to stream updates, Server-Sent Events (SSE) might be used, providing a stream of events to the client.

### Running with Docker

1.  Ensure you have Docker installed.
2.  Navigate to the project folder.
3.  Build the Docker image: `docker compose build` (or `docker build -t browser-agent-mcp-http .`)
4.  Run the container: `docker compose up`
    This will start the `browser_agent` service, which by default exposes port `8000` on your host machine, mapped to port `8000` inside the container (as defined in `docker-compose.yml` and `Dockerfile`).
5.  Interact with the service using an HTTP client like `curl` as described in the "Interacting with the Service (using HTTP)" section. For example:
    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -d '{"task": "What is the current weather in Berlin?"}' \
         http://localhost:8000/mcp/call/query
    ```

### Terminating In-Flight Requests

To terminate an ongoing browser task, use the `terminate` function via HTTP as described above. This will attempt to close the browser and stop the current agent's execution.
The `terminate` function currently does not take a specific request ID; it terminates the `current_agent` if one is active.

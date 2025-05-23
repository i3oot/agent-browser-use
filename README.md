# ADK-Powered Browser Agent (A2A Protocol)

## Purpose

This project provides an AI agent built with the Google Agent Development Kit (ADK). It leverages the `browser-use` library to perform web browsing and automation tasks. The agent exposes its capabilities via the Agent-to-Agent (A2A) communication protocol, allowing other AI agents (or A2A-compatible clients) to delegate web-based tasks to it.

## Environment Variables

Before running the agent, ensure you have a `.env` file in the project root directory with the following environment variables:

*   `OPENAI_API_KEY`: **Required**. Your OpenAI API key.
*   `OPENAI_API_BASE`: (Optional) The base URL for OpenAI compatible APIs. Defaults to an Azure endpoint if not set. Example: `https://api.openai.com/v1`.
*   `OPENAI_MODEL_NAME`: (Optional) The OpenAI model to be used by the `browser-use` library for its internal logic. Defaults to `gpt-4o-mini`.
*   `ADK_MODEL_NAME`: (Optional) The model name the ADK framework uses for the root agent's logic. Defaults to `gpt-4o-mini`.

## Setup Instructions

### Running with Docker (Recommended)

1.  **Ensure Docker is installed.**
2.  **Clone the repository:**
    ```bash
    git clone <github URL to this project>
    cd <project-folder-name>
    ```
3.  **Create your `.env` file** in the project root with the necessary environment variables (see "Environment Variables" section above).
4.  **Build the Docker image:**
    ```bash
    docker build -t adk-browser-agent .
    ```
5.  **Run the Docker container:**
    ```bash
    docker run -d -p 8080:8080 --env-file .env adk-browser-agent
    ```
    *   This command runs the agent in detached mode (`-d`).
    *   It maps port `8080` of the container to port `8080` on your host machine.
    *   The `--env-file .env` flag loads the environment variables from your `.env` file.
    *   The agent will now be listening on `http://localhost:8080`.

### Running Locally (for Development)

1.  **Ensure Python 3.11+ is installed.**
2.  **Clone the repository:**
    ```bash
    git clone <github URL to this project>
    cd <project-folder-name>
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Install Playwright browsers and their dependencies:**
    ```bash
    playwright install --with-deps
    ```
6.  **Set up your `.env` file** as described in the "Environment Variables" section, or ensure these variables are exported in your shell environment.
7.  **Run the agent using the ADK CLI:**
    ```bash
    adk api_server browser_agent.agent --host 0.0.0.0 --port 8080
    ```
    *   The agent will now be listening on `http://localhost:8080`.

## Interacting with the Agent

This agent communicates using the Agent-to-Agent (A2A) protocol. A2A-compatible clients or other ADK agents can interact with it by sending JSON-RPC 2.0 messages to its HTTP endpoint (e.g., `http://localhost:8080` if running locally or via Docker as described above).

The primary tool exposed by this agent is `web_browser_tool`. To use it, an A2A client would send a request to invoke this tool with a `task` parameter describing the web browsing objective.

For example, a JSON-RPC request might look like (this is a conceptual example):
```json
{
  "jsonrpc": "2.0",
  "method": "execute_tool",
  "params": {
    "tool_name": "web_browser_tool",
    "inputs": {
      "task": "Find the current weather in London"
    }
  },
  "id": "1"
}
```

The agent will then process this request using the `browser-use` library and return the result.

For detailed information on the A2A protocol and how to build clients, please refer to the official [A2A Protocol Specification](https://github.com/google/A2A/).

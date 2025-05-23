import os # Added for environment variable access
import os # Ensure os is imported
from dotenv import load_dotenv
load_dotenv(override=True)

from typing import Dict, Any 
from fastmcp import Mcp, Message # Removed MqttConfig, AppConfig
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig

# Define App ID using environment variable with a default for HTTP transport
app_id = os.getenv("APP_ID", "browser_agent_app_default") # Adjusted default as per task example

# Instantiate Mcp directly with app_id
mcp = Mcp(app_id) 

browser = Browser(config=BrowserConfig(headless=True))
current_agent = None

# Note: Pydantic models QueryRequest and QueryResponse are removed as their primary use was for FastAPI.
# Input 'task' will come from Message.payload (assuming it's a dict with a 'task' key or just the string directly).
# Output 'result' will be returned directly.

@mcp.expose(
    name="query", 
    description="Executes a browser-based task. Expects a 'task' string or a dict {'task': '...'} in the message payload.",
    tags=["browser", "agent"]
)
async def query(message: Message) -> Dict[str, Any]:
    """
    Executes a browser-based task based on the provided task string.
    Expects message.payload to be a string containing the task, 
    or a dictionary like {"task": "your task description"}.
    Returns a dictionary with the result of the agent's execution or an error message.
    """
    global current_agent
    
    task_description = ""
    if isinstance(message.payload, dict):
        task_description = message.payload.get("task")
    elif isinstance(message.payload, str):
        task_description = message.payload

    if not task_description:
        # fastmcp might have specific error types or expect a certain return format for errors.
        # For now, returning a dictionary indicating error.
        return {"error": "Task cannot be empty", "status_code": 400}
    
    current_agent = Agent(
        task=task_description,
        llm=ChatOpenAI(base_url="https://models.inference.ai.azure.com", model="gpt-4o-mini"),
        browser=browser,
    )
    result = await current_agent.run()
    
    final_result_text = result.final_result()
    print(f"result >>>>>>> {final_result_text}")
    # Assuming fastmcp can handle direct dictionary returns as responses.
    return {"result": final_result_text}

@mcp.expose(
    name="terminate", 
    description="Terminates the current browser task and closes the browser.",
    tags=["browser", "agent"]
)
async def terminate(message: Message) -> Dict[str, str]:
    """
    Terminates the currently active browser agent and closes the browser.
    Returns a message indicating the outcome.
    """
    global current_agent
    if current_agent:
        if current_agent.browser_context: # browser_context might be specific to how Agent manages it
            await current_agent.browser.close() # Ensure this is the correct way to close
        current_agent = None # Clear the agent after termination
        return {"message": "Request terminated and browser closed."}
    else:
        return {"message": "No active request to terminate."}

if __name__ == "__main__":
    # Define port for HTTP transport using environment variable with a default
    app_port = int(os.getenv("PORT", 8000))

    # Run Mcp with streamable-http transport
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=app_port,
        path="/mcp" # Endpoint path for MCP
    )
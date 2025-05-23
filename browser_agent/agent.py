import os
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_openai import ChatOpenAI
from browser_use import Agent as BrowserUseAgent, Browser, BrowserConfig
from google.adk.agents import Agent as AdkAgent
from google.adk.tools import LongRunningFunctionTool

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent',
        url='http://localhost:9999/', # Agent will run here
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True), # Basic capabilities
        skills=[
            AgentSkill(
                id='hello_world',
                name='Returns hello world',
                description='just returns hello world',
                tags=['hello world'],
                examples=['hi', 'hello world'],
            ),
        ], # Includes the skill defined above
    )


# Global browser instance
browser = Browser(config=BrowserConfig(headless=True))

async def perform_browser_task(task: str) -> dict:
    """
    Automates web browsing for a given task and extracts information.

    This function takes a natural language task, uses a browser automation agent
    to perform the necessary web navigation and interaction, and returns the
    extracted information or an error message.

    Args:
        task: A string describing the task to be performed. 
              For example, "Find the current weather in London" or
              "What are the top 3 news headlines on BBC.com?".

    Returns:
        A dictionary with the status of the operation and the result.
        If successful:
            {"status": "success", "result": "extracted content"}
        If an error occurs:
            {"status": "error", "error_message": "description of the error"}
    """
    try:
        # Create a new BrowserUseAgent instance for each task
        # It will use the global browser instance
        agent = BrowserUseAgent(
            task=task,
            llm=ChatOpenAI(
                base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"), 
                model=os.getenv("OPENAI_MODEL_NAME", "arcee-ai/virtuoso-medium-v2"),
                api_key=os.getenv("OPENROUTER_API_KEY") # Ensure API key is loaded
            ),
            browser=browser,
        )
        result = await agent.run()
        final_output = result.final_result()
        if final_output:
            print(f"Final Output: {final_output}")
            return {"status": "success", "result": final_output}
        else:
            print(f"No Final Output: {result}")
            # If final_result is empty, try to get the last extracted content
            # This part depends on the structure of 'result' object from browser_use.Agent
            if result.result and result.result[-1].extracted_content:
                 return {"status": "success", "result": result.result[-1].extracted_content}
            return {"status": "success", "result": "No specific content extracted, but task may have been performed."}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Wrap the function with LongRunningFunctionTool
browser_tool = LongRunningFunctionTool(
    func=perform_browser_task
)

# Define the main ADK agent
root_agent = LlmAgent(
    name="browser_navigation_agent", # Name for the agent
    description="An agent that can browse the web to find information, answer questions, or complete tasks as requested.", # Description of the agent's capabilities
    model=LiteLlm(model=os.getenv("OPENAI_MODEL_NAME", "gemini/gemini-2.5-flash-preview-05-20")),

    #model_parameters={"base_url": os.getenv("OPENAI_API_BASE")}, # Example if ADK needs explicit base_url
    tools=[browser_tool], # List of tools the agent can use
    
    instruction=(
        "You are a helpful assistant. Your primary function is to use the "
        "web_browser_tool to accomplish tasks that require web browsing. "
        "Understand the user's request, formulate it as a clear task for the "
        "web_browser_tool, and then use the tool to get the information. "
        "Present the result clearly to the user. If the tool returns an error, "
        "inform the user about the error."
    )
)

# Note: The main execution logic (e.g., starting the agent to listen for requests)
# would typically be handled by the ADK framework or A2A SDK, not in this file directly.
# This file now defines the agent and its tools.

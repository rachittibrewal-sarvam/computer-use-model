"""
This is a basic example of how to use the CUA model along with the Responses API.
The code will run a loop taking screenshots and perform actions suggested by the model.
Make sure to install the required packages before running the script.
"""

import argparse
import asyncio
import logging
import os

import cua
import morphvm_computer
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()

# Computer use instructions for the LLM model to follow
COMPUTER_USE_INSTRUCTIONS = """
# Computer Use Instructions for LLM Model

## General Principles
- Always analyze the current screen state before taking any action
- Plan a sequence of steps before executing complex tasks
- Prioritize speed when interacting with UI elements

## Navigation Best Practices
- Use direct clicks on navigation elements rather than typing URLs when possible
- Identify and use keyboard shortcuts when available (Cmd+C/Ctrl+C for copy, Cmd+V/Ctrl+V for paste, etc.)
- Use Tab to navigate through form fields efficiently
- Scroll slowly and incrementally when scanning for information, trying using keyboard shortcuts for page up and page down when possible instead of scrolling when possible.

## UI Interaction Guidelines
- Click on the center of buttons and interactive elements
- Double-check text input before submitting forms
- Use appropriate waits between actions that trigger UI changes (loading screens, animations)
- When encountering dropdown menus, fully expand them before making a selection

## Error Handling
- If an action doesn't produce the expected result, try an alternative approach
- Recognize common error messages and respond appropriately
- When faced with an unexpected popup, carefully read its content before deciding how to proceed
- If navigation leads to a wrong page, use browser back buttons or home navigation to reorient

## Efficiency Techniques
- Utilize search functions within applications when available
- Use context menus (right-click) to access additional options
- Break complex tasks into smaller, manageable segments
- Recognize when a task can be achieved through keyboard shortcuts instead of mouse interactions

## Platform-Specific Considerations
- On macOS: Use Cmd for keyboard shortcuts (Cmd+Space for Spotlight, Cmd+Tab for app switching)
- On Windows: Use Ctrl for most shortcuts, Windows key for system functions
- On web browsers: Check for browser-specific features (Chrome omnibox, Firefox add-ons)
- On mobile interfaces: Adapt to touch-based interactions and consider screen size limitations
"""

async def main():

    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--instructions", dest="instructions",
        default="Open web browser and go to microsoft.com.",
        help="Instructions to follow")
    parser.add_argument("--model", dest="model",
        default="computer-use-preview")
    parser.add_argument("--endpoint", default="azure",
        help="The endpoint to use, either OpenAI or Azure OpenAI")
    parser.add_argument("--autoplay", dest="autoplay", action="store_true",
        default=True, help="Autoplay actions without confirmation")
    parser.add_argument("--environment", dest="environment", default="Darwin")
    parser.add_argument("--use_enhanced_instructions", dest="use_enhanced_instructions", 
        action="store_true", default=True, help="Use enhanced computer use instructions")
    args = parser.parse_args()

    if args.endpoint == "azure":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-03-01-preview",
        )
    else:
        client = openai.AsyncOpenAI()

    model = args.model

    # Computer is used to take screenshots and send keystrokes or mouse clicks
    computer = morphvm_computer.LocalComputer()

    # Scaler is used to resize the screen to a smaller size
    # computer = cua.Scaler(computer, (1024, 768))

    # Agent to run the CUA model and keep track of state
    agent = cua.Agent(client, model, computer)

    # Get the user request
    if args.instructions:
        user_input = args.instructions
    else:
        user_input = input("Please enter the initial task: ")

    # Add enhanced computer use instructions if enabled
    if args.use_enhanced_instructions:
        user_input = f"{COMPUTER_USE_INSTRUCTIONS}\n\nUser Task: {user_input}"
        logger.info("Using enhanced computer use instructions")
    
    logger.info(f"User: {user_input}")
    agent.start_task()
    while True:
        if not user_input and agent.requires_user_input:
            logger.info("")
            user_input = input("User: ")
        await agent.continue_task(user_input)
        user_input = None
        if agent.requires_consent and not args.autoplay:
            input("Press Enter to run computer tool...")
        elif agent.pending_safety_checks and not args.autoplay:
            logger.info(f"Safety checks: {agent.pending_safety_checks}")
            input("Press Enter to acknowledge and continue...")
        if agent.reasoning_summary:
            logger.info("")
            logger.info(f"Action: {agent.reasoning_summary}")
        for action, action_args in agent.actions:
            logger.info(f"  {action} {action_args}")
        if agent.messages:
            logger.info("")
            logger.info(f'Agent: {"".join(agent.messages)}')

if __name__ == "__main__":
    asyncio.run(main())

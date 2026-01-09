import os
from dotenv import load_dotenv
load_dotenv()

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    # Create UserClient
    user_client = UserClient()
    
    # Create all tools
    tools = [
        WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT),
        GetUserByIdTool(user_client=user_client),
        SearchUsersTool(user_client=user_client),
        CreateUserTool(user_client=user_client),
        UpdateUserTool(user_client=user_client),
        DeleteUserTool(user_client=user_client)
    ]
    
    # Create DialClient with all tools
    # You can experiment with different models: gpt-4o, gpt-4o-mini, claude-opus-4-20250514, gemini-2.5-pro, etc.
    client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4o",  # Try different models here
        api_key=API_KEY,
        tools=tools
    )
    
    # Create Conversation and add System message
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))
    
    print("\n" + "="*50)
    print("User Management Agent Started")
    print("="*50)
    print("Type your requests or 'exit' to quit\n")
    
    # Run infinite loop for conversation
    while True:
        user_input = input("> ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
        
        # Add User message to Conversation
        conversation.add_message(Message(role=Role.USER, content=user_input))
        
        try:
            # Call DialClient with conversation history
            assistant_message = client.get_completion(conversation.get_messages())
            
            # Add Assistant message to Conversation and print its content
            conversation.add_message(assistant_message)
            print(f"\nAssistant: {assistant_message.content}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")


main()

#TODO:
# Request sample:
# Add Andrej Karpathy as a new user
import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        self.__api_key = api_key
        
        # Prepare tools dict where key is tool name and value is tool instance
        self.__tools_dict = {tool.name: tool for tool in (tools or [])}
        
        # Prepare tools list with tool schemas
        self.__tools = [tool.schema for tool in (tools or [])]
        
        # Optional: print endpoint and tools schemas
        print(f"Endpoint: {self.__endpoint}")
        print(f"Tools: {len(self.__tools)} tools registered")
        for tool_schema in self.__tools:
            print(f"  - {tool_schema['function']['name']}")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        headers = {
            "api-key": self.__api_key,
            "Content-Type": "application/json"
        }
        
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": self.__tools
        }
        
        if print_request:
            print(f"\n{'='*50}\nREQUEST - Message History ({len(messages)} messages)\n{'='*50}")
        
        response = requests.post(url=self.__endpoint, headers=headers, json=request_data)
        
        if response.status_code == 200:
            response_json = response.json()
            choices = response_json["choices"]
            choice = choices[0]
            
            if print_request:
                print(f"RESPONSE:\n{json.dumps(choice, indent=2)}\n{'='*50}")
            
            message_data = choice["message"]
            content = message_data.get("content", "")
            tool_calls = message_data.get("tool_calls", None)
            
            ai_response = Message(
                role=Role.ASSISTANT,
                content=content,
                tool_calls=tool_calls
            )
            
            if choice["finish_reason"] == "tool_calls":
                messages.append(ai_response)
                tool_messages = self._process_tool_calls(tool_calls)
                messages.extend(tool_messages)
                return self.get_completion(messages, print_request)
            else:
                return ai_response
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            tool_call_id = tool_call["id"]
            function = tool_call["function"]
            function_name = function["name"]
            arguments = json.loads(function["arguments"])
            
            tool_execution_result = self._call_tool(function_name, arguments)
            
            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,
                content=tool_execution_result
            ))
            
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        if function_name in self.__tools_dict:
            tool = self.__tools_dict[function_name]
            return tool.execute(arguments)
        else:
            return f"Unknown function: {function_name}"

from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Searches for users based on optional criteria like name, surname, email, or gender."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "User's first name"
                },
                "surname": {
                    "type": "string",
                    "description": "User's surname"
                },
                "email": {
                    "type": "string",
                    "description": "User's email address"
                },
                "gender": {
                    "type": "string",
                    "description": "User's gender"
                }
            },
            "required": []
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            return self._user_client.search_users(**arguments)
        except Exception as e:
            return f"Error while searching users: {str(e)}"

from typing import List, Optional, Dict
import openai
import os

class MCPAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = self.api_key

    async def process(self, prompt: str, context: Optional[List[str]] = None, parameters: Optional[Dict] = None) -> str:
        """
        Process the given prompt using the AI agent.
        
        Args:
            prompt: The input prompt to process
            context: Optional context information
            parameters: Optional processing parameters
            
        Returns:
            str: The processed response
        """
        try:
            # Prepare the messages
            messages = []
            if context:
                for ctx in context:
                    messages.append({"role": "system", "content": ctx})
            
            messages.append({"role": "user", "content": prompt})

            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=parameters.get("temperature", 0.7) if parameters else 0.7,
                max_tokens=parameters.get("max_tokens", 1000) if parameters else 1000
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 
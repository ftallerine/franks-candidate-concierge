import os
from openai import OpenAI
from typing import Optional

class GPTService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=self.api_key)

    def get_completion(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7, model: Optional[str] = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log or handle error as needed
            print(f"Error calling OpenAI API: {e}")
            return "[Error: Unable to get response from GPT API]" 
from openai import OpenAI as OpenAIClient
from openai.types.chat import ChatCompletion
from .base_provider import BaseProvider
from typing import Dict


class OpenAI(BaseProvider):
    def _initialize_client(self):
        return OpenAIClient(api_key=self.api_key)

    def _validate_access(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def _format_prompt(self, prompt: str, system_prompt: str = None) -> str:
        template = self.model_config["promptTemplate"]
        system = system_prompt or self.model_config.get("systemPrompt", "")

        if "{system}" in template and "{prompt}" in template:
            return template.format(system=system, prompt=prompt)
        return template.replace("%1", prompt)

    def generate(self, prompt: str, **kwargs) -> Dict:
        formatted_prompt = self._format_prompt(prompt, kwargs.get("system_prompt"))

        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=kwargs.get("max_tokens", 2048),
            temperature=kwargs.get("temperature", 0.7),
        )

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        input_cost = (input_tokens / 1000) * self.model_config["inputPricePer1KTokens"]
        output_cost = (output_tokens / 1000) * self.model_config[
            "outputPricePer1KTokens"
        ]
        total_cost = round(input_cost + output_cost, 6)

        return {
            "text": response.choices[0].message.content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
        }

    def count_tokens(self, text: str) -> int:
        try:
            enc = self.client.tokenizers.from_pretrained("gpt2")
            return len(enc.encode(text))
        except Exception:
            # Fallback to approximate token count
            return len(text.split())

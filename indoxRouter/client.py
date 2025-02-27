from importlib import import_module
from pathlib import Path


class Client:
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        self.provider_name, self.model_part = self._parse_model_name()
        self.provider = self._initialize_provider()

    def _parse_model_name(self):
        if "/" not in self.model_name:
            raise ValueError("Model name must be in 'provider/model-name' format")
        provider, model = self.model_name.split("/", 1)
        return provider.lower(), model

    def _initialize_provider(self):
        # Check if provider module exists
        providers_dir = Path(__file__).parent / "providers"
        provider_path = providers_dir / f"{self.provider_name}.py"

        if not provider_path.exists():
            raise ValueError(f"Provider {self.provider_name} not supported")

        # Dynamically import provider module
        try:
            module = import_module(f"providers.{self.provider_name}")
            provider_class = getattr(module, self.provider_name.title())
            return provider_class(api_key=self.api_key, model_name=self.model_part)
        except Exception as e:
            raise RuntimeError(f"Error initializing provider: {str(e)}")

    def generate(self, **kwargs):
        return self.provider.generate(**kwargs)

    def get_model_info(self):
        return self.provider.get_model_info()

    def count_tokens(self, text: str) -> int:
        return self.provider.count_tokens(text)

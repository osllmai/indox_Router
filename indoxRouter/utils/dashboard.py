"""
Dashboard utility module for IndoxRouter.
Provides a Gradio interface for testing the IndoxRouter application.
"""

import os
import sys
import json
import gradio as gr
import time
import platform
from typing import Dict, List, Optional, Tuple
import logging

# Add the parent directory to the path to import from indoxRouter
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_parent_dir)

# Use absolute imports
from indoxRouter.utils.auth import AuthManager
from indoxRouter.utils.config import get_config
from indoxRouter.client import Client

# Configure logging
logger = logging.getLogger(__name__)


class Dashboard:
    """
    Gradio dashboard for testing the IndoxRouter application.
    """

    def __init__(self):
        """Initialize the dashboard."""
        self.config = get_config()
        self.auth_manager = AuthManager()
        self.client = None
        self.current_user = None
        self.api_keys = []
        self.providers = self._load_providers()
        self.models = self._load_models()

    def _load_providers(self) -> List[str]:
        """Load available providers."""
        providers_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "providers"
        )
        providers = []

        for file in os.listdir(providers_dir):
            if file.endswith(".json"):
                providers.append(file.split(".")[0])

        # Ensure all providers are included, even if JSON files are missing
        all_providers = [
            "openai",
            "claude",
            "mistral",
            "cohere",
            "google",
            "meta",
            "ai21",
            "llama",
            "nvidia",
            "deepseek",
            "databricks",
        ]

        for provider in all_providers:
            if provider not in providers:
                providers.append(provider)

        return sorted(providers)

    def _load_models(self) -> Dict[str, List[str]]:
        """Load available models for each provider."""
        providers_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "providers"
        )
        models = {}

        for provider in self.providers:
            provider_file = os.path.join(providers_dir, f"{provider}.json")
            if os.path.exists(provider_file):
                try:
                    with open(provider_file, "r") as f:
                        provider_models = json.load(f)
                        models[provider] = [
                            model["modelName"] for model in provider_models
                        ]
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error loading models for {provider}: {e}")
                    models[provider] = [f"{provider}-default-model"]
            else:
                # Default models for providers without JSON files
                if provider == "llama":
                    models[provider] = [
                        "meta-llama-3-8b-instruct",
                        "meta-llama-3-70b-instruct",
                        "meta-llama-3-405b-instruct",
                    ]
                elif provider == "nvidia":
                    models[provider] = [
                        "nvidia-tensorrt-llm-mixtral-8x7b-instruct",
                        "nvidia-nemotron-4-340b-instruct",
                        "nvidia-nemo-sirius-8b",
                    ]
                elif provider == "deepseek":
                    models[provider] = [
                        "deepseek-llm-67b-chat",
                        "deepseek-coder-33b-instruct",
                        "deepseek-math-7b",
                    ]
                elif provider == "databricks":
                    models[provider] = [
                        "databricks-dbrx-instruct",
                        "databricks-dbrx-instruct-4k",
                    ]
                else:
                    models[provider] = [f"{provider}-default-model"]

        return models

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate a user.

        Args:
            email: User email
            password: User password

        Returns:
            Tuple of (success, message)
        """
        try:
            # Authenticate the user
            user = self.auth_manager.authenticate_user(email, password)
            if not user:
                return False, "Invalid email or password"

            # Set the current user
            self.current_user = user

            # Load the user's API keys if not admin
            if not user.get("is_admin", False):
                self.api_keys = self.auth_manager.get_user_api_keys(user["id"])

            # Create a client with the user's credentials
            self.client = Client(
                base_url=self.config.get("api", {}).get(
                    "base_url", "http://localhost:8000"
                ),
                api_key=self.api_keys[0]["key"] if self.api_keys else None,
            )

            return True, f"Welcome, {user.get('first_name', email)}!"
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, f"Login failed: {str(e)}"

    def register(
        self,
        email: str,
        password: str,
        confirm_password: str,
        first_name: str,
        last_name: str,
    ) -> Tuple[bool, str]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            confirm_password: Password confirmation
            first_name: User's first name
            last_name: User's last name

        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            if not email or not password:
                return False, "Email and password are required"

            if password != confirm_password:
                return False, "Passwords do not match"

            # Check if user already exists
            existing_user = self.auth_manager.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists"

            # Create the user
            user = self.auth_manager.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            # Generate an API key for the user
            api_key = self.auth_manager.create_api_key(
                user_id=user["id"],
                key_name="Default API Key",
            )

            # Set the current user
            self.current_user = user
            self.api_keys = [api_key]

            # Create a client with the user's credentials
            self.client = Client(
                base_url=self.config.get("api", {}).get(
                    "base_url", "http://localhost:8000"
                ),
                api_key=api_key["key"],
            )

            return True, f"Registration successful! Your API key: {api_key['key']}"
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"

    def generate_key(self, key_name: str) -> Tuple[bool, str]:
        """
        Generate a new API key for the current user.

        Args:
            key_name: Name for the new API key

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.current_user:
                return False, "You must be logged in to generate an API key"

            if not key_name:
                return False, "Key name is required"

            # Generate the API key
            if self.current_user.get("is_admin", False):
                # Admin can generate keys for any user
                user_id = gr.Dropdown(
                    label="User", choices=self.auth_manager.get_all_users()
                )
                api_key = self.auth_manager.create_api_key(
                    user_id=user_id,
                    key_name=key_name,
                )
            else:
                # Regular user can only generate keys for themselves
                api_key = self.auth_manager.create_api_key(
                    user_id=self.current_user["id"],
                    key_name=key_name,
                )

            # Add the new key to the list
            self.api_keys.append(api_key)

            return True, f"API key generated: {api_key['key']}"
        except Exception as e:
            logger.error(f"API key generation error: {e}")
            return False, f"API key generation failed: {str(e)}"

    def test_model(
        self,
        provider: str,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: str = None,
    ) -> str:
        """
        Test a model with the given parameters.

        Args:
            provider: Provider name
            model: Model name
            prompt: Prompt text
            temperature: Temperature parameter
            max_tokens: Maximum number of tokens to generate
            api_key: Optional API key to use

        Returns:
            Model response
        """
        try:
            if not self.client and not api_key:
                return "You must be logged in or provide an API key to test a model"

            # Create a temporary client if an API key is provided
            client = self.client
            if api_key:
                client = Client(
                    base_url=self.config.get("api", {}).get(
                        "base_url", "http://localhost:8000"
                    ),
                    api_key=api_key,
                )

            # Call the API
            response = client.completions(
                provider=provider,
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.get("text", "No response")
        except Exception as e:
            logger.error(f"Model test error: {e}")
            return f"Error: {str(e)}"

    def run(self, host: str = "0.0.0.0", port: int = 7860, share: bool = False):
        """
        Run the dashboard.

        Args:
            host: Host to bind to
            port: Port to bind to
            share: Whether to create a public URL
        """
        with gr.Blocks(title="IndoxRouter Dashboard") as dashboard:
            gr.Markdown("# IndoxRouter Dashboard")

            with gr.Tabs() as tabs:
                # Login tab
                with gr.TabItem("Login"):
                    with gr.Row():
                        with gr.Column():
                            email_input = gr.Textbox(label="Email")
                            password_input = gr.Textbox(
                                label="Password", type="password"
                            )
                            login_button = gr.Button("Login")
                            login_output = gr.Textbox(label="Status", interactive=False)

                # Registration tab
                with gr.TabItem("Register"):
                    with gr.Row():
                        with gr.Column():
                            reg_email = gr.Textbox(label="Email")
                            reg_password = gr.Textbox(label="Password", type="password")
                            reg_confirm = gr.Textbox(
                                label="Confirm Password", type="password"
                            )
                            reg_first_name = gr.Textbox(label="First Name")
                            reg_last_name = gr.Textbox(label="Last Name")
                            register_button = gr.Button("Register")
                            register_output = gr.Textbox(
                                label="Status", interactive=False
                            )

                # Playground tab
                with gr.TabItem("Playground"):
                    with gr.Row():
                        with gr.Column():
                            playground_api_key = gr.Textbox(
                                label="API Key (optional if logged in)"
                            )
                            provider_dropdown = gr.Dropdown(
                                label="Provider",
                                choices=self.providers,
                                value=self.providers[0] if self.providers else None,
                            )
                            model_dropdown = gr.Dropdown(
                                label="Model",
                                choices=(
                                    self.models.get(self.providers[0], [])
                                    if self.providers
                                    else []
                                ),
                            )
                            temperature_slider = gr.Slider(
                                label="Temperature",
                                minimum=0.0,
                                maximum=1.0,
                                value=0.7,
                                step=0.1,
                            )
                            max_tokens_slider = gr.Slider(
                                label="Max Tokens",
                                minimum=1,
                                maximum=4000,
                                value=1000,
                                step=1,
                            )

                    with gr.Row():
                        with gr.Column():
                            prompt_input = gr.Textbox(
                                label="Prompt",
                                lines=5,
                                placeholder="Enter your prompt here...",
                            )
                            test_button = gr.Button("Test Model")
                            response_output = gr.Textbox(
                                label="Response",
                                lines=10,
                                interactive=False,
                            )

                # API Keys tab
                with gr.TabItem("API Keys"):
                    with gr.Row():
                        with gr.Column():
                            key_name_input = gr.Textbox(label="Key Name")
                            generate_button = gr.Button("Generate API Key")
                            keys_output = gr.Textbox(
                                label="API Keys",
                                lines=5,
                                interactive=False,
                            )

                # Security Checks tab
                with gr.TabItem("Security Checks"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("## Security Checks")
                            check_button = gr.Button("Run Security Checks")
                            security_output = gr.Textbox(
                                label="Results",
                                lines=10,
                                interactive=False,
                            )

                # About tab
                with gr.TabItem("About"):
                    gr.Markdown(
                        """
                        # IndoxRouter
                        
                        IndoxRouter is a unified API for multiple LLM providers.
                        
                        ## Features
                        
                        - Support for multiple LLM providers
                        - User authentication and API key management
                        - Request logging and monitoring
                        - Caching for improved performance
                        
                        ## Version
                        
                        IndoxRouter v1.0.0
                        
                        ## System Information
                        
                        - Python: {python_version}
                        - Platform: {platform}
                        """.format(
                            python_version=sys.version.split()[0],
                            platform=platform.platform(),
                        )
                    )

            # Event handlers
            login_button.click(
                fn=self.login,
                inputs=[email_input, password_input],
                outputs=[login_output],
            )

            register_button.click(
                fn=self.register,
                inputs=[
                    reg_email,
                    reg_password,
                    reg_confirm,
                    reg_first_name,
                    reg_last_name,
                ],
                outputs=[register_output],
            )

            def update_models(provider):
                return gr.Dropdown.update(
                    choices=self.models.get(provider, []),
                    value=(
                        self.models.get(provider, [""])[0]
                        if self.models.get(provider, [])
                        else None
                    ),
                )

            provider_dropdown.change(
                fn=update_models,
                inputs=[provider_dropdown],
                outputs=[model_dropdown],
            )

            test_button.click(
                fn=self.test_model,
                inputs=[
                    provider_dropdown,
                    model_dropdown,
                    prompt_input,
                    temperature_slider,
                    max_tokens_slider,
                    playground_api_key,
                ],
                outputs=[response_output],
            )

            generate_button.click(
                fn=self.generate_key,
                inputs=[key_name_input],
                outputs=[keys_output],
            )

            def run_security_checks():
                checks = [
                    "✅ JWT Secret: "
                    + (
                        "Secure"
                        if len(self.config.get("jwt", {}).get("secret", "")) > 32
                        else "Insecure"
                    ),
                    (
                        "✅ Database Connection: Secure"
                        if self.config.get("database", {}).get("password") != "password"
                        else "❌ Database Connection: Insecure default password"
                    ),
                    (
                        "✅ API Rate Limiting: Enabled"
                        if self.config.get("api", {}).get("rate_limit", 0) > 0
                        else "❌ API Rate Limiting: Disabled"
                    ),
                    (
                        "✅ SSL/TLS: Enabled"
                        if self.config.get("api", {}).get("ssl", False)
                        else "❌ SSL/TLS: Disabled"
                    ),
                ]
                return "\n".join(checks)

            check_button.click(
                fn=run_security_checks,
                inputs=[],
                outputs=[security_output],
            )

        # Launch the dashboard
        dashboard.launch(server_name=host, server_port=port, share=share)


def main():
    """Run the dashboard."""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()

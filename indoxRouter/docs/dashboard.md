# IndoxRouter Dashboard

The IndoxRouter Dashboard is a web-based interface for testing and managing the IndoxRouter application. It provides a user-friendly way to generate API keys, test completions with different providers and models, and check the security of your configuration.

## Running the Dashboard

To run the dashboard, use the following command:

```bash
python indoxRouter/run_dashboard.py
```

This will start the dashboard on port 7860. You can access it by opening a web browser and navigating to `http://localhost:7860`.

### Command Line Options

The dashboard script supports the following command line options:

- `--port`: Port to run the dashboard on (default: 7860)
- `--host`: Host to run the dashboard on (default: 0.0.0.0)
- `--debug`: Run in debug mode

Example:

```bash
python indoxRouter/run_dashboard.py --port 8080 --debug
```

## Dashboard Features

### Authentication

The dashboard requires authentication to access its features. For testing purposes, the default credentials are:

- Username: `admin`
- Password: `admin`

In a production environment, you should implement proper authentication with your database.

### API Key Management

The dashboard allows you to generate and manage API keys for accessing the IndoxRouter API. You can:

- Generate new API keys
- View existing API keys
- Deactivate API keys

API keys are used to authenticate requests to the IndoxRouter API. They are displayed in a masked format for security.

### Testing Completions

The dashboard provides a user-friendly interface for testing completions with different providers and models. You can:

- Select a provider (OpenAI, Anthropic, Google, etc.)
- Select a model for the chosen provider
- Enter a prompt
- Configure parameters like max tokens and temperature
- Generate a completion

The results include the generated text, cost, and token usage.

### Security Check

The dashboard includes a security check feature that analyzes your configuration and provides recommendations for improving security. It checks:

- API key security
- Environment variables
- Database configuration
- Cache configuration
- Provider configuration

## Integration with IndoxRouter

The dashboard integrates with the IndoxRouter application using the following components:

- **Client API**: Uses the IndoxRouter client to generate completions
- **Security Utilities**: Uses the security utilities for API key management
- **Database Manager**: Uses the database manager for user and API key storage
- **Configuration**: Uses the configuration manager for accessing settings

## Screenshots

![Dashboard Login](../assets/dashboard_login.png)

_Login screen for the IndoxRouter Dashboard_

![API Key Management](../assets/dashboard_api_keys.png)

_API Key Management screen_

![Test Completion](../assets/dashboard_test.png)

_Test Completion screen_

## Customization

The dashboard is built using Gradio, which makes it easy to customize. You can modify the `dashboard.py` file to add new features or change the appearance of the dashboard.

## Security Considerations

The dashboard is intended for testing and development purposes. In a production environment, you should:

- Implement proper authentication with your database
- Use HTTPS to encrypt communications
- Restrict access to the dashboard to trusted users
- Regularly rotate API keys

## Troubleshooting

If you encounter issues with the dashboard, check the following:

- Make sure the IndoxRouter application is properly configured
- Check that the required dependencies are installed
- Verify that the database is accessible
- Check the console output for error messages

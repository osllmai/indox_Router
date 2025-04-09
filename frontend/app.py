"""
IndoxRouter Dashboard - Main App

This is the main Streamlit application for the IndoxRouter Dashboard.
It provides a user interface for signing up, purchasing credits, and managing API keys.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import logging

import database
import config
import setup_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dashboard")

# Custom CSS
css = """
<style>
    .main-header {
        color: #5046e4;
        font-size: 42px;
        text-align: center;
        margin-bottom: 0;
    }
    
    .sub-header {
        color: #5046e4;
        margin-bottom: 20px;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    
    .feature-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #eee;
        height: 100%;
        text-align: center;
    }
    
    .api-key {
        background-color: #e9ecef;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        margin: 5px 0;
        word-break: break-all;
    }
    
    .pricing-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #eee;
        text-align: center;
        height: 100%;
    }
    
    .pricing-card.free {
        border-top: 5px solid #28a745;
    }
    
    .pricing-card.basic {
        border-top: 5px solid #007bff;
    }
    
    .pricing-card.premium {
        border-top: 5px solid #6f42c1;
    }
    
    .pricing-card.enterprise {
        border-top: 5px solid #dc3545;
    }
    
    .pricing-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .pricing-price {
        font-size: 36px;
        color: #5046e4;
        margin-bottom: 15px;
    }
    
    .pricing-description {
        margin-bottom: 20px;
    }
    
    .feature-list {
        text-align: left;
        padding-left: 20px;
    }
</style>
"""

# Initialize the app
st.set_page_config(
    page_title="IndoxRouter Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"
if "show_signup_success" not in st.session_state:
    st.session_state.show_signup_success = False
if "show_purchase_success" not in st.session_state:
    st.session_state.show_purchase_success = False
if "api_keys" not in st.session_state:
    st.session_state.api_keys = []

# Initialize database connection
if not hasattr(st.session_state, "db_initialized"):
    # First run database setup to ensure all required columns exist
    setup_success = setup_db.setup_database()
    if not setup_success:
        st.error("Failed to set up the database schema. Please check the logs.")
        
    # Then initialize database connections
    st.session_state.db_initialized = database.init_db()
    if not st.session_state.db_initialized:
        st.error("Failed to connect to the database. Please check your configuration.")


def login_form():
    """Display the login form."""
    st.markdown('<h2 class="sub-header">Login</h2>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log In")

        if submit:
            if username and password:
                user = database.validate_login(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.api_keys = database.get_user_api_keys(user["id"])
                    st.session_state.active_tab = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter username and password.")

    st.markdown("Don't have an account? [Sign up](#signup)")

    if st.button("Switch to Sign Up"):
        st.session_state.active_tab = "signup"
        st.rerun()


def signup_form():
    """Display the signup form."""
    st.markdown('<h2 class="sub-header">Sign Up</h2>', unsafe_allow_html=True)

    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")

        # Default tier is free
        tier = "free"

        # Add terms checkbox
        terms_accepted = st.checkbox("I accept the Terms of Service and Privacy Policy")

        submit = st.form_submit_button("Sign Up")

        if submit:
            if not username or not email or not password:
                st.error("Please fill in all required fields.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            elif not terms_accepted:
                st.error("You must accept the Terms of Service to continue.")
            else:
                # Create the user
                user = database.create_user(username, email, password, tier)
                if user:
                    st.session_state.user = user
                    st.session_state.api_keys = database.get_user_api_keys(user["id"])
                    st.session_state.show_signup_success = True
                    st.session_state.active_tab = "pricing"
                    st.rerun()
                else:
                    st.error(
                        "Failed to create account. Username or email may already be in use."
                    )

    if st.button("Switch to Login"):
        st.session_state.active_tab = "login"
        st.rerun()


def pricing_page():
    """Display the pricing page."""
    st.markdown('<h2 class="sub-header">Choose Your Plan</h2>', unsafe_allow_html=True)

    if st.session_state.show_signup_success:
        st.markdown(
            '<div class="success-message">Account created successfully! Choose a plan to get started.</div>',
            unsafe_allow_html=True,
        )
        st.session_state.show_signup_success = False

    # Display pricing tiers in a grid
    cols = st.columns(4)

    for i, (tier_id, tier) in enumerate(config.PRICING_TIERS.items()):
        with cols[i]:
            st.markdown(
                f"""
                <div class="pricing-card {tier_id}">
                    <div class="pricing-header">{tier["name"]}</div>
                    <div class="pricing-price">${tier["price"]:.2f}</div>
                    <div class="pricing-description">{tier["description"]}</div>
                    <ul class="feature-list">
                        {"".join([f"<li>{feature}</li>" for feature in tier["features"]])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if tier_id != "free" or not st.session_state.user:
                if st.button(f"Choose {tier['name']}", key=f"buy_{tier_id}"):
                    if st.session_state.user:
                        # Process purchase
                        success = database.update_user_tier(
                            st.session_state.user["id"], tier_id
                        )
                        if success:
                            # Add transaction record
                            database.add_transaction(
                                st.session_state.user["id"],
                                tier["credits"],
                                "purchase",
                                f"Purchase of {tier['name']} plan with {tier['credits']} credits",
                            )

                            # Update user info
                            st.session_state.user = database.get_user_by_id(
                                st.session_state.user["id"]
                            )
                            st.session_state.show_purchase_success = True
                            st.session_state.active_tab = "dashboard"
                            st.rerun()
                    else:
                        st.session_state.active_tab = "signup"
                        st.rerun()


def dashboard_page():
    """Display the user dashboard."""
    if not st.session_state.user:
        st.warning("Please log in to access your dashboard.")
        st.session_state.active_tab = "login"
        st.rerun()
        return

    st.markdown(
        f'<h2 class="sub-header">Welcome, {st.session_state.user["username"]}!</h2>',
        unsafe_allow_html=True,
    )

    if st.session_state.show_purchase_success:
        st.markdown(
            '<div class="success-message">Purchase successful! Your credits have been added to your account.</div>',
            unsafe_allow_html=True,
        )
        st.session_state.show_purchase_success = False

    # Account overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Account Information")
        st.markdown(f"**Username:** {st.session_state.user['username']}")
        st.markdown(f"**Email:** {st.session_state.user['email']}")
        st.markdown(
            f"**Account Tier:** {st.session_state.user['account_tier'].capitalize()}"
        )
        st.markdown(f"**Available Credits:** {st.session_state.user['credits']}")
        st.markdown(
            f"**Member Since:** {st.session_state.user['created_at'].strftime('%B %d, %Y')}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### API Keys")

        # Refresh API keys
        st.session_state.api_keys = database.get_user_api_keys(
            st.session_state.user["id"]
        )

        if st.session_state.api_keys:
            for key in st.session_state.api_keys:
                st.markdown(f"**Name:** {key['name']}")
                st.markdown(
                    f'<div class="api-key">{key["api_key"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Created:** {key['created_at'].strftime('%B %d, %Y')}")
                if key["expires_at"]:
                    st.markdown(
                        f"**Expires:** {key['expires_at'].strftime('%B %d, %Y')}"
                    )
                st.markdown("---")
        else:
            st.markdown("No API keys found.")

        if st.button("Generate New API Key"):
            key_name = f"API Key {len(st.session_state.api_keys) + 1}"
            new_key = database.create_api_key(st.session_state.user["id"], key_name)
            if new_key:
                st.session_state.api_keys = database.get_user_api_keys(
                    st.session_state.user["id"]
                )
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Recent transactions
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Recent Transactions")
    transactions = database.get_user_transactions(st.session_state.user["id"])

    if transactions:
        transaction_data = []
        for tx in transactions:
            transaction_item = {
                "Date": tx["created_at"].strftime("%Y-%m-%d %H:%M"),
                "Type": tx["transaction_type"].capitalize(),
                "Amount": f"{tx['amount']} {tx.get('currency', 'USD')}",
                "Status": tx.get("status", "Completed").capitalize(),
                "Description": tx.get("description") or "-",
            }
            # Add transaction_id if it exists
            if "transaction_id" in tx:
                transaction_item["ID"] = tx["transaction_id"]

            transaction_data.append(transaction_item)

        st.dataframe(pd.DataFrame(transaction_data), use_container_width=True)
    else:
        st.info("No transactions found.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Model usage (with graceful error handling)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Model Usage")

    try:
        # Get usage data safely
        usage_data = database.get_model_usage(st.session_state.user["id"])

        if usage_data and len(usage_data) > 0:
            usage_df = pd.DataFrame(usage_data)

            # Create a pie chart for token usage by model
            fig1 = px.pie(
                usage_df,
                values="tokens_total",
                names=usage_df.apply(lambda x: f"{x['provider']}/{x['model']}", axis=1),
                title="Token Usage by Model",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig1.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig1, use_container_width=True)

            # Create a bar chart for requests by model
            fig2 = px.bar(
                usage_df,
                x=usage_df.apply(lambda x: f"{x['provider']}/{x['model']}", axis=1),
                y="requests",
                title="API Requests by Model",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Display usage data in a table
            st.markdown("#### Usage Details")
            st.dataframe(
                usage_df.rename(
                    columns={
                        "provider": "Provider",
                        "model": "Model",
                        "tokens_total": "Total Tokens",
                        "cost": "Cost ($)",
                        "requests": "Requests",
                    }
                ),
                use_container_width=True,
            )
        else:
            st.info(
                "No usage data available yet. Start using your API key to see usage statistics."
            )
    except Exception as e:
        st.warning(f"Could not load usage statistics. Please try again later.")
        st.info(
            "No usage data available yet. Start using your API key to see usage statistics."
        )
        # Log the error but don't show to user
        print(f"Error retrieving usage data: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Buy more credits
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Buy More Credits")
    st.write("Need more credits? Upgrade your plan or purchase additional credits.")

    if st.button("Browse Plans"):
        st.session_state.active_tab = "pricing"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_navigation():
    """Render the navigation menu."""
    st.markdown('<h1 class="main-header">IndoxRouter Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Your gateway to unified Language Model access")
    
    # Create navigation based on user login status
    if st.session_state.user:
        cols = st.columns([1, 1, 1, 1])
        
        with cols[0]:
            if st.button("Dashboard", use_container_width=True):
                st.session_state.active_tab = "dashboard"
                st.rerun()
                
        with cols[1]:
            if st.button("Plans & Pricing", use_container_width=True):
                st.session_state.active_tab = "pricing"
                st.rerun()
                
        with cols[2]:
            if st.button("API Docs", use_container_width=True):
                st.session_state.active_tab = "docs"
                st.rerun()
                
        with cols[3]:
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.api_keys = []
                st.session_state.active_tab = "home"
                st.rerun()
    else:
        cols = st.columns([1, 1, 1, 1])
        
        with cols[0]:
            if st.button("Home", use_container_width=True):
                st.session_state.active_tab = "home"
                st.rerun()
                
        with cols[1]:
            if st.button("Login", use_container_width=True):
                st.session_state.active_tab = "login"
                st.rerun()
                
        with cols[2]:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.active_tab = "signup"
                st.rerun()
                
        with cols[3]:
            if st.button("Plans & Pricing", use_container_width=True):
                st.session_state.active_tab = "pricing"
                st.rerun()
    
    st.markdown("---")


def home_page():
    """Display the home page."""
    st.markdown('<h2 class="sub-header">Welcome to IndoxRouter</h2>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    IndoxRouter is your gateway to accessing multiple AI models through a unified API. 
    Built for developers and organizations, IndoxRouter simplifies integration with various 
    AI providers including OpenAI, Anthropic, Google, and more.
    """)
    
    # Key features in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🔄 Unified API")
        st.markdown("""
        Access multiple AI providers through a single, consistent API.
        Switch between models without changing your code.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Cost Management")
        st.markdown("""
        Track and control your AI spending with detailed usage analytics.
        Pay-as-you-go pricing with no long-term commitments.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🛡️ Enterprise Ready")
        st.markdown("""
        Built with security, reliability, and scalability in mind.
        Self-hosted option available for organizations with strict data policies.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    st.markdown("### Ready to get started?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign Up Now", use_container_width=True, key="home_signup"):
            st.session_state.active_tab = "signup"
            st.rerun()
            
    with col2:
        if st.button("View Pricing", use_container_width=True, key="home_pricing"):
            st.session_state.active_tab = "pricing"
            st.rerun()


def documentation_page():
    """Display the API documentation page."""
    st.markdown('<h2 class="sub-header">API Documentation</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Getting Started
    
    To use the IndoxRouter API, you'll need an API key. You can get one by signing up and 
    generating a key from your dashboard.
    
    ### Base URL
    
    ```
    http://localhost:8000/api/v1
    ```
    
    ### Authentication
    
    All API requests require authentication using your API key. You can pass the API key 
    in the headers:
    
    ```
    Authorization: Bearer YOUR_API_KEY
    ```
    
    ## Endpoints
    
    ### Chat Completions
    
    ```
    POST /chat/completions
    ```
    
    ### Text Completions
    
    ```
    POST /completions
    ```
    
    ### Embeddings
    
    ```
    POST /embeddings
    ```
    
    ### Image Generation
    
    ```
    POST /images/generations
    ```
    
    ## Client Libraries
    
    IndoxRouter provides official client libraries for easy integration:
    
    - Python: `pip install indoxrouter-client`
    - JavaScript: `npm install indoxrouter-client`
    
    ## Example Usage (Python)
    
    ```python
    from indoxrouter_client import IndoxRouter
    
    client = IndoxRouter(api_key="your-api-key")
    
    response = client.chat.completions(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, who are you?"}
        ],
        model="openai/gpt-4o-mini"
    )
    
    print(response.data)
    ```
    """)
    
    # Link back to dashboard
    if st.button("Back to Dashboard"):
        st.session_state.active_tab = "dashboard"
        st.rerun()


def main():
    """Initialize the dashboard application."""
    # Apply custom CSS
    st.markdown(css, unsafe_allow_html=True)

    # Run database setup
    try:
        logger.info("Setting up database...")
        setup_success = setup_db.setup_database()
        if not setup_success:
            st.error("Failed to set up database. Some features may not work correctly.")
            logger.error("Database setup failed")
    except Exception as e:
        logger.error(f"Error running database setup: {e}")
        st.error("Database setup failed. Some features may not work correctly.")

    # Initialize the database
    if not database.init_db():
        st.error("Failed to connect to databases. Some features may not work correctly.")
        logger.error("Database connection failed")

    # Render the navigation
    render_navigation()

    # Render the active tab
    if st.session_state.active_tab == "home":
        home_page()
    elif st.session_state.active_tab == "login":
        login_form()
    elif st.session_state.active_tab == "signup":
        signup_form()
    elif st.session_state.active_tab == "dashboard":
        dashboard_page()
    elif st.session_state.active_tab == "pricing":
        pricing_page()
    elif st.session_state.active_tab == "docs":
        documentation_page()
    else:
        home_page()


if __name__ == "__main__":
    main()

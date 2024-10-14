import logging
import os
from typing import Optional
import warnings
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

load_dotenv()

class Settings:
    """
    Base settings class containing default configuration for the application, 
    including Snowflake connection parameters and logging configuration.
    """
    
    # Snowflake parameters
    ACCOUNT: str = os.getenv("SNOWFLAKE_ACCOUNT", "your_snowflake_account")
    DATABASE: str = os.getenv("SNOWFLAKE_DATABASE", "your_database")
    SCHEMA: str = os.getenv("SNOWFLAKE_SCHEMA", "your_schema")
    ROLE: str = os.getenv("SNOWFLAKE_ROLE", "your_role")
    DATAWAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE", "your_warehouse")

    # Logging configuration
    LOGGING = {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "DEBUG"
            }
        },
        "disable_existing_loggers": True,
    }


def load_user_secrets(username: str, vault_url: str, environment: str) -> Optional[str]:
    """
    Loads user secrets for Snowflake credentials, either from environment variables or from Azure Key Vault.
    
    Args:
        username (str): Snowflake username.
        vault_url (str): Azure Key Vault URL.
        environment (str): Current environment (e.g., 'local', 'prod').
    
    Returns:
        Optional[str]: Snowflake password or None if not found.
    """
    if os.getenv("ENV", "local") == "local" or os.getenv("ENV") != environment:
        return os.getenv("SNOWFLAKE_PASSWORD")
    
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    return secret_client.get_secret(username.replace('_', '')).value


class PRODSettings(Settings):
    """
    Production settings class that loads secrets from Azure Key Vault or environment variables.
    """
    
    SNOWFLAKE_USER: Optional[str] = os.getenv("SNOWFLAKE_USER")
    VAULT_KEY_URL: str = os.getenv("VAULT_KEY_URL", "your_vault_key_url")
    SNOWFLAKE_PASSWORD: Optional[str] = load_user_secrets(SNOWFLAKE_USER, VAULT_KEY_URL, "prod")

    warnings.filterwarnings("ignore")


# Instantiate the settings object
settings = PRODSettings()

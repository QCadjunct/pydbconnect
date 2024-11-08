# Description: This module provides a class for managing secure storage and retrieval of database credentials.
from typing import Dict, Any, Optional
import os
from pathlib import Path
import json
import keyring
from getpass import getpass
from ..types.exceptions import CredentialError
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages secure storage and retrieval of database credentials"""
    
    def __init__(
        self,
        service_name: str = "pydatabaseconnection",
        env_file: Optional[str] = None
    ):
        self.service_name = service_name
        self._credentials: Dict[str, str] = {}
        self._env_file = env_file
        self._load_environment()

    def _load_environment(self) -> None:
        """Load environment variables from .env file if specified"""
        if self._env_file:
            env_path = Path(self._env_file)
            if env_path.exists():
                load_dotenv(env_path)

    def set_credentials(
        self,
        username: str,
        password: str,
        engine: Optional[str] = None
    ) -> None:
        """
        Set credentials for database engine.
        
        Args:
            username: Database username
            password: Database password
            engine: Optional database engine name
        
        Raises:
            CredentialError: If credentials are invalid
        """
        if not username or not password:
            raise CredentialError("Username and password are required")
            
        keyring_key = f"{self.service_name}_{engine}" if engine else self.service_name
        
        try:
            keyring.set_password(keyring_key, username, password)
            self._credentials = {"username": username, "password": password}
        except Exception as e:
            raise CredentialError(f"Failed to store credentials: {str(e)}")

    def get_credentials(
        self,
        engine: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get stored credentials for database engine.
        
        Args:
            engine: Optional database engine name
        
        Returns:
            Dictionary containing username and password
            
        Raises:
            CredentialError: If credentials not found
        """
        keyring_key = f"{self.service_name}_{engine}" if engine else self.service_name
        
        if self._credentials:
            return self._credentials.copy()
            
        # Try environment variables first
        username = os.getenv(f"{engine}_USERNAME" if engine else "DB_USERNAME")
        password = os.getenv(f"{engine}_PASSWORD" if engine else "DB_PASSWORD")
        
        if username and password:
            self._credentials = {"username": username, "password": password}
            return self._credentials.copy()
            
        # Try keyring
        try:
            stored_creds = keyring.get_credential(keyring_key, None)
            if stored_creds:
                self._credentials = {
                    "username": stored_creds.username,
                    "password": stored_creds.password
                }
                return self._credentials.copy()
        except Exception as e:
            logger.warning(f"Failed to retrieve credentials from keyring: {e}")
            
        raise CredentialError("No credentials found")

    def prompt_credentials(
        self,
        engine: Optional[str] = None,
        store: bool = True
    ) -> Dict[str, str]:
        """
        Prompt user for credentials.
        
        Args:
            engine: Optional database engine name
            store: Whether to store entered credentials
            
        Returns:
            Dictionary containing username and password
        """
        print(f"Enter credentials for {engine if engine else 'database'}:")
        username = input("Username: ")
        password = getpass("Password: ")
        
        if store:
            self.set_credentials(username, password, engine)
            
        return {"username": username, "password": password}

    def clear_credentials(self, engine: Optional[str] = None) -> None:
        """
        Clear stored credentials.
        
        Args:
            engine: Optional database engine name
        """
        keyring_key = f"{self.service_name}_{engine}" if engine else self.service_name
        
        try:
            if self._credentials:
                username = self._credentials["username"]
                keyring.delete_password(keyring_key, username)
        except Exception as e:
            logger.warning(f"Failed to clear credentials from keyring: {e}")
            
        self._credentials = {}

    def load_from_env(self, engine: str) -> Dict[str, str]:
        """
        Load credentials from environment variables.
        
        Args:
            engine: Database engine name
            
        Returns:
            Dictionary containing username and password
            
        Raises:
            CredentialError: If credentials not found in environment
        """
        username = os.getenv(f"{engine}_USERNAME")
        password = os.getenv(f"{engine}_PASSWORD")
        
        if not username or not password:
            raise CredentialError(
                f"Missing environment variables: {engine}_USERNAME and/or {engine}_PASSWORD"
            )
            
        self._credentials = {"username": username, "password": password}
        return self._credentials.copy()

    def validate_credentials(self) -> bool:
        """
        Validate current credentials.
        
        Returns:
            True if credentials are valid
        """
        return bool(
            self._credentials and
            self._credentials.get("username") and
            self._credentials.get("password")
        )

    def rotate_credentials(
        self,
        engine: Optional[str] = None,
        new_password: Optional[str] = None
    ) -> None:
        """
        Rotate database credentials.
        
        Args:
            engine: Optional database engine name
            new_password: Optional new password, will prompt if not provided
        """
        current_creds = self.get_credentials(engine)
        new_pass = new_password or getpass("New password: ")
        
        self.set_credentials(
            current_creds["username"],
            new_pass,
            engine
        )
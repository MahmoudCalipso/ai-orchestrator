"""
OAuth2 Service Hub
Handles provider-specific logic for GitHub, GitLab, Bitbucket, and Google.
"""
import httpx
import os
import secrets
from typing import Dict, Any, Optional, List
from .encryption import encryption_service

class OAuth2Service:
    def __init__(self):
        self.providers = {
            "github": {
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_url": "https://api.github.com/user",
                "scopes": ["user:email", "repo"]
            },
            "gitlab": {
                "client_id": os.getenv("GITLAB_CLIENT_ID"),
                "client_secret": os.getenv("GITLAB_CLIENT_SECRET"),
                "auth_url": "https://gitlab.com/oauth/authorize",
                "token_url": "https://gitlab.com/oauth/token",
                "user_url": "https://gitlab.com/api/v4/user",
                "scopes": ["read_user", "api"]
            },
            "bitbucket": {
                "client_id": os.getenv("BITBUCKET_CLIENT_ID"),
                "client_secret": os.getenv("BITBUCKET_CLIENT_SECRET"),
                "auth_url": "https://bitbucket.org/site/oauth2/authorize",
                "token_url": "https://bitbucket.org/site/oauth2/access_token",
                "user_url": "https://api.bitbucket.org/2.0/user",
                "scopes": ["account", "repository"]
            },
            "google": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "scopes": ["openid", "email", "profile"]
            }
        }

    def get_auth_url(self, provider: str, redirect_uri: str, state: str) -> str:
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        config = self.providers[provider]
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "state": state
        }
        
        # Google needs access_type=offline for refresh tokens
        if provider == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        query = "&".join([f"{k}={v}" for k, v in params.items() if v])
        return f"{config['auth_url']}?{query}"

    async def exchange_code(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
            
        config = self.providers[provider]
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(config["token_url"], data=data, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to exchange code: {response.text}")
            return response.json()

    async def get_user_profile(self, provider: str, access_token: str) -> Dict[str, Any]:
        config = self.providers[provider]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(config["user_url"], headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch user profile: {response.text}")
            return response.json()

    def map_profile(self, provider: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize profile data across providers"""
        if provider == "github":
            return {
                "uid": str(profile["id"]),
                "username": profile["login"],
                "email": profile.get("email"),
                "avatar": profile.get("avatar_url")
            }
        elif provider == "google":
            return {
                "uid": profile["sub"],
                "username": profile.get("name"),
                "email": profile.get("email"),
                "avatar": profile.get("picture")
            }
        elif provider == "gitlab":
            return {
                "uid": str(profile["id"]),
                "username": profile["username"],
                "email": profile.get("email"),
                "avatar": profile.get("avatar_url")
            }
        elif provider == "bitbucket":
            return {
                "uid": profile["uuid"],
                "username": profile["username"],
                "email": profile.get("email"),
                "avatar": profile.get("links", {}).get("avatar", {}).get("href")
            }
        
        # Fallback
        return {
            "uid": str(profile.get("id") or profile.get("uuid") or profile.get("sub", "")),
            "username": profile.get("username") or profile.get("login") or profile.get("name"),
            "email": profile.get("email"),
            "avatar": profile.get("avatar_url") or profile.get("avatar") or profile.get("picture")
        }

oauth_service = OAuth2Service()

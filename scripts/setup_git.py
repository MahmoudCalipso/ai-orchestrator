"""
Git Configuration Setup Script
Interactive tool to configure Git credentials securely
"""
import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet
import yaml
import getpass


def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key()


def save_encryption_key(key: bytes, key_file: Path):
    """Save encryption key to file"""
    key_file.write_bytes(key)
    print(f"✓ Encryption key saved to {key_file}")


def load_encryption_key(key_file: Path) -> bytes:
    """Load encryption key from file"""
    if not key_file.exists():
        print(f"⚠ Encryption key not found at {key_file}")
        key = generate_encryption_key()
        save_encryption_key(key, key_file)
        return key
    return key_file.read_bytes()


def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a string value"""
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def test_github_token(token: str) -> bool:
    """Test GitHub token validity"""
    try:
        import requests
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ GitHub token valid for user: {user_data.get('login')}")
            return True
        else:
            print(f"✗ GitHub token invalid: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠ Could not validate GitHub token: {e}")
        return False


def test_gitlab_token(token: str) -> bool:
    """Test GitLab token validity"""
    try:
        import requests
        headers = {"PRIVATE-TOKEN": token}
        response = requests.get("https://gitlab.com/api/v4/user", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ GitLab token valid for user: {user_data.get('username')}")
            return True
        else:
            print(f"✗ GitLab token invalid: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠ Could not validate GitLab token: {e}")
        return False


def update_env_file(env_file: Path, updates: dict):
    """Update .env file with new values"""
    if env_file.exists():
        lines = env_file.read_text().splitlines()
    else:
        lines = []
    
    # Update existing or add new variables
    updated_keys = set()
    for i, line in enumerate(lines):
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in updates:
                lines[i] = f"{key}={updates[key]}"
                updated_keys.add(key)
    
    # Add new variables that weren't found
    for key, value in updates.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}")
    
    env_file.write_text('\n'.join(lines) + '\n')
    print(f"✓ Updated {env_file}")


def main():
    """Main setup function"""
    print("=" * 60)
    print("AI Orchestrator - Git Configuration Setup")
    print("=" * 60)
    print()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    key_file = project_root / ".git_encryption_key"
    git_config_file = project_root / "config" / "git_config.yaml"
    
    # Load or generate encryption key
    print("🔐 Setting up encryption...")
    encryption_key = load_encryption_key(key_file)
    print()
    
    # Collect Git configuration
    env_updates = {}
    
    print("📝 Git User Configuration")
    print("-" * 60)
    git_name = input("Enter your Git user name [AI Orchestrator]: ").strip() or "AI Orchestrator"
    git_email = input("Enter your Git user email [ai-orchestrator@example.com]: ").strip() or "ai-orchestrator@example.com"
    env_updates["GIT_USER_NAME"] = git_name
    env_updates["GIT_USER_EMAIL"] = git_email
    env_updates["GIT_ENCRYPTION_KEY"] = encryption_key.decode()
    print()
    
    # GitHub configuration
    print("🐙 GitHub Configuration")
    print("-" * 60)
    setup_github = input("Configure GitHub? (y/n) [y]: ").strip().lower() or 'y'
    if setup_github == 'y':
        github_token = getpass.getpass("Enter your GitHub Personal Access Token: ").strip()
        github_username = input("Enter your GitHub username: ").strip()
        
        if github_token:
            print("Testing GitHub token...")
            if test_github_token(github_token):
                env_updates["GITHUB_TOKEN"] = github_token
                env_updates["GITHUB_USERNAME"] = github_username
            else:
                print("⚠ GitHub token validation failed, but saving anyway...")
                env_updates["GITHUB_TOKEN"] = github_token
                env_updates["GITHUB_USERNAME"] = github_username
    print()
    
    # GitLab configuration
    print("🦊 GitLab Configuration")
    print("-" * 60)
    setup_gitlab = input("Configure GitLab? (y/n) [n]: ").strip().lower() or 'n'
    if setup_gitlab == 'y':
        gitlab_token = getpass.getpass("Enter your GitLab Personal Access Token: ").strip()
        gitlab_username = input("Enter your GitLab username: ").strip()
        
        if gitlab_token:
            print("Testing GitLab token...")
            if test_gitlab_token(gitlab_token):
                env_updates["GITLAB_TOKEN"] = gitlab_token
                env_updates["GITLAB_USERNAME"] = gitlab_username
            else:
                print("⚠ GitLab token validation failed, but saving anyway...")
                env_updates["GITLAB_TOKEN"] = gitlab_token
                env_updates["GITLAB_USERNAME"] = gitlab_username
    print()
    
    # Bitbucket configuration
    print("🪣 Bitbucket Configuration")
    print("-" * 60)
    setup_bitbucket = input("Configure Bitbucket? (y/n) [n]: ").strip().lower() or 'n'
    if setup_bitbucket == 'y':
        bitbucket_token = getpass.getpass("Enter your Bitbucket App Password: ").strip()
        bitbucket_username = input("Enter your Bitbucket username: ").strip()
        
        if bitbucket_token:
            env_updates["BITBUCKET_TOKEN"] = bitbucket_token
            env_updates["BITBUCKET_USERNAME"] = bitbucket_username
    print()
    
    # Save configuration
    print("💾 Saving configuration...")
    print("-" * 60)
    update_env_file(env_file, env_updates)
    
    print()
    print("=" * 60)
    print("✅ Git configuration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review your .env file to ensure all values are correct")
    print("2. Never commit .env or .git_encryption_key to version control")
    print("3. Test your Git integration with: python -m scripts.test_git")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

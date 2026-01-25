"""
SMTP Configuration Setup Script
Interactive or CLI-based tool to configure SMTP credentials securely
"""
import os
import sys
import argparse
from pathlib import Path
import getpass
from dotenv import load_dotenv

# Load .env file
load_dotenv()

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
    print(f"Updated {env_file}")

def main():
    parser = argparse.ArgumentParser(description="AI Orchestrator - SMTP Configuration Setup")
    parser.add_argument("--host", help="SMTP Host (e.g., smtp.gmail.com)")
    parser.add_argument("--port", help="SMTP Port (e.g., 587)")
    parser.add_argument("--user", help="SMTP Username (email)")
    parser.add_argument("--password", help="SMTP App Password")
    parser.add_argument("--from-email", help="From Email Address")
    parser.add_argument("--non-interactive", action="store_true", help="Run without asking for input")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AI Orchestrator - SMTP Configuration Setup")
    print("=" * 60)
    print()
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    env_updates = {}
    
    if args.non_interactive:
        env_updates["SMTP_HOST"] = args.host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        env_updates["SMTP_PORT"] = args.port or os.getenv("SMTP_PORT", "587")
        env_updates["SMTP_USERNAME"] = args.user or os.getenv("SMTP_USERNAME", "")
        env_updates["SMTP_PASSWORD"] = args.password or os.getenv("SMTP_PASSWORD", "")
        env_updates["FROM_EMAIL"] = args.from_email or os.getenv("FROM_EMAIL", env_updates.get("SMTP_USERNAME", "noreply@ai-orchestrator.com"))
    else:
        print("SMTP Server Configuration")
        print("-" * 60)
        current_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        env_updates["SMTP_HOST"] = args.host or input(f"Enter SMTP Host [{current_host}]: ").strip() or current_host
        
        current_port = os.getenv("SMTP_PORT", "587")
        env_updates["SMTP_PORT"] = args.port or input(f"Enter SMTP Port [{current_port}]: ").strip() or current_port
        print()
        
        print("SMTP Credentials")
        print("-" * 60)
        current_user = os.getenv("SMTP_USERNAME", "")
        env_updates["SMTP_USERNAME"] = args.user or input(f"Enter SMTP Username (email) [{current_user}]: ").strip() or current_user
        
        env_updates["SMTP_PASSWORD"] = args.password or getpass.getpass("Enter SMTP App Password: ").strip() or os.getenv("SMTP_PASSWORD", "")
        
        current_from = os.getenv("FROM_EMAIL", env_updates['SMTP_USERNAME'])
        env_updates["FROM_EMAIL"] = args.from_email or input(f"Enter From Email [{current_from}]: ").strip() or current_from
        print()

    # Save configuration
    print("Saving SMTP configuration...")
    print("-" * 60)
    update_env_file(env_file, env_updates)
    
    print()
    print("=" * 60)
    print("SMTP configuration completed successfully!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed: {e}")
        sys.exit(1)

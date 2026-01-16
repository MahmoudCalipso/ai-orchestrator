"""
Generate Security Keys for AI Orchestrator
Run this script to generate JWT secret and encryption keys
"""

import secrets
from cryptography.fernet import Fernet

def main():
    print("=" * 70)
    print("AI Orchestrator - Security Keys Generator")
    print("=" * 70)
    print()
    
    # JWT Secret Key
    jwt_secret = secrets.token_urlsafe(32)
    print("🔐 JWT Secret Key (for token signing):")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    
    # Master Encryption Key
    encryption_key = Fernet.generate_key().decode()
    print("🔐 Master Encryption Key (for data encryption):")
    print(f"MASTER_ENCRYPTION_KEY={encryption_key}")
    print()
    
    # API Key Example
    api_key_example = f"aio_{secrets.token_urlsafe(32)}"
    print("🔑 Example API Key Format:")
    print(f"   {api_key_example}")
    print()
    
    print("=" * 70)
    print("⚠️  IMPORTANT:")
    print("1. Copy these values to your .env file")
    print("2. NEVER commit these keys to version control")
    print("3. Use different keys for development and production")
    print("4. Rotate keys regularly for security")
    print("=" * 70)
    print()
    
    # Save to file option
    save = input("Save to .env file? (y/n): ").lower()
    if save == 'y':
        try:
            with open('.env', 'a') as f:
                f.write(f"\n# Generated Security Keys - {secrets.token_hex(4)}\n")
                f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
                f.write(f"MASTER_ENCRYPTION_KEY={encryption_key}\n")
            print("✅ Keys appended to .env file")
        except Exception as e:
            print(f"❌ Error saving to .env: {e}")
            print("Please copy the keys manually")

if __name__ == "__main__":
    main()

# Git Configuration Guide

## 🔐 Setting Up Git Credentials

The AI Orchestrator supports multiple Git providers:
- **GitHub**
- **GitLab**
- **Bitbucket**
- **Azure DevOps**

---

## 📝 Configuration File

**Location:** `config/git_config.yaml`

This file contains all Git provider configurations. You can edit it directly or use the API endpoints.

---

## 🔑 Method 1: Environment Variables (Recommended)

Set credentials via environment variables for better security:

### GitHub
```powershell
$env:GITHUB_TOKEN='ghp_your_github_token_here'
```

### GitLab
```powershell
$env:GITLAB_TOKEN='glpat_your_gitlab_token_here'
```

### Bitbucket
```powershell
$env:BITBUCKET_APP_PASSWORD='your_app_password_here'
```

### Azure DevOps
```powershell
$env:AZURE_DEVOPS_TOKEN='your_pat_token_here'
```

---

## 🌐 Method 2: API Endpoints

### List All Providers
```bash
GET /git/providers
```

**Response:**
```json
{
  "providers": {
    "github": {
      "enabled": true,
      "configured": true
    },
    "gitlab": {
      "enabled": true,
      "configured": false
    }
  }
}
```

### Set GitHub Credentials
```bash
POST /git/config/github
Content-Type: application/json

{
  "token": "ghp_your_github_token"
}
```

### Set GitLab Credentials
```bash
POST /git/config/gitlab
Content-Type: application/json

{
  "token": "glpat_your_gitlab_token"
}
```

### Set Bitbucket Credentials
```bash
POST /git/config/bitbucket
Content-Type: application/json

{
  "username": "your_username",
  "app_password": "your_app_password"
}
```

### Set Azure DevOps Credentials
```bash
POST /git/config/azure_devops
Content-Type: application/json

{
  "token": "your_pat_token",
  "organization": "your_organization"
}
```

### Validate Credentials
```bash
POST /git/validate/github
```

**Response:**
```json
{
  "valid": true,
  "provider": "github",
  "message": "Credentials are valid"
}
```

### Get Provider Configuration
```bash
GET /git/config/github
```

**Response:**
```json
{
  "provider": "github",
  "configured": true,
  "config": {
    "type": "token",
    "api_url": "https://api.github.com"
  }
}
```

### Delete Credentials
```bash
DELETE /git/config/github
```

---

## 🔐 How to Get Tokens

### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Click "Generate token"
5. Copy the token (starts with `ghp_`)

### GitLab Personal Access Token
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Enter token name and expiration
3. Select scopes:
   - `api` (Access the authenticated user's API)
   - `read_repository` (Read access to repositories)
   - `write_repository` (Write access to repositories)
4. Click "Create personal access token"
5. Copy the token (starts with `glpat-`)

### Bitbucket App Password
1. Go to https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Enter label and select permissions:
   - `Repositories: Read, Write`
   - `Pull requests: Read, Write`
4. Click "Create"
5. Copy the app password

### Azure DevOps Personal Access Token
1. Go to https://dev.azure.com/{your-organization}/_usersSettings/tokens
2. Click "New Token"
3. Enter name and expiration
4. Select scopes:
   - `Code: Read & Write`
   - `Build: Read & Execute`
5. Click "Create"
6. Copy the token

---

## 🔒 Security Features

### Encryption
All sensitive credentials are encrypted using Fernet encryption before storage.

**Set encryption key:**
```powershell
$env:GIT_ENCRYPTION_KEY='your-secret-encryption-key-here'
```

### Credential Storage
Credentials can be stored in:
- **Encrypted file** (default)
- **Database** (PostgreSQL)
- **External vault** (HashiCorp Vault)

Configure in `config/git_config.yaml`:
```yaml
security:
  encrypt_credentials: true
  credential_storage: "encrypted_file"
  encryption_key_env: "GIT_ENCRYPTION_KEY"
```

---

## 📋 Complete Example

### PowerShell Script
```powershell
# Set environment variables
$env:GITHUB_TOKEN='ghp_xxxxx'
$env:GITLAB_TOKEN='glpat_xxxxx'
$env:GIT_ENCRYPTION_KEY='my-secret-key'

# Start AI Orchestrator
.\start.ps1

# Test Git configuration
curl -X GET http://localhost:8080/git/providers `
  -H "X-API-Key: dev-key-12345"

# Set GitHub credentials via API
curl -X POST http://localhost:8080/git/config/github `
  -H "X-API-Key: dev-key-12345" `
  -H "Content-Type: application/json" `
  -d '{"token": "ghp_xxxxx"}'

# Validate credentials
curl -X POST http://localhost:8080/git/validate/github `
  -H "X-API-Key: dev-key-12345"
```

---

## 🎯 Usage in AI Orchestrator

Once Git credentials are configured, you can:

1. **Clone repositories** for analysis
2. **Create branches** for migrations
3. **Commit changes** automatically
4. **Create pull requests** with migrated code
5. **Push updates** to remote repositories

---

## ⚠️ Important Notes

1. **Never commit tokens** to version control
2. **Use environment variables** for production
3. **Rotate tokens regularly** (every 90 days)
4. **Use minimal scopes** required for your use case
5. **Enable encryption** for stored credentials

---

## 🔧 Troubleshooting

### Credentials not working?
```bash
# Validate credentials
POST /git/validate/github

# Check provider status
GET /git/providers

# View configuration (tokens hidden)
GET /git/config/github
```

### Reset credentials
```bash
# Delete and re-add
DELETE /git/config/github
POST /git/config/github
```

---

## 📚 API Reference

All Git configuration endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/git/providers` | GET | List all providers |
| `/git/config/{provider}` | GET | Get provider config |
| `/git/config/{provider}` | POST | Set credentials |
| `/git/config/{provider}` | DELETE | Delete credentials |
| `/git/validate/{provider}` | POST | Validate credentials |
| `/git/config` | GET | Get general Git config |

**Supported providers:** `github`, `gitlab`, `bitbucket`, `azure_devops`

---

Your Git credentials are now ready for use with the AI Orchestrator! 🚀

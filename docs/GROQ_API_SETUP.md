# Groq API Key Setup

This guide explains how to set up the Groq API key for AI-generated commit messages in PyDevToolkit-MagicCLI.

## What is Groq API?

Groq is used by PyDevToolkit-MagicCLI to automatically generate high-quality, conventional commit messages based on your code changes. The AI analyzes your git diffs and creates meaningful commit messages following best practices.

## Prerequisites

- A Groq account (free tier available)
- Administrative access to set environment variables (for permanent setup)

## Step 1: Get Your Groq API Key

1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account or log in
3. Navigate to the **API Keys** section
4. Click **Create API Key**
5. Copy the generated API key (starts with `gsk_`)

## Step 2: Set the GROQ_API_KEY Environment Variable

### Option A: Set Permanently (Recommended for Windows)

Run this in PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable('GROQ_API_KEY', 'gsk_your_actual_key_here', 'User')
```

**Important:** Restart your terminal or IDE after running this command for the changes to take effect.

### Option B: Set Temporarily (Current Session Only)

Run this in PowerShell:

```powershell
$env:GROQ_API_KEY = "gsk_your_actual_key_here"
```

**Note:** This setting will be lost when you close the terminal.

### Option C: Set via .env File (Project-Specific)

1. Create a `.env` file in your project root directory
2. Add the following line:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

3. Ensure your application loads environment variables from `.env` files

## Step 3: Verify Your Setup

To verify that your API key is set correctly, run:

```powershell
# Check if the environment variable is set
$env:GROQ_API_KEY
```

You should see your API key displayed.

## Troubleshooting

### Error: "Failed to generate AI commit message"

This error occurs when the `GROQ_API_KEY` environment variable is not set or is invalid.

**Solutions:**
1. Verify the API key is set: `$env:GROQ_API_KEY`
2. Ensure the key starts with `gsk_`
3. Restart your terminal/IDE after setting the variable
4. Check that your API key is still valid in the Groq console

### Error: "Authentication failed" or "401 Unauthorized"

This error means your API key is invalid or expired.

**Solutions:**
1. Verify your API key in the Groq console
2. Generate a new API key if needed
3. Update the environment variable with the new key

### Error: "Rate limit exceeded"

The free tier has rate limits on API calls.

**Solutions:**
1. Wait a few minutes and try again
2. Consider upgrading to a paid Groq plan for higher limits
3. Reduce the frequency of commit operations

## Security Best Practices

- **Never commit your API key** to version control (add `.env` to `.gitignore`)
- **Keep your API key secret** - don't share it publicly
- **Rotate your API keys** periodically for better security
- **Use environment variables** instead of hardcoding keys in code

## How It Works

When you use the git push functionality:

1. PyDevToolkit-MagicCLI analyzes your staged changes
2. The code diffs are sent to Groq's API
3. Groq's AI models generate a conventional commit message
4. The message is validated and applied to your commit

## Supported Models

The tool automatically tries these Groq models in order:

1. `llama-3.3-70b-versatile` (primary)
2. `llama-3.1-70b-versatile` (fallback)
3. `mixtral-8x7b-32768` (fallback)
4. `llama-3.1-8b-instant` (fallback)

If one model fails, the tool automatically tries the next one.

## Additional Resources

- [Groq API Documentation](https://console.groq.com/docs)
- [Groq Console](https://console.groq.com/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
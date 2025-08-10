# N8N LLM Workflow Bulk Updater

With the rapid pace of AI evolution, new language models are being released at an unprecedented rate. A common challenge for automation enthusiasts and businesses is: what happens when you have a large number of workflows or automations configured with one model, and you want to update them to use its successor?

This script was created to solve exactly that problem. When OpenAI recently released GPT-5 Mini, I found myself needing to update dozens of N8N workflows that were still using GPT-4.1 Mini. Rather than manually editing each workflow, this Python script programmatically updates model references by interacting directly with the N8N API.

The script performs bulk updates across all your N8N workflows, automatically finding and replacing old OpenRouter model IDs with newer ones - saving hours of manual work and ensuring consistency across your automation infrastructure.

## Features

- **Bulk Model Updates**: Updates multiple OpenRouter model IDs across all workflows
- **Dry Run Mode**: Preview changes before applying (default)
- **Cloudflare Support**: Works with N8N instances behind Cloudflare Access
- **Rich Console Output**: Beautiful progress tracking and reporting
- **Safe Operations**: Confirmation prompts and error handling

## Model Replacement

Replaces these OpenRouter model IDs:
- `openai/gpt-3.5-turbo`
- `openai/gpt-4o-mini`
- `openai/gpt-4.1-mini`
- `openai/gpt-4.1-nano`

With: `openai/gpt-5-mini`

## Quick Start

1. Clone and install:
```bash
git clone <repo-url>
cd N8N-LLM-Workflow-Bulk-Updater
pip install -r requirements.txt
```

2. Configure `.env`:
```bash
cp .env.example .env
# Edit .env with your N8N details
```

3. Run (dry run first):
```bash
python bulk_updater.py          # Preview changes
python bulk_updater.py --live   # Apply changes
```

## Configuration

### Environment Variables

Create a `.env` file with the following required variables:

```env
# N8N API Configuration
N8N_API_KEY=your_n8n_api_key_here
N8N_BASE_URL=your_n8n_instance_url_here

# Cloudflare Access Headers (if using Cloudflare authentication)
CF_ACCESS_CLIENT_ID=your_cf_client_id_here
CF_ACCESS_CLIENT_SECRET=your_cf_client_secret_here

# Model Configuration
NEW_MODEL_ID=openai/gpt-5-mini
```

### Getting Your N8N API Key

1. Log into your N8N instance
2. Go to **Settings** → **Personal** → **API Keys**
3. Click **Create API Key**
4. Copy the generated key to your `.env` file

**Note**: N8N uses a custom header format `X-N8N-API-KEY` (not standard Bearer tokens).

## Usage Examples

### Preview Changes (Dry Run)
```bash
python bulk_updater.py
```

**Sample Output:**
```
🚀 Starting bulk update: openai/gpt-3.5-turbo, openai/gpt-4o-mini, openai/gpt-4.1-mini, openai/gpt-4.1-nano → openai/gpt-5-mini
📍 Target instance: https://n8n.example.com
✅ Successfully connected to N8N API
📋 Found 86 workflows

                 Workflows to Update                  
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Name         ┃ ID           ┃ Active ┃ Models Found┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━┩
│ My Workflow  │ abc123...    │ Yes    │ openai/gpt… │
└──────────────┴──────────────┴────────┴─────────────┘

📊 Found 1 workflows to update
🔍 DRY RUN COMPLETE - Use --live to apply changes
```

### Apply Changes
```bash
python bulk_updater.py --live
```

### Override Target Model
```bash
python bulk_updater.py --new-model "openai/gpt-4o" --live
```

## How It Works

1. **Connects** to your N8N instance using the API key
2. **Fetches** all workflows from your instance
3. **Scans** each workflow for old OpenRouter model IDs
4. **Replaces** found model IDs with the new target model
5. **Updates** workflows back to N8N with minimal required fields

The script performs a simple find-and-replace operation on the workflow JSON, ensuring all references to old models are updated to the new one.

## Troubleshooting

### 401 Unauthorized Error
- **Cause**: Invalid or missing N8N API key
- **Solution**: 
  1. Verify your API key is correct in `.env`
  2. Ensure the API key hasn't expired
  3. Check that you have proper permissions in N8N

### Connection Issues
- **Cause**: Network connectivity or Cloudflare configuration
- **Solution**:
  1. Test your N8N instance URL in a browser
  2. If using Cloudflare Access, verify your client ID and secret
  3. Check if your N8N instance is accessible from your current network

### 400 Bad Request Error
- **Cause**: Invalid workflow data or API payload
- **Solution**: This is usually handled automatically by the script's payload formatting

### No Workflows Found
- **Cause**: No workflows contain the target model IDs
- **Solution**: This is normal if you've already updated all workflows or don't use the specified models

## Security Notes

- **API Keys**: Never commit your `.env` file to version control
- **Cloudflare Headers**: Keep CF access credentials secure
- **Private Directory**: The `private/` folder is gitignored for additional secrets

## File Structure

```
N8N-LLM-Workflow-Bulk-Updater/
├── bulk_updater.py          # Main script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .env                    # Your secrets (gitignored)
├── .gitignore             # Git ignore rules
├── model-replacement.md    # Model mapping documentation
├── README.md              # This file
└── private/               # Private files (gitignored)
    └── secrets/
        └── secrets.txt
```

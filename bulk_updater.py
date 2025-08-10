#!/usr/bin/env python3
"""
N8N LLM Workflow Bulk Updater

This script connects to an N8N instance and bulk updates LLM model references
across all workflows. Specifically designed to update OpenRouter model IDs
from older versions to newer ones (e.g., GPT-4.1 mini to GPT-5.1 mini).
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.prompt import Confirm

# Load environment variables
load_dotenv()

console = Console()

class N8NWorkflowUpdater:
    def __init__(self):
        self.api_key = os.getenv('N8N_API_KEY')
        self.base_url = os.getenv('N8N_BASE_URL')
        self.cf_client_id = os.getenv('CF_ACCESS_CLIENT_ID')
        self.cf_client_secret = os.getenv('CF_ACCESS_CLIENT_SECRET')
        
        # Model configuration - multiple models to replace
        self.models_to_replace = [
            'openai/gpt-3.5-turbo',
            'openai/gpt-4o-mini',
            'openai/gpt-4.1-mini',
            'openai/gpt-4.1-nano'
        ]
        self.new_model_id = os.getenv('NEW_MODEL_ID', 'openai/gpt-5-mini')
        
        if not self.api_key or not self.base_url:
            raise ValueError("N8N_API_KEY and N8N_BASE_URL must be set in .env file")
        
        # Ensure base URL has proper format
        if not self.base_url.startswith('http'):
            self.base_url = f"https://{self.base_url}"
        if not self.base_url.endswith('/api/v1'):
            self.base_url = f"{self.base_url.rstrip('/')}/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests including Cloudflare access if configured."""
        headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Add Cloudflare headers if configured
        if self.cf_client_id and self.cf_client_secret:
            headers.update({
                'CF-Access-Client-Id': self.cf_client_id,
                'CF-Access-Client-Secret': self.cf_client_secret
            })
        
        return headers
    
    def test_connection(self) -> bool:
        """Test connection to N8N API."""
        try:
            response = requests.get(
                f"{self.base_url}/workflows",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            console.print("✅ Successfully connected to N8N API", style="green")
            return True
        except requests.exceptions.RequestException as e:
            console.print(f"❌ Failed to connect to N8N API: {e}", style="red")
            return False
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Fetch all workflows from N8N."""
        try:
            response = requests.get(
                f"{self.base_url}/workflows",
                headers=self._get_headers()
            )
            response.raise_for_status()
            workflows = response.json().get('data', [])
            console.print(f"📋 Found {len(workflows)} workflows", style="blue")
            return workflows
        except requests.exceptions.RequestException as e:
            console.print(f"❌ Failed to fetch workflows: {e}", style="red")
            return []
    
    def workflow_contains_model(self, workflow: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Check if workflow contains any of the old model IDs."""
        workflow_json = json.dumps(workflow)
        found_models = []
        for model_id in self.models_to_replace:
            if model_id in workflow_json:
                found_models.append(model_id)
        return len(found_models) > 0, found_models
    
    def update_workflow_model(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Update model references in a workflow."""
        # Convert to JSON string, replace all old models with new model, and convert back
        workflow_json = json.dumps(workflow)
        updated_json = workflow_json
        
        for old_model_id in self.models_to_replace:
            updated_json = updated_json.replace(old_model_id, self.new_model_id)
        
        return json.loads(updated_json)
    
    def save_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Save updated workflow back to N8N."""
        try:
            workflow_id = workflow.get('id')
            if not workflow_id:
                console.print("❌ Workflow missing ID", style="red")
                return False
            
            # Create payload with required fields for N8N API
            update_payload = {
                'name': workflow.get('name'),
                'nodes': workflow.get('nodes'),
                'connections': workflow.get('connections'),
                'settings': workflow.get('settings', {})  # Required field
            }
            
            response = requests.put(
                f"{self.base_url}/workflows/{workflow_id}",
                headers=self._get_headers(),
                json=update_payload
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            console.print(f"❌ Failed to save workflow {workflow.get('name', 'Unknown')}: {e}", style="red")
            return False
    
    def run_bulk_update(self, dry_run: bool = True) -> None:
        """Run the bulk update process."""
        console.print(f"\n🚀 Starting bulk update: {', '.join(self.models_to_replace)} → {self.new_model_id}")
        console.print(f"📍 Target instance: {self.base_url.replace('/api/v1', '')}")
        
        if dry_run:
            console.print("🔍 Running in DRY RUN mode - no changes will be made", style="yellow")
        
        # Test connection
        if not self.test_connection():
            return
        
        # Get all workflows
        workflows = self.get_all_workflows()
        if not workflows:
            return
        
        # Find workflows that need updating
        workflows_to_update = []
        workflow_model_map = {}
        for workflow in workflows:
            contains_model, found_models = self.workflow_contains_model(workflow)
            if contains_model:
                workflows_to_update.append(workflow)
                workflow_model_map[workflow.get('id')] = found_models
        
        if not workflows_to_update:
            console.print("✅ No workflows found containing the old model ID", style="green")
            return
        
        # Display summary table
        table = Table(title="Workflows to Update")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Active", style="green")
        table.add_column("Models Found", style="yellow")
        
        for workflow in workflows_to_update:
            workflow_id = workflow.get('id')
            found_models = workflow_model_map.get(workflow_id, [])
            table.add_row(
                workflow.get('name', 'Unnamed'),
                str(workflow_id or 'Unknown'),
                "Yes" if workflow.get('active', False) else "No",
                ", ".join(found_models)
            )
        
        console.print(table)
        console.print(f"\n📊 Found {len(workflows_to_update)} workflows to update")
        
        if dry_run:
            console.print("\n🔍 DRY RUN COMPLETE - Use --live to apply changes", style="yellow")
            return
        
        # Confirm before proceeding
        if not Confirm.ask(f"\nProceed with updating {len(workflows_to_update)} workflows?"):
            console.print("❌ Update cancelled", style="red")
            return
        
        # Update workflows
        updated_count = 0
        failed_count = 0
        
        with Progress() as progress:
            task = progress.add_task("Updating workflows...", total=len(workflows_to_update))
            
            for workflow in workflows_to_update:
                # Update the workflow
                updated_workflow = self.update_workflow_model(workflow)
                
                # Save the updated workflow
                if self.save_workflow(updated_workflow):
                    updated_count += 1
                    console.print(f"✅ Updated: {workflow.get('name', 'Unknown')}", style="green")
                else:
                    failed_count += 1
                
                progress.update(task, advance=1)
        
        # Summary
        console.print(f"\n📊 Update Summary:")
        console.print(f"✅ Successfully updated: {updated_count}")
        console.print(f"❌ Failed to update: {failed_count}")
        
        if updated_count > 0:
            console.print(f"🎉 Bulk update completed! Updated {updated_count} workflows.", style="green")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="N8N LLM Workflow Bulk Updater")
    parser.add_argument(
        '--live', 
        action='store_true', 
        help='Apply changes (default is dry run)'
    )
    parser.add_argument(
        '--new-model',
        help='Override new model ID from .env (default: openai/gpt-5-mini)'
    )
    
    args = parser.parse_args()
    
    try:
        updater = N8NWorkflowUpdater()
        
        # Override new model ID if provided
        if args.new_model:
            updater.new_model_id = args.new_model
        
        # Run the update
        updater.run_bulk_update(dry_run=not args.live)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

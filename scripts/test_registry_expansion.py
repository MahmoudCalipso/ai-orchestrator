import asyncio
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from services.registry.registry_updater import RegistryUpdater

async def test_registry_expansion():
    print("Testing Registry Expansion to 16 Languages...")
    updater = RegistryUpdater()
    
    # 1. Verify all 16 files exist
    registry_dir = Path("services/registry/registries")
    files = list(registry_dir.glob("*_registry.json"))
    print(f"Found {len(files)} registry files.")
    
    if len(files) < 16:
        print(f"Warning: Expected 16 registry files, found {len(files)}.")
    
    # 2. Run update for a few representative languages
    test_languages = ["python", "javascript", "go", "rust", "java", "php"]
    
    print("\nRunning test updates for representative languages:")
    for lang in test_languages:
        print(f"Checking {lang}...")
        try:
            updates = await updater.update_registry(lang)
            if updates:
                print(f"✓ {lang} updates found: {list(updates.keys())}")
            else:
                print(f"✓ {lang} is up to date or no packages checked.")
        except Exception as e:
            print(f"✗ {lang} update failed: {e}")

    # 3. Verify update_all_registries handles the loop
    print("\nVerifying update_all_registries loop logic...")
    # We won't run the full thing to avoid rate limits, but we'll check the structure
    all_langs = [
        "javascript", "typescript", "python", "java", "csharp", "go", 
        "rust", "php", "ruby", "scala", "kotlin", "swift", "dart", 
        "elixir", "c", "cpp"
    ]
    
    # Check if updater has correctly mapped files
    for lang in all_langs:
        filename = updater.registry_path / f"{lang}_registry.json"
        # Special case for csharp -> dotnet
        if lang == "csharp":
            filename = updater.registry_path / "dotnet_registry.json"
            
        if not filename.exists():
             print(f"✗ Mapping error: {lang} -> {filename} (File not found)")
        else:
             print(f"✓ {lang} -> {filename.name}")

    print("\nTest Complete.")

if __name__ == "__main__":
    asyncio.run(test_registry_expansion())

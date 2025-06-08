import os
import shutil
from pathlib import Path

def copy_assets_to_website():
    """Copy necessary assets to the website directory to avoid 404 errors."""
    source_dir = Path('.')
    target_dir = Path('./website')
    
    # Create target directory if it doesn't exist
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
        print(f"Created directory {target_dir}")
    
    # List of assets to copy
    assets = [
        'population_animation.mp4',
        'population_final_frame.png'
    ]
    
    # Copy each asset
    for asset in assets:
        source = source_dir / asset
        target = target_dir / asset
        
        if source.exists():
            shutil.copy2(source, target)
            print(f"Copied: {asset}")
        else:
            print(f"Warning: {asset} not found in source directory")
    
    # Copy flags directory if it exists
    flags_source = source_dir / 'flags'
    flags_target = target_dir / 'flags'
    
    if flags_source.exists() and flags_source.is_dir():
        if flags_target.exists():
            shutil.rmtree(flags_target)
        shutil.copytree(flags_source, flags_target)
        print("Copied: flags directory")
    else:
        print("Warning: flags directory not found")
    
    print("\nAssets copying complete. Run 'quarto preview' to view the site.")

if __name__ == "__main__":
    copy_assets_to_website()

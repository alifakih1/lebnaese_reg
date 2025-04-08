#!/usr/bin/env python3
"""
Fix Installation Script for Lebanese Regulations App

This script fixes the installation issues with the Lebanese Regulations app
by modifying the necessary files to skip asset building.

Usage:
    python fix_installation.py

After running this script, you can install the app using:
    bench --site your-site install-app lebanese_regulations --skip-assets
"""

import os
import sys
import re
from pathlib import Path

def fix_pyproject_toml():
    """Fix the pyproject.toml file to skip asset building"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        return False
    
    content = pyproject_path.read_text()
    
    # Add skip_build_assets = true
    if "[tool.bench]" in content and "skip_build_assets" not in content:
        content = content.replace(
            "[tool.bench]",
            "[tool.bench]\nskip_build_assets = true"
        )
    
    # Remove assets section if it exists
    assets_pattern = re.compile(r'\[tool\.bench\.assets\].*?(\n\[|\Z)', re.DOTALL)
    content = re.sub(assets_pattern, r'\1', content)
    
    pyproject_path.write_text(content)
    print("✅ Fixed pyproject.toml")
    return True

def fix_hooks_py():
    """Comment out all asset references in hooks.py"""
    hooks_path = Path("lebanese_regulations/hooks.py")
    
    if not hooks_path.exists():
        print("Error: hooks.py not found")
        return False
    
    content = hooks_path.read_text()
    
    # Comment out asset references
    patterns = [
        r'(app_include_css\s*=\s*".*")',
        r'(app_include_js\s*=\s*\[.*\])',
        r'(web_include_css\s*=\s*".*")',
        r'(web_include_js\s*=\s*".*")',
        r'(website_theme_scss\s*=\s*".*")',
        r'(webform_include_js\s*=\s*\{.*\})',
        r'(webform_include_css\s*=\s*\{.*\})',
        r'(page_js\s*=\s*\{.*\})',
        r'(doctype_js\s*=\s*\{[\s\S]*?\})',
        r'(doctype_list_js\s*=\s*\{[\s\S]*?\})',
        r'(doctype_tree_js\s*=\s*\{.*\})',
        r'(doctype_calendar_js\s*=\s*\{.*\})',
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, r'# \1', content)
    
    hooks_path.write_text(content)
    print("✅ Fixed hooks.py")
    return True

def create_public_dir():
    """Create empty public directory structure"""
    dirs = [
        "lebanese_regulations/public",
        "lebanese_regulations/public/js",
        "lebanese_regulations/public/css",
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Create empty files to ensure directories are created
    Path("lebanese_regulations/public/js/.gitkeep").touch()
    Path("lebanese_regulations/public/css/.gitkeep").touch()
    
    print("✅ Created public directory structure")
    return True

def update_readme():
    """Update README.md with installation instructions"""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("Error: README.md not found")
        return False
    
    content = readme_path.read_text()
    
    # Update installation instructions
    if "bench --site your-site install-app lebanese_regulations" in content:
        content = content.replace(
            "bench --site your-site install-app lebanese_regulations",
            "bench --site your-site install-app lebanese_regulations --skip-assets"
        )
        
        if "--skip-assets" in content and "Note: The `--skip-assets` flag" not in content:
            install_section = re.search(r'(bench --site your-site install-app lebanese_regulations --skip-assets.*?)(\n\n|\Z)', content, re.DOTALL)
            if install_section:
                replacement = install_section.group(1) + "\n\nNote: The `--skip-assets` flag is important as it skips the asset building process, which may cause errors in some environments."
                content = content.replace(install_section.group(0), replacement + install_section.group(2))
    
    readme_path.write_text(content)
    print("✅ Updated README.md")
    return True

def main():
    """Main function"""
    print("🔧 Fixing Lebanese Regulations App Installation")
    
    success = True
    success = fix_pyproject_toml() and success
    success = fix_hooks_py() and success
    success = create_public_dir() and success
    success = update_readme() and success
    
    if success:
        print("\n✅ All fixes applied successfully!")
        print("\nYou can now install the app using:")
        print("    bench --site your-site install-app lebanese_regulations --skip-assets")
    else:
        print("\n❌ Some fixes could not be applied")
        print("Please check the errors above and fix them manually")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
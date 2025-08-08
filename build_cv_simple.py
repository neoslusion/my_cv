#!/usr/bin/env python3
"""
Simple CV build script that generates HTML from Doxygen and optionally converts to PDF
This version uses browser printing for PDF generation as a fallback
"""

import os
import sys
import subprocess
import shutil
import argparse
import webbrowser
from pathlib import Path

def check_command(command):
    """Check if a command is available in PATH"""
    try:
        subprocess.run([command, '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    parser = argparse.ArgumentParser(description='Build CV from Doxygen source')
    parser.add_argument('--skip-pdf', action='store_true', 
                       help='Skip PDF generation instructions')
    parser.add_argument('--no-open', action='store_true',
                       help='Do not open generated HTML file in browser')
    args = parser.parse_args()
    
    print("🚀 Building CV from Doxygen source...")
    
    # Check dependencies
    if not check_command('doxygen'):
        print("❌ Error: Doxygen not found. Please install Doxygen first.")
        print("📥 Download from: https://www.doxygen.nl/download.html")
        sys.exit(1)
    
    # Get Doxygen version
    try:
        result = subprocess.run(['doxygen', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Found Doxygen version: {result.stdout.strip()}")
    except Exception:
        pass
    
    # Create output directory
    output_dir = Path("docs/generated")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run Doxygen
    print("📝 Generating HTML documentation...")
    result = subprocess.run(['doxygen', 'Doxyfile'])
    if result.returncode != 0:
        print("❌ Error: Doxygen generation failed!")
        sys.exit(1)
    
    # Copy assets
    assets_source = Path("docs/assets")
    assets_target = output_dir / "html" / "assets"
    if assets_source.exists():
        shutil.copytree(assets_source, assets_target, dirs_exist_ok=True)
        print("📂 Copied assets to generated folder")
    
    # Copy favicon
    favicon_source = Path("docs/favicon.ico")
    favicon_target = output_dir / "html" / "favicon.ico"
    if favicon_source.exists():
        shutil.copy2(favicon_source, favicon_target)
        print("🖼️  Copied favicon to generated folder")
    
    # Find generated HTML file
    html_files = list((output_dir / "html").glob("*.html"))
    main_html = None
    
    # Look for the main CV page
    for html_file in html_files:
        if 'cv_main' in html_file.name or 'index' in html_file.name:
            main_html = html_file
            break
    
    if not main_html and html_files:
        main_html = html_files[0]  # Use first HTML file found
    
    if main_html:
        print(f"✅ HTML CV generated successfully!")
        print(f"📄 Location: {main_html}")
    else:
        print("❌ Warning: No HTML files found in output directory")
        sys.exit(1)
    
    # Create a simplified PDF generation message
    if not args.skip_pdf:
        print("📋 PDF Generation Instructions:")
        print("   Since automatic PDF generation requires complex dependencies,")
        print("   you can create a PDF manually by:")
        print("   1. Opening the HTML file in your browser")
        print("   2. Using Ctrl+P (or Cmd+P on Mac) to print")
        print("   3. Selecting 'Save as PDF' as the destination")
        print("   4. Saving to the 'build' folder as 'LePhucDuc_CV.pdf'")
        print()
        
        # Alternative: Use the existing build system if available
        existing_pdf_script = Path("build/get_via_htmltopdf.py")
        if existing_pdf_script.exists():
            print("💡 Alternative: Use the existing PDF generation system:")
            print("   Run the existing build script to generate PDF via web service")
    
    print("✨ Build completed!")
    print(f"🌐 HTML CV: {main_html}")
    
    pdf_path = Path("build/LePhucDuc_CV.pdf")
    if pdf_path.exists():
        print(f"📁 PDF CV: {pdf_path}")
    
    # Open result if requested or if it's the default behavior
    if not args.no_open:  # Open by default unless --no-open is specified
        try:
            # Convert to absolute path and use file:// URL
            abs_path = main_html.resolve()
            file_url = f"file:///{abs_path}".replace('\\', '/')
            webbrowser.open(file_url)
            print(f"🌐 Opened CV in your default browser")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"   Please open this file manually: {main_html}")
    
    print("\n📝 Usage:")
    print("   To rebuild: python build_cv_simple.py")
    print("   To skip opening browser: python build_cv_simple.py --no-open")
    print("   To skip PDF instructions: python build_cv_simple.py --skip-pdf")

if __name__ == "__main__":
    main()

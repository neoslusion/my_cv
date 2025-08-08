#!/usr/bin/env python3
"""
Build script for CV generation from Doxygen source
Supports both HTML and PDF output
"""

import os
import sys
import subprocess
import shutil
import argparse
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

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: {description} failed!")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Build CV from Doxygen source')
    parser.add_argument('--skip-pdf', action='store_true', 
                       help='Skip PDF generation')
    parser.add_argument('--open', action='store_true',
                       help='Open generated HTML file')
    args = parser.parse_args()
    
    print("Building CV from Doxygen source...")
    
    # Check dependencies
    if not check_command('doxygen'):
        print("Error: Doxygen not found. Please install Doxygen first.")
        print("Download from: https://www.doxygen.nl/download.html")
        sys.exit(1)
    
    # Get Doxygen version
    try:
        result = subprocess.run(['doxygen', '--version'], 
                              capture_output=True, text=True)
        print(f"Found Doxygen version: {result.stdout.strip()}")
    except Exception:
        pass
    
    # Create output directory
    output_dir = Path("docs/generated")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run Doxygen
    if not run_command('doxygen Doxyfile', 'Doxygen generation'):
        sys.exit(1)
    
    # Copy assets
    assets_source = Path("docs/assets")
    assets_target = output_dir / "html" / "assets"
    if assets_source.exists():
        shutil.copytree(assets_source, assets_target, dirs_exist_ok=True)
        print("Copied assets to generated folder")
    
    # Copy favicon
    favicon_source = Path("docs/favicon.ico")
    favicon_target = output_dir / "html" / "favicon.ico"
    if favicon_source.exists():
        shutil.copy2(favicon_source, favicon_target)
        print("Copied favicon to generated folder")
    
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
        print(f"HTML CV generated successfully: {main_html}")
    else:
        print("Warning: No HTML files found in output directory")
        sys.exit(1)
    
    # Generate PDF if not skipped
    if not args.skip_pdf:
        print("Generating PDF...")
        
        if not check_command('python'):
            print("Warning: Python not found. Skipping PDF generation.")
        else:
            # Try to install weasyprint
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'weasyprint'], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print("Warning: Could not install weasyprint. Skipping PDF generation.")
            else:
                # Generate PDF
                pdf_script = f'''
import weasyprint
import os
from pathlib import Path

html_file = r"{main_html.absolute()}"
pdf_file = Path("build/LePhucDuc_CV.pdf")

# Create build directory
pdf_file.parent.mkdir(exist_ok=True)

try:
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    css_style = """
    @page {{
        size: A4;
        margin: 1cm;
    }}
    body {{
        font-family: 'Roboto', Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.4;
    }}
    #banner {{
        display: none;
    }}
    .contents {{
        box-shadow: none;
        margin: 0;
        padding: 0;
    }}
    h1 {{ font-size: 18pt; }}
    h2 {{ font-size: 14pt; }}
    h3 {{ font-size: 12pt; }}
    h4 {{ font-size: 11pt; }}
    """
    
    html_doc = weasyprint.HTML(string=html_content, base_url=str(Path(html_file).parent))
    css_doc = weasyprint.CSS(string=css_style)
    
    html_doc.write_pdf(str(pdf_file), stylesheets=[css_doc])
    print(f"PDF generated successfully: {{pdf_file}}")
    
except Exception as e:
    print(f"Error generating PDF: {{e}}")
    exit(1)
'''
                
                # Write and execute PDF generation script
                with open('temp_pdf_gen.py', 'w', encoding='utf-8') as f:
                    f.write(pdf_script)
                
                try:
                    result = subprocess.run([sys.executable, 'temp_pdf_gen.py'])
                    if result.returncode == 0:
                        print("PDF generated successfully!")
                    else:
                        print("Warning: PDF generation failed. HTML version is still available.")
                except Exception as e:
                    print(f"Warning: Could not generate PDF: {e}")
                finally:
                    # Clean up
                    if os.path.exists('temp_pdf_gen.py'):
                        os.remove('temp_pdf_gen.py')
    
    print("\\nBuild completed!")
    print(f"HTML CV: {main_html}")
    
    pdf_path = Path("build/LePhucDuc_CV.pdf")
    if pdf_path.exists():
        print(f"PDF CV: {pdf_path}")
    
    # Open result if requested
    if args.open and main_html:
        if sys.platform == "win32":
            os.startfile(main_html)
        elif sys.platform == "darwin":
            subprocess.run(["open", main_html])
        else:
            subprocess.run(["xdg-open", main_html])
    
    print("\\nTo rebuild, run: python build_cv.py")
    print("To open HTML result: python build_cv.py --open")
    print("To skip PDF generation: python build_cv.py --skip-pdf")

if __name__ == "__main__":
    main()

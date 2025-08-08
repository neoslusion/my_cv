#!/usr/bin/env python3
"""
Doxygen CV to PDF converter for Linux build system
Integrates with existing ngrok and HTML-to-PDF.net infrastructure
"""

import os
import sys
import subprocess
import shutil
import requests
import time
import json
import re
from pathlib import Path

# Import the existing API if available
try:
    sys.path.append('build')
    from api import HtmlToPdfDotNet
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_colored(message, color):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.NC}")

def check_command(command):
    """Check if a command is available"""
    try:
        subprocess.run([command, '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def cleanup_processes():
    """Clean up any running processes"""
    print_colored("🧹 Cleaning up processes...", Colors.YELLOW)
    try:
        subprocess.run(['pkill', '-f', 'python.*http.server'], check=False)
        subprocess.run(['pkill', 'ngrok'], check=False)
    except Exception:
        pass

def start_http_server(directory, port=8000):
    """Start HTTP server for the generated HTML"""
    print_colored(f"🌐 Starting HTTP server on port {port}...", Colors.BLUE)
    
    # Change to the directory and start server
    cmd = f"cd {directory} && python3 -m http.server {port}"
    process = subprocess.Popen(cmd, shell=True, 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    
    # Wait a bit for server to start
    time.sleep(2)
    return process

def start_ngrok_tunnel(port=8000):
    """Start ngrok tunnel and return the public URL"""
    print_colored("🔗 Starting ngrok tunnel...", Colors.BLUE)
    
    # Check if ngrok is available
    if not shutil.which('ngrok') and not os.path.exists('./ngrok'):
        raise Exception("ngrok not found")
    
    # Use local ngrok if available, otherwise system ngrok
    ngrok_cmd = './ngrok' if os.path.exists('./ngrok') else 'ngrok'
    
    process = subprocess.Popen([ngrok_cmd, 'http', str(port)],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    
    # Wait for ngrok to establish tunnel
    print_colored("⏳ Waiting for ngrok tunnel to establish...", Colors.YELLOW)
    time.sleep(5)
    
    # Get tunnel URL
    for attempt in range(10):
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                url = tunnels[0]['public_url']
                print_colored(f"✅ Ngrok tunnel established: {url}", Colors.GREEN)
                return url, process
        except Exception:
            pass
        
        print_colored(f"⏳ Waiting for tunnel... (attempt {attempt + 1}/10)", Colors.YELLOW)
        time.sleep(2)
    
    raise Exception("Could not establish ngrok tunnel")

def generate_pdf_via_service(url, output_file):
    """Generate PDF using the HTML-to-PDF service"""
    print_colored("📄 Generating PDF via web service...", Colors.BLUE)
    
    if API_AVAILABLE:
        # Use existing API
        converter = HtmlToPdfDotNet()
        pdf_content = converter.convert_pdf(url)
    else:
        # Fallback implementation
        pdf_content = simple_html_to_pdf(url)
    
    if pdf_content:
        with open(output_file, 'wb') as f:
            f.write(pdf_content)
        
        file_size = len(pdf_content)
        print_colored(f"✅ PDF generated successfully: {output_file}", Colors.GREEN)
        print_colored(f"📊 PDF size: {file_size:,} bytes", Colors.GREEN)
        return True
    else:
        print_colored("❌ PDF generation failed", Colors.RED)
        return False

def simple_html_to_pdf(url):
    """Simple fallback HTML to PDF conversion"""
    try:
        # This is a simplified version of the conversion
        # In a real scenario, you might want to use a different service
        # or implement a more robust solution
        
        session = requests.Session()
        
        # Get the conversion page
        response = session.get("https://www.html-to-pdf.net/free-online-pdf-converter.aspx")
        
        # Extract required form fields
        view_state_match = re.search(r'id="__VIEWSTATE" value="(.*?)"', response.text)
        event_validation_match = re.search(r'id="__EVENTVALIDATION" value="(.*?)"', response.text)
        
        if not view_state_match or not event_validation_match:
            raise Exception("Could not extract form validation fields")
        
        # Prepare form data
        form_data = {
            "__VIEWSTATE": view_state_match.group(1),
            "__EVENTVALIDATION": event_validation_match.group(1),
            "ctl00$ContentPlaceHolder1$txtUrl": url,
            "ctl00$ContentPlaceHolder1$ddlPageSize": "A4",
            "ctl00$ContentPlaceHolder1$ddlPageOrientation": "Portrait",
            "ctl00$ContentPlaceHolder1$txtWidth": "1024",
            "ctl00$ContentPlaceHolder1$txtConversionDelay": "1",
            "ctl00$ContentPlaceHolder1$btnConvert": "Convert to PDF"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Submit conversion request
        response = session.post(
            "https://www.html-to-pdf.net/free-online-pdf-converter.aspx",
            data=form_data,
            headers=headers
        )
        
        # Check if we got PDF content directly
        if 'application/pdf' in response.headers.get('content-type', ''):
            return response.content
        
        # Try to find download link in response
        download_link_match = re.search(r'href="([^"]*\.pdf[^"]*)"', response.text)
        if download_link_match:
            pdf_url = "https://www.html-to-pdf.net" + download_link_match.group(1)
            pdf_response = session.get(pdf_url)
            if pdf_response.status_code == 200:
                return pdf_response.content
        
        raise Exception("Could not extract PDF from service response")
        
    except Exception as e:
        print_colored(f"Error in PDF conversion: {e}", Colors.RED)
        return None

def main():
    """Main build function"""
    print_colored("🚀 Building CV from Doxygen source (Linux build system)...", Colors.BLUE)
    
    # Configuration
    dox_file = "docs/LePhucDuc_CV.dox"
    html_output_dir = "docs/generated/html"
    pdf_output = "LePhucDuc_CV.pdf"
    http_port = 8000
    
    # Set up cleanup on exit
    import atexit
    atexit.register(cleanup_processes)
    
    try:
        # Check dependencies
        if not check_command('doxygen'):
            print_colored("❌ Error: Doxygen is not installed", Colors.RED)
            print_colored("📥 Install with: sudo apt-get install doxygen", Colors.YELLOW)
            sys.exit(1)
        
        if not os.path.exists(dox_file):
            print_colored(f"❌ Error: CV source file not found: {dox_file}", Colors.RED)
            sys.exit(1)
        
        # Get Doxygen version
        result = subprocess.run(['doxygen', '--version'], 
                               capture_output=True, text=True)
        print_colored(f"✅ Found Doxygen version: {result.stdout.strip()}", Colors.GREEN)
        
        # Clean up existing files
        if os.path.exists(pdf_output):
            os.remove(pdf_output)
            print_colored("🗑️  Removed existing PDF file", Colors.YELLOW)
        
        if os.path.exists("docs/generated"):
            shutil.rmtree("docs/generated")
            print_colored("🗑️  Cleaned previous build output", Colors.YELLOW)
        
        # Generate HTML from Doxygen
        print_colored("📝 Generating HTML documentation from Doxygen...", Colors.BLUE)
        result = subprocess.run(['doxygen', 'Doxyfile'])
        if result.returncode != 0:
            print_colored("❌ Error: Doxygen generation failed", Colors.RED)
            sys.exit(1)
        
        # Copy assets
        if os.path.exists("docs/assets"):
            shutil.copytree("docs/assets", f"{html_output_dir}/assets", dirs_exist_ok=True)
            print_colored("📂 Copied assets to generated folder", Colors.GREEN)
        
        # Copy favicon
        if os.path.exists("docs/favicon.ico"):
            shutil.copy2("docs/favicon.ico", f"{html_output_dir}/favicon.ico")
            print_colored("🖼️  Copied favicon to generated folder", Colors.GREEN)
        
        # Find main HTML file
        html_files = list(Path(html_output_dir).glob("*.html"))
        main_html = None
        
        for html_file in html_files:
            if 'cv_main' in html_file.name or 'index' in html_file.name:
                main_html = html_file
                break
        
        if not main_html and html_files:
            main_html = html_files[0]
        
        if not main_html:
            print_colored("❌ Error: No HTML files generated", Colors.RED)
            sys.exit(1)
        
        print_colored(f"✅ HTML CV generated successfully: {main_html}", Colors.GREEN)
        
        # Create index.html for web server
        index_path = Path(html_output_dir) / "index.html"
        if not index_path.exists():
            shutil.copy2(main_html, index_path)
            print_colored("📋 Created index.html for web server", Colors.GREEN)
        
        # Start HTTP server
        http_process = start_http_server(html_output_dir, http_port)
        
        # Start ngrok tunnel
        try:
            tunnel_url, ngrok_process = start_ngrok_tunnel(http_port)
        except Exception as e:
            print_colored(f"⚠️  Warning: Could not start ngrok tunnel: {e}", Colors.YELLOW)
            print_colored(f"📱 HTML CV available locally at: http://localhost:{http_port}", Colors.YELLOW)
            print_colored("💡 For PDF generation, use browser print (Ctrl+P)", Colors.YELLOW)
            return
        
        # Generate PDF
        if generate_pdf_via_service(tunnel_url, pdf_output):
            # Copy to build directory
            os.makedirs("build", exist_ok=True)
            shutil.copy2(pdf_output, "build/")
            print_colored("📁 PDF copied to build directory", Colors.GREEN)
        
        # Show results
        print_colored("\n✨ Build completed!", Colors.GREEN)
        if os.path.exists(pdf_output):
            file_size = os.path.getsize(pdf_output)
            print_colored(f"📄 PDF CV: {pdf_output} ({file_size:,} bytes)", Colors.GREEN)
        
        print_colored(f"🌐 HTML CV: {main_html}", Colors.GREEN)
        print_colored(f"🔗 Live URL: {tunnel_url}", Colors.GREEN)
        
        print_colored("\n💡 To rebuild:", Colors.BLUE)
        print_colored("   python3 build/build_doxygen.py", Colors.BLUE)
        print_colored(f"\n📝 To edit your CV:", Colors.BLUE)
        print_colored(f"   Edit: {dox_file}", Colors.BLUE)
        
        # Keep tunnel alive for inspection
        print_colored(f"\n🕐 Keeping tunnel alive for 30 seconds for inspection...", Colors.YELLOW)
        print_colored(f"   Visit: {tunnel_url}", Colors.YELLOW)
        time.sleep(30)
        
        print_colored("\n🎉 Build process completed!", Colors.GREEN)
        
    except KeyboardInterrupt:
        print_colored("\n⚠️  Build interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Build failed: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()

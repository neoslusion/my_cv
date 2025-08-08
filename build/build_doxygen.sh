#!/bin/bash

# Doxygen CV Build Script for Linux
# Integrates with existing build framework using ngrok and HTML-to-PDF service

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOX_FILE="docs/LePhucDuc_CV.dox"
HTML_OUTPUT_DIR="docs/generated/html"
PDF_OUTPUT="LePhucDuc_CV.pdf"
LOCAL_PDF="build/CV_Local.pdf"
HTTP_PORT=8000

echo -e "${BLUE}🚀 Building CV from Doxygen source...${NC}"

# Function to cleanup processes
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    pkill -f "python.*http.server" 2>/dev/null || true
    pkill ngrok 2>/dev/null || true
    pkill python 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Trap to ensure cleanup on script exit
trap cleanup EXIT

# Check if Doxygen is installed
if ! command -v doxygen &> /dev/null; then
    echo -e "${RED}❌ Error: Doxygen is not installed${NC}"
    echo -e "${YELLOW}📥 Install with: sudo apt-get install doxygen${NC}"
    exit 1
fi

# Check if the .dox file exists
if [ ! -f "$DOX_FILE" ]; then
    echo -e "${RED}❌ Error: CV source file not found: $DOX_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Doxygen version: $(doxygen --version)${NC}"

# Clean up any existing PDF files
if [ -f "$PDF_OUTPUT" ]; then
    rm "$PDF_OUTPUT"
    echo -e "${YELLOW}🗑️  Removed existing PDF file${NC}"
fi

# Clean up previous build output
if [ -d "$HTML_OUTPUT_DIR" ]; then
    rm -rf "docs/generated"
    echo -e "${YELLOW}🗑️  Cleaned previous build output${NC}"
fi

# Generate HTML from Doxygen
echo -e "${BLUE}📝 Generating HTML documentation from Doxygen...${NC}"
if ! doxygen Doxyfile; then
    echo -e "${RED}❌ Error: Doxygen generation failed${NC}"
    exit 1
fi

# Copy assets to generated folder
if [ -d "docs/assets" ]; then
    cp -r docs/assets "$HTML_OUTPUT_DIR/"
    echo -e "${GREEN}📂 Copied assets to generated folder${NC}"
fi

# Copy favicon
if [ -f "docs/favicon.ico" ]; then
    cp docs/favicon.ico "$HTML_OUTPUT_DIR/"
    echo -e "${GREEN}🖼️  Copied favicon to generated folder${NC}"
fi

# Find the main CV HTML file
MAIN_HTML_FILE=$(find "$HTML_OUTPUT_DIR" -name "*cv_main*.html" -o -name "*index*.html" | head -n 1)

if [ -z "$MAIN_HTML_FILE" ]; then
    # If no specific file found, use the first HTML file
    MAIN_HTML_FILE=$(find "$HTML_OUTPUT_DIR" -name "*.html" | head -n 1)
fi

if [ -z "$MAIN_HTML_FILE" ]; then
    echo -e "${RED}❌ Error: No HTML files generated${NC}"
    exit 1
fi

echo -e "${GREEN}✅ HTML CV generated successfully: $MAIN_HTML_FILE${NC}"

# Create a symlink or copy to make it accessible as index.html for the web server
if [ ! -f "$HTML_OUTPUT_DIR/index.html" ]; then
    cp "$MAIN_HTML_FILE" "$HTML_OUTPUT_DIR/index.html"
    echo -e "${GREEN}📋 Created index.html for web server${NC}"
fi

# Start HTTP server for the generated HTML
echo -e "${BLUE}🌐 Starting HTTP server on port $HTTP_PORT...${NC}"
cd "$HTML_OUTPUT_DIR"
python3 -m http.server $HTTP_PORT &
HTTP_SERVER_PID=$!
cd - > /dev/null

# Wait a bit for server to start
sleep 2

# Check if ngrok is available
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: ngrok not found. PDF generation will be skipped.${NC}"
    echo -e "${YELLOW}📥 Install ngrok or use manual PDF generation:${NC}"
    echo -e "${YELLOW}   1. Open http://localhost:$HTTP_PORT in your browser${NC}"
    echo -e "${YELLOW}   2. Use Ctrl+P to print and save as PDF${NC}"
    
    # Wait for user to potentially create PDF manually
    echo -e "${BLUE}💡 Press Enter when ready or Ctrl+C to exit...${NC}"
    read -r
    exit 0
fi

# Start ngrok tunnel
echo -e "${BLUE}🔗 Starting ngrok tunnel...${NC}"
./ngrok http $HTTP_PORT &
NGROK_PID=$!

# Wait for ngrok to establish tunnel
echo -e "${YELLOW}⏳ Waiting for ngrok tunnel to establish...${NC}"
sleep 5

# Get the ngrok tunnel URL
TUNNEL_URL=""
for i in {1..10}; do
    TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)
    
    if [ -n "$TUNNEL_URL" ]; then
        break
    fi
    echo -e "${YELLOW}⏳ Waiting for tunnel... (attempt $i/10)${NC}"
    sleep 2
done

if [ -z "$TUNNEL_URL" ]; then
    echo -e "${RED}❌ Error: Could not establish ngrok tunnel${NC}"
    echo -e "${YELLOW}📱 Manual PDF generation available at: http://localhost:$HTTP_PORT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ngrok tunnel established: $TUNNEL_URL${NC}"

# Generate PDF using the existing Python script approach
echo -e "${BLUE}📄 Generating PDF via web service...${NC}"

# Create a temporary Python script for PDF generation
cat > temp_pdf_gen.py << EOF
import requests
import re
import sys
import os

class HtmlToPdfDotNet:
    def __init__(self):
        self.size = "A4"
        self.orientation = "Portrait"
        self.width = "1024"
        self.conversion_delay = "1"

    def convert_pdf(self, url):
        try:
            # Getting validation parameters
            res = requests.get("https://www.html-to-pdf.net/free-online-pdf-converter.aspx")
            view_state = re.search(
                r'id="__VIEWSTATE" value="(.*?)"', res.content.decode(), re.S | re.M
            ).group(1)
            event_validation = re.search(
                r'id="__EVENTVALIDATION" value="(.*?)"', res.content.decode(), re.S | re.M
            ).group(1)

            # Converting
            headers = {
                "authority": "www.html-to-pdf.net",
                "cache-control": "max-age=0",
                "upgrade-insecure-requests": "1",
                "origin": "https://www.html-to-pdf.net",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }

            data = {
                "__VIEWSTATE": view_state,
                "__EVENTVALIDATION": event_validation,
                "ctl00\$ContentPlaceHolder1\$txtUrl": url,
                "ctl00\$ContentPlaceHolder1\$ddlPageSize": self.size,
                "ctl00\$ContentPlaceHolder1\$ddlPageOrientation": self.orientation,
                "ctl00\$ContentPlaceHolder1\$txtWidth": self.width,
                "ctl00\$ContentPlaceHolder1\$txtConversionDelay": self.conversion_delay,
                "ctl00\$ContentPlaceHolder1\$btnConvert": "Convert to PDF"
            }

            response = requests.post(
                "https://www.html-to-pdf.net/free-online-pdf-converter.aspx",
                headers=headers,
                data=data
            )

            if "pdf" in response.headers.get("content-type", "").lower():
                return response.content
            else:
                # Try to extract download link
                download_link = re.search(r'href="(.*?\.pdf.*?)"', response.text)
                if download_link:
                    pdf_url = "https://www.html-to-pdf.net" + download_link.group(1)
                    pdf_response = requests.get(pdf_url)
                    return pdf_response.content
                else:
                    raise Exception("Could not extract PDF content")

        except Exception as e:
            print(f"Error in PDF conversion: {e}")
            return None

# Main execution
url = "$TUNNEL_URL"
print(f"Converting URL to PDF: {url}")

converter = HtmlToPdfDotNet()
pdf_content = converter.convert_pdf(url)

if pdf_content:
    with open("$PDF_OUTPUT", "wb") as f:
        f.write(pdf_content)
    print(f"PDF generated successfully: $PDF_OUTPUT")
    print(f"PDF size: {len(pdf_content)} bytes")
else:
    print("Failed to generate PDF")
    sys.exit(1)
EOF

# Run the PDF generation
if python3 temp_pdf_gen.py; then
    echo -e "${GREEN}✅ PDF generated successfully!${NC}"
    
    # Also create a copy in the build directory
    if [ ! -d "build" ]; then
        mkdir -p build
    fi
    cp "$PDF_OUTPUT" "build/"
    echo -e "${GREEN}📁 PDF copied to build directory${NC}"
else
    echo -e "${RED}❌ PDF generation failed${NC}"
    echo -e "${YELLOW}📱 You can still access the HTML version at: $TUNNEL_URL${NC}"
fi

# Clean up temporary files
rm -f temp_pdf_gen.py

# Show results
echo -e "\n${GREEN}✨ Build completed!${NC}"
if [ -f "$PDF_OUTPUT" ]; then
    echo -e "${GREEN}📄 PDF CV: $PDF_OUTPUT${NC}"
    echo -e "${GREEN}📊 PDF size: $(ls -lh $PDF_OUTPUT | awk '{print $5}')${NC}"
fi
echo -e "${GREEN}🌐 HTML CV: $MAIN_HTML_FILE${NC}"
echo -e "${GREEN}🔗 Live URL: $TUNNEL_URL${NC}"

echo -e "\n${BLUE}💡 To rebuild:${NC}"
echo -e "${BLUE}   ./build/build_doxygen.sh${NC}"
echo -e "\n${BLUE}📝 To edit your CV:${NC}"
echo -e "${BLUE}   Edit: $DOX_FILE${NC}"

# Keep the tunnel alive for a bit longer for manual inspection
echo -e "\n${YELLOW}🕐 Keeping tunnel alive for 30 seconds for inspection...${NC}"
echo -e "${YELLOW}   Visit: $TUNNEL_URL${NC}"
sleep 30

echo -e "\n${GREEN}🎉 Build process completed!${NC}"

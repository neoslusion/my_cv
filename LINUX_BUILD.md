# Linux Build System Integration for Doxygen CV

This document explains how the new Doxygen CV system integrates with the existing Linux-based build framework using ngrok and HTML-to-PDF.net service.

## 🏗️ Build System Overview

The repository now supports **two build workflows**:

1. **Original HTML Workflow** - Direct HTML editing with external PDF conversion
2. **New Doxygen Workflow** - Source-based CV generation with automated HTML and PDF output

## 🚀 Quick Start (Linux/CI Environment)

### Using the New Doxygen Workflow

```bash
# Install dependencies
sudo apt-get install doxygen
pip install -r requirements.txt

# Run Doxygen build
./build/build.sh doxygen
```

### Using the Original Workflow

```bash
# Run original build
./build/build.sh
```

## 📁 File Structure for Linux Build

```
my_cv/
├── build/
│   ├── build.sh              # Main build script (supports both workflows)
│   ├── build_doxygen.sh      # Bash script for Doxygen workflow
│   ├── build_doxygen.py      # Python script for Doxygen workflow
│   ├── get_via_htmltopdf.py  # Original HTML-to-PDF conversion
│   └── api.py                # HTML-to-PDF.net API wrapper
├── docs/
│   ├── LePhucDuc_CV.dox      # Doxygen CV source
│   ├── doxygen_header.html   # Custom HTML template
│   ├── doxygen_footer.html   # Custom HTML footer
│   ├── generated/            # Generated output (created during build)
│   └── assets/               # CSS and images
├── Doxyfile                  # Doxygen configuration
├── .github/workflows/
│   └── python-app.yml        # Updated GitHub Actions workflow
└── requirements.txt          # Python dependencies
```

## 🔧 Build Process Details

### Doxygen Workflow Process

1. **Environment Check**: Verify Doxygen and dependencies
2. **HTML Generation**: Run `doxygen Doxyfile` to generate HTML from `.dox` source
3. **Asset Management**: Copy CSS, images, and favicon to generated folder
4. **Web Server**: Start Python HTTP server for the generated HTML
5. **Tunnel Creation**: Use ngrok to create public tunnel
6. **PDF Generation**: Convert HTML to PDF using HTML-to-PDF.net service
7. **Output Management**: Save PDF and provide access URLs

### Integration with Existing System

The new system reuses existing infrastructure:

- **ngrok tunneling** - Same tunnel setup as original build
- **HTML-to-PDF.net service** - Reuses existing `api.py` wrapper
- **GitHub Actions** - Enhanced existing workflow with Doxygen support
- **Build scripts** - Extended `build.sh` to support both workflows

## 🛠️ Configuration Options

### Build Method Selection

**In GitHub Actions** (`.github/workflows/python-app.yml`):
```yaml
env:
  BUILD_METHOD: "doxygen"  # Options: "html" or "doxygen"
```

**Local Build**:
```bash
# Doxygen workflow
./build/build.sh doxygen

# Original workflow  
./build/build.sh
```

### Doxygen Configuration

Key settings in `Doxyfile`:
```
PROJECT_NAME           = "Le Phuc Duc - CV"
INPUT                  = docs/LePhucDuc_CV.dox
OUTPUT_DIRECTORY       = docs/generated
HTML_HEADER            = docs/doxygen_header.html
HTML_FOOTER            = docs/doxygen_footer.html
HTML_EXTRA_STYLESHEET  = docs/assets/css/devresume.css
```

## 📝 Editing Your CV (Doxygen Source)

Edit `docs/LePhucDuc_CV.dox` using Doxygen syntax:

```doxygen
/**
 * @page cv_main Your Name - Curriculum Vitae
 * 
 * @section contact_info Contact Information
 * - **Name:** Your Full Name
 * - **Email:** your.email@example.com
 * - **Phone:** +1234567890
 * 
 * @section skills Technical Skills
 * - **Programming Languages:** C++, Python, JavaScript
 * - **Frameworks:** React, Django, Node.js
 * - **Tools:** Git, Docker, Jenkins
 * 
 * @section experience Work Experience
 * 
 * @subsection current_company Current Company Name
 * **Location:** City, Country
 * 
 * @subsubsection current_role Software Engineer (Jan 2022 – Present)
 * **Product:** Product Name
 * **Customer:** Customer Name
 * 
 * **Responsibilities:**
 * - Developed scalable web applications
 * - Led cross-functional teams
 * - Implemented CI/CD pipelines
 * 
 * **Achievements:**
 * - Improved system performance by 40%
 * - Reduced deployment time by 60%
 */
```

## 🔄 GitHub Actions Integration

The workflow automatically:

1. **Detects Changes**: Triggers on changes to `docs/`, `build/`, or `Doxyfile`
2. **Sets Up Environment**: Installs Doxygen and Python dependencies
3. **Configures ngrok**: Sets up tunneling with secret token
4. **Builds CV**: Runs appropriate build workflow based on `BUILD_METHOD`
5. **Verifies Output**: Checks PDF generation success
6. **Publishes Release**: Uploads PDF to GitHub Releases

### Required Secrets

Ensure these secrets are set in your GitHub repository:

- `ngrok_token` - Your ngrok authentication token

### Workflow Environment Variables

```yaml
env:
  BUILD_METHOD: "doxygen"  # Choose workflow: "html" | "doxygen"
```

## 🐧 Linux Dependencies

### System Packages
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y doxygen

# CentOS/RHEL
sudo yum install doxygen

# Arch Linux
sudo pacman -S doxygen
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - For HTTP API calls
- `gitpython` - For Git operations (original workflow)

## 🔧 Build Script Options

### Main Build Script (`build/build.sh`)

```bash
# Doxygen workflow (recommended for new CVs)
./build/build.sh doxygen

# Original HTML workflow (for existing HTML-based CVs)
./build/build.sh

# Alternative: Direct script execution
./build/build_doxygen.sh        # Bash version
python3 build/build_doxygen.py  # Python version
```

### Script Features

**Bash Script** (`build_doxygen.sh`):
- ✅ Colored terminal output
- ✅ Process cleanup on exit
- ✅ Error handling with meaningful messages
- ✅ ngrok integration
- ✅ PDF generation via web service

**Python Script** (`build_doxygen.py`):
- ✅ Cross-platform compatibility
- ✅ Enhanced error handling
- ✅ API integration with existing `build/api.py`
- ✅ Colored output with emoji indicators
- ✅ Robust tunnel management

## 🚨 Troubleshooting

### Common Issues

**"Doxygen not found"**
```bash
# Install Doxygen
sudo apt-get install doxygen

# Verify installation
doxygen --version
```

**"ngrok tunnel failed"**
```bash
# Check if ngrok is available
./ngrok version

# Verify authentication
./ngrok config add-authtoken YOUR_TOKEN
```

**"PDF generation failed"**
- Check tunnel URL accessibility
- Verify HTML content is properly generated
- Ensure HTML-to-PDF.net service is available
- Check for network connectivity issues

**"Permission denied"**
```bash
# Make scripts executable
chmod +x build/build.sh
chmod +x build/build_doxygen.sh
```

### Debug Mode

Enable verbose output:
```bash
# For bash script
DEBUG=1 ./build/build_doxygen.sh

# For Python script
python3 build/build_doxygen.py --verbose
```

## 🔄 Migration from Original System

To migrate from the original HTML-based system:

1. **Keep existing setup** - Both systems can coexist
2. **Update GitHub Actions** - Change `BUILD_METHOD` to `"doxygen"`
3. **Convert content** - Transfer CV content from HTML to `.dox` format
4. **Test build** - Run `./build/build.sh doxygen` locally
5. **Commit changes** - Push to trigger automated build

## 🎯 Advanced Usage

### Custom PDF Styling

Modify CSS in `docs/doxygen_header.html`:
```css
/* Custom PDF styles */
@media print {
    body { font-size: 12pt; }
    .contents { margin: 0; padding: 0; }
}
```

### Multiple Output Formats

The system can be extended to generate additional formats:
- LaTeX output (set `GENERATE_LATEX = YES` in Doxyfile)
- XML output for further processing
- RTF output for Word compatibility

### Integration with Other Services

Replace HTML-to-PDF.net with alternatives:
- wkhtmltopdf (local generation)
- Puppeteer (headless Chrome)
- WeasyPrint (CSS-based PDF generation)

## 📊 Performance Considerations

- **Build Time**: Doxygen workflow ~30-60 seconds (including PDF generation)
- **Output Size**: Typical PDF size 100-500KB
- **Dependencies**: Minimal system requirements (Doxygen + Python)
- **Scalability**: Can handle large CVs with multiple sections

## 🔮 Future Enhancements

Potential improvements:
- Multiple CV templates
- Multi-language support
- Integration with LinkedIn API
- Automated grammar checking
- PDF optimization
- Docker containerization for consistent builds

---

The Linux build system integration provides a robust, automated solution for generating professional CVs from source files while maintaining compatibility with existing infrastructure and workflows.

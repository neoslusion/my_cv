# Doxygen CV Build System

This project now supports generating your CV from a Doxygen documentation file (`.dox`) into both HTML and PDF formats using the existing beautiful DevResume theme.

## Prerequisites

### Required Software
1. **Doxygen** - For generating HTML from .dox files
   - Download from: https://www.doxygen.nl/download.html
   - Make sure `doxygen` is in your PATH

2. **Python 3.x** - For PDF generation
   - Download from: https://python.org

### Python Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install weasyprint
```

## Quick Start

### Method 1: Using PowerShell (Windows)
```powershell
# Build both HTML and PDF
.\build-cv.ps1

# Build and open HTML result
.\build-cv.ps1 -OpenResult

# Skip PDF generation
.\build-cv.ps1 -SkipPdf
```

### Method 2: Using Batch File (Windows)
```cmd
# Double-click build-cv.bat or run:
build-cv.bat
```

### Method 3: Using Python (Cross-platform)
```bash
# Build both HTML and PDF
python build_cv.py

# Build and open HTML result
python build_cv.py --open

# Skip PDF generation
python build_cv.py --skip-pdf
```

## File Structure

### Input Files
- `docs/LePhucDuc_CV.dox` - Your CV content in Doxygen format
- `docs/assets/css/devresume.css` - Styling theme
- `docs/assets/images/` - Images used in CV
- `docs/doxygen_header.html` - Custom HTML header template
- `docs/doxygen_footer.html` - Custom HTML footer template

### Configuration
- `Doxyfile` - Doxygen configuration file

### Output Files
- `docs/generated/html/` - Generated HTML documentation
- `build/LePhucDuc_CV.pdf` - Generated PDF file

## Editing Your CV

Edit the `docs/LePhucDuc_CV.dox` file using Doxygen documentation syntax:

```doxygen
/**
 * @page cv_main Your Name - Curriculum Vitae
 * 
 * @section contact_info Contact Information
 * - **Name:** Your Name
 * - **Email:** your.email@example.com
 * 
 * @section skills Skills
 * - **Programming Languages:** C++, Python, JavaScript
 * 
 * @section experience Work Experience
 * 
 * @subsection company_name Company Name
 * **Location:** City, Country
 * 
 * @subsubsection role_name Job Title (Start Date – End Date)
 * **Responsibilities:**
 * - Your responsibility 1
 * - Your responsibility 2
 */
```

## Customization

### Styling
- Modify `docs/assets/css/devresume.css` for theme changes
- Edit `docs/doxygen_header.html` and `docs/doxygen_footer.html` for layout changes
- Adjust CSS styles in the header template for custom appearance

### Doxygen Configuration
- Edit `Doxyfile` to change Doxygen generation settings
- Common settings:
  - `PROJECT_NAME` - Your project/CV title
  - `OUTPUT_DIRECTORY` - Where files are generated
  - `HTML_EXTRA_STYLESHEET` - Additional CSS files

### PDF Settings
- PDF styling is controlled in the build scripts
- Modify the CSS in the PDF generation section for custom PDF appearance
- Page size, margins, and fonts can be adjusted

## Troubleshooting

### Common Issues

1. **Doxygen not found**
   - Make sure Doxygen is installed and in your PATH
   - Try running `doxygen --version` in terminal

2. **PDF generation fails**
   - Ensure Python is installed: `python --version`
   - Install weasyprint: `pip install weasyprint`
   - On some systems, you may need additional dependencies for weasyprint

3. **HTML styling issues**
   - Check that CSS files are in the correct location
   - Verify paths in `Doxyfile` and template files

4. **Images not showing**
   - Ensure images are in `docs/assets/images/`
   - Update `IMAGE_PATH` in `Doxyfile` if needed

### Platform-Specific Notes

**Windows:**
- Use PowerShell or Command Prompt
- Make sure execution policy allows script running: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Linux/macOS:**
- Make Python script executable: `chmod +x build_cv.py`
- Install system dependencies for weasyprint if needed

## GitHub Actions Integration

The existing GitHub Actions workflow in `.github/workflows/python-app.yml` can be updated to use the new Doxygen build system for automated PDF generation on every commit.

## Output Examples

After building, you'll have:
- **HTML Version**: Professional web-based CV with responsive design
- **PDF Version**: Print-ready PDF with proper formatting
- **Consistent Styling**: Both versions use the same DevResume theme

The generated HTML includes:
- Responsive design for mobile and desktop
- Professional typography
- Download link for PDF version
- Clean, modern layout

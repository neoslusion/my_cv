# Complete Setup Guide: Doxygen CV to HTML/PDF

This guide shows you how to set up a system that converts your Doxygen CV file into beautiful HTML and PDF versions using the existing DevResume theme.

## 📋 Quick Start (TL;DR)

1. **Install Doxygen**: Download from https://www.doxygen.nl/download.html
2. **Run the build**: `python build_cv_simple.py`
3. **View result**: HTML opens automatically in your browser
4. **Create PDF**: Use Ctrl+P in browser to save as PDF

## 📁 What You Have Now

Your CV setup includes:

### 📝 Source Files
- `docs/LePhucDuc_CV.dox` - Your CV content in Doxygen format
- `docs/assets/css/devresume.css` - Beautiful styling theme
- `docs/assets/images/` - Profile pictures and images

### 🔧 Configuration Files
- `Doxyfile` - Doxygen configuration (customized for CV generation)
- `docs/doxygen_header.html` - Custom HTML template (integrates with DevResume theme)
- `docs/doxygen_footer.html` - Custom HTML footer

### 🚀 Build Scripts
- `build_cv_simple.py` - Recommended: Simple, reliable build script
- `build_cv.py` - Advanced: Includes automatic PDF generation (requires complex dependencies)
- `build-cv.ps1` - PowerShell version for Windows
- `build-cv.bat` - Batch file for easy Windows execution

### 📄 Output
- `docs/generated/html/cv_main.html` - Generated HTML CV
- `build/LePhucDuc_CV.pdf` - PDF version (when created)

## 🛠️ Setup Instructions

### Step 1: Install Doxygen
1. Go to https://www.doxygen.nl/download.html
2. Download the installer for your operating system
3. Install and make sure `doxygen` is in your PATH
4. Test: Open command prompt and run `doxygen --version`

### Step 2: Build Your CV
Run one of these commands in your project directory:

**Option A: Simple Python Script (Recommended)**
```bash
python build_cv_simple.py
```

**Option B: PowerShell (Windows)**
```powershell
.\build-cv.ps1
```

**Option C: Batch File (Windows)**
```cmd
build-cv.bat
```

### Step 3: View and Create PDF
1. The HTML CV opens automatically in your browser
2. To create PDF: Press Ctrl+P (or Cmd+P on Mac)
3. Select "Save as PDF" and save to the `build` folder

## ✏️ Editing Your CV

Edit the `docs/LePhucDuc_CV.dox` file using Doxygen syntax:

### Basic Structure
```doxygen
/**
 * @page cv_main Your Name - Curriculum Vitae
 * 
 * @section contact_info Contact Information
 * - **Name:** Your Full Name
 * - **Email:** your.email@example.com
 * - **Phone:** +1234567890
 * - **Location:** Your City, Country
 * 
 * @section skills Skills
 * - **Programming Languages:** C++, Python, JavaScript
 * - **Frameworks:** React, Node.js, Django
 * - **Tools:** Git, Docker, AWS
 * 
 * @section experience Work Experience
 * 
 * @subsection company1 Company Name
 * **Location:** City, Country
 * 
 * @subsubsection role1 Software Engineer (Jan 2022 – Present)
 * **Responsibilities:**
 * - Developed web applications using modern technologies
 * - Collaborated with cross-functional teams
 * - Implemented automated testing and CI/CD pipelines
 * 
 * **Achievements:**
 * - Increased system performance by 40%
 * - Led a team of 5 developers
 */
```

### Doxygen Syntax Reference
- `@page` - Creates a main page
- `@section` - Major sections (Contact, Skills, Experience)
- `@subsection` - Company or institution names
- `@subsubsection` - Specific roles or positions
- `**Bold text**` - Makes text bold
- `- Item` - Creates bullet points

## 🎨 Customization

### Styling
1. **Colors**: Edit `docs/doxygen_header.html` CSS section
2. **Layout**: Modify the same file for structure changes
3. **Theme**: Replace `docs/assets/css/devresume.css` with your preferred theme

### Content Structure
1. **Add new sections**: Use `@section new_section_name Section Title`
2. **Change order**: Rearrange sections in the .dox file
3. **Add images**: Place in `docs/assets/images/` and reference with `\image html filename.jpg`

### Build Configuration
1. **Project name**: Edit `PROJECT_NAME` in `Doxyfile`
2. **Output location**: Change `OUTPUT_DIRECTORY` in `Doxyfile`
3. **Additional files**: Add to `HTML_EXTRA_FILES` in `Doxyfile`

## 🔄 Automation Options

### GitHub Actions (Existing)
Your repository already has `.github/workflows/python-app.yml` that can be updated to use the new Doxygen system.

### Local Automation
- **Windows**: Set up scheduled task to run build script
- **Mac/Linux**: Use cron jobs for regular rebuilds
- **VS Code**: Add build task to `.vscode/tasks.json`

## 🐛 Troubleshooting

### Common Issues

**"Doxygen not found"**
- Install Doxygen from official website
- Make sure it's in your system PATH
- Restart command prompt/terminal after installation

**"No HTML files generated"**
- Check that `docs/LePhucDuc_CV.dox` exists
- Verify Doxygen syntax in your .dox file
- Look for error messages in Doxygen output

**"CSS not loading"**
- Ensure `docs/assets/css/devresume.css` exists
- Check file paths in `docs/doxygen_header.html`
- Verify assets were copied to generated folder

**"Images not showing"**
- Place images in `docs/assets/images/`
- Use relative paths in Doxygen: `\image html profile.jpg`
- Check that images are copied during build

### Platform-Specific Notes

**Windows:**
- Use PowerShell or Command Prompt
- Some antivirus software may interfere with file generation
- Use forward slashes (/) in paths when possible

**macOS:**
- Install Doxygen via Homebrew: `brew install doxygen`
- Use Terminal for command-line operations

**Linux:**
- Install via package manager: `sudo apt install doxygen` (Ubuntu/Debian)
- Ensure proper file permissions for output directories

## 🚀 Advanced Features

### Multiple Output Formats
The Doxyfile is configured to generate:
- HTML with custom styling
- Search functionality
- Mobile-responsive design

### Integration with Existing System
The new Doxygen system works alongside your existing build scripts in the `build/` folder, so you can use both approaches.

### PDF Generation Options
1. **Manual** (Recommended): Print from browser
2. **Automated**: Use `build_cv.py` with weasyprint (requires additional setup)
3. **Web Service**: Use existing `build/get_via_htmltopdf.py` system

## 📚 Resources

- **Doxygen Documentation**: https://www.doxygen.nl/manual/
- **DevResume Theme**: Original theme by Xiaoying Riley
- **Doxygen Commands**: https://www.doxygen.nl/manual/commands.html
- **CSS Customization**: Standard CSS applies to customize appearance

## 🎯 Next Steps

1. **Edit your CV**: Update `docs/LePhucDuc_CV.dox` with your information
2. **Customize styling**: Modify colors and layout in header template
3. **Add your photo**: Place in `docs/assets/images/` and reference in CV
4. **Test build**: Run `python build_cv_simple.py` to verify everything works
5. **Share**: The generated HTML works on any web server or can be shared directly

Your CV system is now ready! You can easily maintain a professional-looking CV by editing a simple text file and running a build command.

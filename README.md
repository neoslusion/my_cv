# CV Generation System

Professional, responsive web CV with automated PDF generation, powered by Doxygen documentation system and CI/CD pipeline from GitHub Actions.

## 🚀 Quick Start

### New: Doxygen-Based CV System (Recommended)

**Windows:**
```powershell
# Simple build (opens in browser automatically)
python build_cv_simple.py

# Full build with PDF attempt
python build_cv.py
```

**Linux/CI:**
```bash
# Install dependencies
sudo apt-get install doxygen
pip install -r requirements.txt

# Run build
./build/build.sh doxygen
```

**Edit your CV:** Modify `docs/LePhucDuc_CV.dox` using simple Doxygen syntax

📚 **Complete guides:**
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and usage instructions
- **[LINUX_BUILD.md](LINUX_BUILD.md)** - Linux build system integration
- **[DOXYGEN_BUILD.md](DOXYGEN_BUILD.md)** - Doxygen-specific documentation

### Original HTML-Based System

You can still use the original system by editing `docs/index.html` directly and using the build scripts in the `build/` folder.

## 🎯 Why This System?

**The Problem:** Writing a CV shouldn't require fighting with design tools or worrying about formatting. You want to focus on content, not layout.

**The Solution:** Write your CV in simple text format (Doxygen), get beautiful HTML and PDF outputs automatically.

### ✨ Key Benefits

- **📝 Content-First**: Edit CV in simple text format, no HTML/CSS knowledge needed
- **🎨 Professional Design**: Beautiful, responsive DevResume theme included
- **🤖 Automated**: CI/CD pipeline generates PDF on every commit
- **📱 Multi-Platform**: Works on Windows, Linux, and in GitHub Actions
- **🔄 Version Control**: Text-based source is perfect for Git tracking
- **🌐 Dual Output**: Get both web-ready HTML and print-ready PDF

### 🔧 Technical Features

- **Source-based Generation**: Doxygen converts `.dox` text files to professional HTML
- **Integrated Build System**: Works with existing ngrok + HTML-to-PDF.net infrastructure  
- **Cross-platform Scripts**: Python, PowerShell, and Bash build options
- **GitHub Actions Ready**: Automated builds with secret management
- **Asset Management**: Automatic handling of CSS, images, and fonts
- **Error Handling**: Comprehensive error checking and user feedback

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   CV Source     │    │   Doxygen    │    │  Beautiful HTML │
│ (.dox text file)│───▶│  Generator   │───▶│   + DevResume   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌──────────────┐              │
│  Professional   │    │ HTML-to-PDF  │◄─────────────┘
│   PDF Output    │◄───│  Conversion  │
└─────────────────┘    └──────────────┘
```

## 📋 What You Get

### 📄 Input (Easy to Edit)
```doxygen
/**
 * @section experience Work Experience
 * @subsection bosch_company Bosch Global Software Technologies
 * @subsubsection current_role Software Engineer (Feb 2024 – Present)
 * **Responsibilities:**
 * - Software Developer in Master ECU development
 * - DevOps activities and CI/CD pipeline setup
 */
```

### 🌐 Output (Professional Results)
- **HTML CV**: Mobile-responsive, professional design
- **PDF CV**: Print-ready, properly formatted
- **Live URL**: Shareable web link via ngrok tunnel
- **GitHub Release**: Automatic PDF publishing

## But why?
I would love to write a CV without bothering too much about the design, where I can easily update & share. Oh, and it should be automated because I like to automate stuff.

Web page CV is lovely, responsive for both desktop & mobile, but it is not PDF, which HRs will need. So I built a CI/CD pipeline via Github Actions to build PDF file based on the web page and post it on [Release Page](https://github.com/neoslusion/my_cv/releases).

## Credits
* Designed by [Xiaoying Riley](https://github.com/xriley/DevResume-Theme). Thank you!
<!-- * Forked from my friend's repo [Trung Le](https://github.com/jackblk). Thank bro, for the amazing CV's concept. -->

# CV Generation System

Nice looking, responsive web page CV on both desktop & mobile with auto-generated PDF file, powered by Doxygen documentation system and CI/CD pipeline from Github Actions.

## 🚀 Quick Start

### New: Doxygen-Based CV System (Recommended)

1. **Install Doxygen**: Download from https://www.doxygen.nl/download.html
2. **Build your CV**: `python build_cv_simple.py`
3. **Edit content**: Modify `docs/LePhucDuc_CV.dox` file
4. **Create PDF**: Use browser print function (Ctrl+P)

📚 **See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete instructions**

### Original HTML-Based System

You can still use the original system by editing `docs/index.html` directly and using the build scripts in the `build/` folder.

## But why?
I would love to write a CV without bothering too much about the design, where I can easily update & share. Oh, and it should be automated because I like to automate stuff.

Web page CV is lovely, responsive for both desktop & mobile, but it is not PDF, which HRs will need. So I built a CI/CD pipeline via Github Actions to build PDF file based on the web page and post it on [Release Page](https://github.com/neoslusion/my_cv/releases).

## Credits
* Designed by [Xiaoying Riley](https://github.com/xriley/DevResume-Theme). Thank you!
<!-- * Forked from my friend's repo [Trung Le](https://github.com/jackblk). Thank bro, for the amazing CV's concept. -->

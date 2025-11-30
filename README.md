# CV Generator - Le Phuc Duc

This project generates a professional CV in PDF format from a Doxygen-formatted source file.

## Features

- **Source**: CV content written in Doxygen markup format (`.dox` file)
- **Output**: Professional PDF document
- **Build System**: CMake + Doxygen + LaTeX
- **Custom Styling**: Optimized for CV presentation with compact layout

## Quick Start

### Using the Build Script (Recommended)
```bash
./build_cv.sh
```

### Using CMake directly
```bash
mkdir -p build && cd build
cmake ..
make doc
```

## File Structure

```
├── build_cv.sh                          # Convenient build script
├── LePhucDuc_CV.pdf                      # Generated CV PDF (output)
├── docs/
│   ├── LePhucDuc_CV.dox                  # CV content source file (adapted to match .docx)
│   ├── LePhucDuc_CV.docx                 # Reference Word document
│   └── CMakeLists.txt                    # Documentation build config
├── build_environment/
│   ├── cmake_common/
│   │   ├── doxygen.cmake                 # Doxygen configuration
│   │   └── venv.cmake                    # Python environment setup
│   └── tool/
│       └── doxygen/
│           ├── Doxyfile.in               # Doxygen configuration template
│           ├── latex_header.tex          # Custom LaTeX header
│           └── cv_style.sty              # LaTeX styling package
└── build/                                # Build artifacts (generated)
    └── docs/latex/refman.pdf             # Original PDF location
```

## How It Works

1. **Source**: CV content is written in `docs/LePhucDuc_CV.dox` using Doxygen markup
2. **Configuration**: Doxygen is configured via `Doxyfile.in` for PDF generation
3. **Processing**: 
   - Doxygen parses the .dox file and generates LaTeX
   - XeLaTeX compiles the LaTeX to PDF
   - PDF is copied to project root as `LePhucDuc_CV.pdf`

## Customization

### Updating CV Content
Edit `docs/LePhucDuc_CV.dox` and rebuild:
```bash
./build_cv.sh
```

### Modifying Appearance
Adjust settings in `build_environment/tool/doxygen/Doxyfile.in`:
- `PROJECT_NAME`: Document title
- `PROJECT_BRIEF`: Subtitle
- `PAPER_TYPE`: Paper size (a4, letter, etc.)
- `COMPACT_LATEX`: Layout density
- `EXTRA_PACKAGES`: Additional LaTeX packages

## Requirements

- CMake (3.10+)
- Doxygen (1.9+)
- pdfLaTeX (TeX Live 2022+)
- Make

## Format Adaptation

The PDF format has been adapted to closely match the provided `.docx` file with:
- **Times New Roman font** throughout the document
- **Centered section headers** with bold formatting
- **Compact layout** similar to the Word document structure
- **Professional formatting** with proper spacing and alignment
- **Contact information** displayed in a single line with separators
- **Work experience sections** with right-aligned dates
- **Structured bullet points** for responsibilities and achievements

## Output

The generated PDF (`LePhucDuc_CV.pdf`) includes:
- Personal information and contact details (single line format)
- Skills section with programming languages, automotive knowledge, and tools
- Education history with right-aligned dates
- Work experience with detailed responsibilities organized by position
- Key achievements for each role
- Professional formatting matching the .docx layout

## Development

To modify the build process:
1. Update `build_environment/cmake_common/doxygen.cmake` for Doxygen setup
2. Update `docs/CMakeLists.txt` for build targets
3. Update `build_environment/tool/doxygen/Doxyfile.in` for Doxygen configuration
4. Modify `docs/LePhucDuc_CV.dox` to change CV content and structure

## Deployment Options

### PDF Generation (Local)
```bash
./build_cv.sh
```

### HTML CV Deployment (GitHub Pages)
The project includes automatic deployment to GitHub Pages:
- **HTML CV**: Available at `https://<username>.github.io/my_cv/`
- **Auto-deployment**: Triggered on pushes to `main` branch that modify `docs/` folder
- **Workflow**: See `.github/workflows/python-app.yml`

### Content Synchronization
Use the sync script to maintain consistency between formats:
```bash
./sync_cv_content.sh
```

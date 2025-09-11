# System Requirements for CV Generation

## Required Software

### 1. LaTeX Distribution
The CV generation requires a LaTeX distribution with pdflatex.

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
```

#### CentOS/RHEL/Fedora:
```bash
sudo dnf install texlive-latex texlive-collection-latexrecommended texlive-collection-latexextra
```

#### macOS (with Homebrew):
```bash
brew install --cask mactex
```

### 2. Doxygen
```bash
# Ubuntu/Debian
sudo apt-get install doxygen

# CentOS/RHEL/Fedora  
sudo dnf install doxygen

# macOS
brew install doxygen
```

### 3. CMake
```bash
# Ubuntu/Debian
sudo apt-get install cmake

# CentOS/RHEL/Fedora
sudo dnf install cmake

# macOS
brew install cmake
```

## Verification
After installation, verify the tools are available:
```bash
pdflatex --version
doxygen --version
cmake --version
```

## Alternative: Docker-based Build
If you prefer not to install LaTeX locally, you can use a Docker container:

```bash
# Build using Docker (if Docker is available)
docker run --rm -v $(pwd):/workspace -w /workspace \
  texlive/texlive:latest bash -c \
  "apt-get update && apt-get install -y cmake doxygen && ./build_cv.sh"
```

## Troubleshooting

### Common Issues:
1. **"pdflatex: Not a directory"**: LaTeX not installed or not in PATH
2. **Missing packages**: Install complete LaTeX distribution
3. **Font errors**: Ensure Times font package is installed

### Quick Test:
```bash
# Test LaTeX installation
echo "\\documentclass{article}\\begin{document}Hello World\\end{document}" | pdflatex
```

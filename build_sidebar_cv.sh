#!/bin/bash
# Build the sidebar-style CV PDF
# Requires: pdflatex, python3

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building Sidebar CV ==="
echo ""

# Check for pdflatex
if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex not found. Please install texlive:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-latex-extra texlive-fonts-extra"
    echo "  Fedora: sudo dnf install texlive-scheme-full"
    exit 1
fi

# Check for required LaTeX packages
echo "Checking LaTeX packages..."
kpsewhich paracol.sty > /dev/null 2>&1 || {
    echo "Error: paracol package not found. Install with:"
    echo "  sudo apt-get install texlive-latex-extra"
    exit 1
}
kpsewhich fontawesome5.sty > /dev/null 2>&1 || {
    echo "Error: fontawesome5 package not found. Install with:"
    echo "  sudo apt-get install texlive-fonts-extra"
    exit 1
}

# Run the Python script
python3 "${SCRIPT_DIR}/tool/build_sidebar_cv.py"

echo ""
echo "=== Done ==="

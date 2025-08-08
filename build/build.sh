#!/bin/bash

# CV Build Script - Supports both original HTML and new Doxygen workflow
# Usage: 
#   ./build.sh          - Original HTML workflow
#   ./build.sh doxygen  - New Doxygen workflow

WORKFLOW=${1:-"html"}

if [ "$WORKFLOW" = "doxygen" ]; then
    echo "🚀 Using Doxygen build workflow..."
    
    # Check if Python script exists, otherwise use bash script
    if [ -f "build/build_doxygen.py" ]; then
        echo "📝 Running Python Doxygen build script..."
        python3 build/build_doxygen.py
    elif [ -f "build/build_doxygen.sh" ]; then
        echo "📝 Running Bash Doxygen build script..."
        chmod +x build/build_doxygen.sh
        bash build/build_doxygen.sh
    else
        echo "❌ Error: No Doxygen build script found"
        exit 1
    fi
    exit 0
fi

echo "🚀 Using original HTML build workflow..."

# Original build script content
# Prepare
inputfile="my_cv_repo/docs/LePhucDuc_CV.docx"
file="LePhucDuc_CV.pdf"
if [ -f "$file" ] ; then
    rm "$file"
fi
killall ngrok 2>/dev/null || true
killall python 2>/dev/null || true

# Getting stuff
echo "Setting up..."
sh -c "python -m http.server 8000" & echo "Running HTTP Server"
sh -c "./ngrok http 8000" & echo "Running Ngrok"
echo "Waiting for 5 seconds." && sleep 5
echo "\nFinished setting up!\n"
echo "Getting PDF file."
python build/get_via_htmltopdf.py
#python docs/convert_docx2pdf.py

libreoffice --headless --convert-to pdf $inputfile

# Clean up
killall python 2>/dev/null || true
killall ngrok 2>/dev/null || true
echo "Killed ngrok & python processes."

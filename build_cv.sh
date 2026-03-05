#!/bin/bash

# Build script for generating CV PDF from Doxygen
# Usage: ./build_cv.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
CV_PDF="$PROJECT_ROOT/LePhucDuc_CV.pdf"

echo "=== CV PDF Generation Script ==="

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Creating build directory..."
    mkdir -p "$BUILD_DIR"
fi

# Change to build directory and configure
cd "$BUILD_DIR"
if [ ! -f "Makefile" ]; then
    echo "Configuring project with CMake..."
    cmake ..
fi

# Build the documentation
echo "Building CV PDF..."
make doc > /dev/null 2>&1

# Check result
if [ -f "$CV_PDF" ]; then
    echo "CV PDF generated successfully: $CV_PDF"
    echo "File size: $(du -h "$CV_PDF" | cut -f1)"
else
    echo "Error: Failed to generate CV PDF"
    exit 1
fi

echo "=== Build Complete ==="

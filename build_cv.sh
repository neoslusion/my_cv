#!/bin/bash

# Build script for generating CV PDF from Doxygen
# Usage: ./build_cv.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"

echo "=== CV PDF Generation Script ==="
echo "Project root: $PROJECT_ROOT"
echo "Build directory: $BUILD_DIR"

# Check if build directory exists, if not create it
if [ ! -d "$BUILD_DIR" ]; then
    echo "Creating build directory..."
    mkdir -p "$BUILD_DIR"
fi

# Change to build directory
cd "$BUILD_DIR"

# Configure with CMake if needed
if [ ! -f "Makefile" ]; then
    echo "Configuring project with CMake..."
    cmake ..
fi

# Build the documentation
echo "Building CV PDF..."
make doc

# Check if PDF was generated
CV_PDF="$PROJECT_ROOT/LePhucDuc_CV.pdf"
if [ -f "$CV_PDF" ]; then
    echo "✅ CV PDF generated successfully!"
    echo "📄 CV PDF location: $CV_PDF"
    
    # Display file size and creation time
    file_size=$(du -h "$CV_PDF" | cut -f1)
    echo "📊 File size: $file_size"
    echo "🕒 Generated at: $(date)"
else
    echo "❌ Failed to generate CV PDF"
    exit 1
fi

# Optionally open the PDF (uncomment if desired)
# if command -v xdg-open > /dev/null; then
#     echo "Opening PDF..."
#     xdg-open "$CV_PDF"
# fi

echo "=== Build Complete ==="

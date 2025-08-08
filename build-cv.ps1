# PowerShell script to build CV from Doxygen source
# Build CV from .dox file to HTML and PDF

param(
    [switch]$SkipPdf = $false,
    [switch]$OpenResult = $false
)

Write-Host "Building CV from Doxygen source..." -ForegroundColor Green

# Check if Doxygen is installed
try {
    $doxygenVersion = doxygen --version 2>$null
    Write-Host "Found Doxygen version: $doxygenVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Doxygen not found. Please install Doxygen first." -ForegroundColor Red
    Write-Host "Download from: https://www.doxygen.nl/download.html" -ForegroundColor Yellow
    exit 1
}

# Create output directories
$outputDir = "docs\generated"
if (Test-Path $outputDir) {
    Remove-Item $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Run Doxygen to generate HTML
Write-Host "Generating HTML documentation..." -ForegroundColor Cyan
doxygen Doxyfile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Doxygen generation failed!" -ForegroundColor Red
    exit 1
}

# Copy assets to generated folder
$assetsSource = "docs\assets"
$assetsTarget = "$outputDir\html\assets"
if (Test-Path $assetsSource) {
    Copy-Item $assetsSource $assetsTarget -Recurse -Force
    Write-Host "Copied assets to generated folder" -ForegroundColor Cyan
}

# Copy favicon
$faviconSource = "docs\favicon.ico"
$faviconTarget = "$outputDir\html\favicon.ico"
if (Test-Path $faviconSource) {
    Copy-Item $faviconSource $faviconTarget -Force
    Write-Host "Copied favicon to generated folder" -ForegroundColor Cyan
}

$htmlFile = "$outputDir\html\cv__main.html"
if (Test-Path $htmlFile) {
    Write-Host "HTML CV generated successfully: $htmlFile" -ForegroundColor Green
} else {
    Write-Host "Warning: Expected HTML file not found. Check Doxygen output." -ForegroundColor Yellow
    # List generated files
    Get-ChildItem "$outputDir\html\*.html" | ForEach-Object {
        Write-Host "Generated: $($_.Name)" -ForegroundColor Gray
    }
}

# Generate PDF if not skipped
if (-not $SkipPdf) {
    Write-Host "Generating PDF..." -ForegroundColor Cyan
    
    # Check for Python and required packages
    try {
        python --version 2>$null | Out-Null
    } catch {
        Write-Host "Error: Python not found. Please install Python first." -ForegroundColor Red
        exit 1
    }
    
    # Install required packages if not present
    Write-Host "Checking Python dependencies..." -ForegroundColor Cyan
    pip install weasyprint 2>$null
    
    # Create PDF generation script
    $pdfScript = @"
import weasyprint
import os
import sys
from pathlib import Path

html_file = r"$((Get-Item $htmlFile).FullName)"
pdf_file = r"$(Join-Path (Get-Location) "build\LePhucDuc_CV.pdf")"

# Create build directory if it doesn't exist
Path(pdf_file).parent.mkdir(exist_ok=True)

try:
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate PDF
    css_style = '''
    @page {
        size: A4;
        margin: 1cm;
    }
    body {
        font-family: 'Roboto', Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.4;
    }
    #banner {
        display: none;
    }
    .contents {
        box-shadow: none;
        margin: 0;
        padding: 0;
    }
    h1 { font-size: 18pt; }
    h2 { font-size: 14pt; }
    h3 { font-size: 12pt; }
    h4 { font-size: 11pt; }
    '''
    
    html_doc = weasyprint.HTML(string=html_content, base_url=os.path.dirname(html_file))
    css_doc = weasyprint.CSS(string=css_style)
    
    html_doc.write_pdf(pdf_file, stylesheets=[css_doc])
    print(f"PDF generated successfully: {pdf_file}")
    
except Exception as e:
    print(f"Error generating PDF: {e}")
    sys.exit(1)
"@
    
    $pdfScript | Out-File -FilePath "temp_pdf_gen.py" -Encoding utf8
    
    try {
        python temp_pdf_gen.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PDF generated successfully!" -ForegroundColor Green
        } else {
            Write-Host "Warning: PDF generation failed. HTML version is still available." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Warning: Could not generate PDF. Please install weasyprint: pip install weasyprint" -ForegroundColor Yellow
    } finally {
        # Clean up temporary script
        if (Test-Path "temp_pdf_gen.py") {
            Remove-Item "temp_pdf_gen.py" -Force
        }
    }
}

Write-Host "`nBuild completed!" -ForegroundColor Green
Write-Host "HTML CV: $htmlFile" -ForegroundColor Cyan
if (Test-Path "build\LePhucDuc_CV.pdf") {
    Write-Host "PDF CV: build\LePhucDuc_CV.pdf" -ForegroundColor Cyan
}

# Open result if requested
if ($OpenResult) {
    if (Test-Path $htmlFile) {
        Start-Process $htmlFile
    }
}

Write-Host "`nTo rebuild, run: .\build-cv.ps1" -ForegroundColor Gray
Write-Host "To open HTML result: .\build-cv.ps1 -OpenResult" -ForegroundColor Gray
Write-Host "To skip PDF generation: .\build-cv.ps1 -SkipPdf" -ForegroundColor Gray

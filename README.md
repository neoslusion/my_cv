# CV Generator - Le Phuc Duc

This project generates a professional CV in multiple formats: **PDF** (via Doxygen/LaTeX) and **HTML** (responsive web CV). 

## Primary Version: Automotive & SDV Specialist
The system is centralized around the **Automotive & SDV Specialist** profile, highlighting senior experience in Embedded Systems, AUTOSAR, ASPICE, and Software-Defined Vehicles.

- **Web CV**: [index.html](https://neoslusion.github.io/my_cv/)
- **PDF CV**: `LePhucDuc_CV_Automotive.pdf`

## Project Structure

- `docs/LePhucDuc_CV.dox`: The single source of truth for all CV content.
- `docs/index.html`: The web template updated dynamically from the DOX source.
- `tool/update_html_from_dox.py`: Python script to sync content from DOX to HTML.
- `build_cv.sh`: Simple script to generate the PDF locally.

## Local Usage

To build the PDF:
```bash
./build_cv.sh
```

To update the HTML:
```bash
python3 tool/update_html_from_dox.py
```

## Automated Deployment
Every push to the `main` branch triggers a GitHub Action that rebuilds the PDF, updates the HTML, and deploys to GitHub Pages and the repository's Releases.

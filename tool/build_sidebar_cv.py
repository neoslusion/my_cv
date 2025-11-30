#!/usr/bin/env python3
"""Build a sidebar-style PDF CV from the DOX file.

This script:
1. Parses docs/LePhucDuc_CV.dox
2. Fills in the LaTeX template
3. Compiles to PDF using pdflatex

Output: LePhucDuc_CV_Sidebar.pdf
"""

import re
import subprocess
import shutil
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOX_FILE = REPO_ROOT / 'docs' / 'LePhucDuc_CV.dox'
TEMPLATE_FILE = REPO_ROOT / 'build_environment' / 'tool' / 'sidebar_cv' / 'sidebar_cv_template.tex'
OUTPUT_PDF = REPO_ROOT / 'LePhucDuc_CV_Sidebar.pdf'

# Regex patterns
SECTION_PATTERN = re.compile(r'@section\s+(\w+)\s+[^\n]+\n(.*?)(?=@section|\*/)', re.DOTALL)


def extract_sections(text: str) -> dict:
    """Extract sections from DOX file."""
    sections = {}
    for name, body in SECTION_PATTERN.findall(text):
        sections[name.strip()] = body.strip()
    return sections


def extract_name(text: str) -> str:
    """Extract name from @mainpage."""
    match = re.search(r'@mainpage\s+(.+?)(?:\n|$)', text)
    return match.group(1).strip() if match else 'Name'


def extract_contact(text: str) -> str:
    """Extract contact info and format for LaTeX sidebar."""
    match = re.search(r'@mainpage\s+[^\n]+\n\n([^\n]+)', text)
    if not match:
        return ''
    
    raw = match.group(1).strip()
    parts = [p.strip() for p in raw.split('|') if p.strip()]
    
    lines = []
    for p in parts:
        if '@' in p and 'linkedin' not in p.lower() and 'github' not in p.lower():
            # Email
            lines.append(f'\\contactitem{{envelope}}{{{p}}}')
        elif re.search(r'\(\+?\d', p):
            # Phone
            lines.append(f'\\contactitem{{phone}}{{{p}}}')
        elif 'linkedin' in p.lower():
            url = re.search(r'\((https?://[^)]+)\)', p)
            if url:
                lines.append(f'\\contactitem{{linkedin}}{{\\href{{{url.group(1)}}}{{LinkedIn}}}}')
        elif 'github' in p.lower():
            url = re.search(r'\((https?://[^)]+)\)', p)
            if url:
                lines.append(f'\\contactitem{{github}}{{\\href{{{url.group(1)}}}{{GitHub}}}}')
        else:
            # Location
            lines.append(f'\\contactitem{{map-marker-alt}}{{{p}}}')
    
    return '\n'.join(lines)


def extract_summary(text: str) -> str:
    """Extract professional summary."""
    sections = extract_sections(text)
    if 'summary' in sections:
        # Remove the section header formatting, keep just the text
        summary = sections['summary']
        # Remove any remaining doxygen markup
        summary = re.sub(r'@\w+\s*', '', summary)
        summary = summary.strip()
        return escape_latex(summary)
    return ''


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    # Order matters - & must come first
    replacements = [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def build_skills(raw: str) -> str:
    """Build skills section for LaTeX sidebar."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    
    # Icon mapping for skill categories
    icon_map = {
        'Programming Languages': 'code',
        'Automotive Standards': 'car',
        'Tools & Platforms': 'tools',
        'DevOps': 'server',
        'Methodologies': 'project-diagram',
        'Soft Skills': 'users',
    }
    
    blocks = []
    for ln in lines:
        ln = re.sub(r'^-\s*', '', ln)
        m = re.match(r'<b>([^<]+)</b>:\s*(.*)', ln)
        if m:
            cat, vals = m.groups()
            cat = cat.strip()
            icon = icon_map.get(cat, 'check')
            vals_list = [v.strip() for v in re.split(r',\s*(?![^()]*\))', vals) if v.strip()]
            
            block = f'\\skillcategory{{{icon}}}{{{escape_latex(cat)}}}\n'
            tags = ' '.join([f'\\skilltag{{{escape_latex(v)}}}' for v in vals_list])
            block += tags + '\n\\vspace{0.4em}\n'
            blocks.append(block)
    
    return '\n'.join(blocks)


def build_certifications(raw: str) -> str:
    """Build certifications for LaTeX sidebar."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    
    items = []
    for ln in lines:
        ln = re.sub(r'^-\s*', '', ln)
        # Remove "(Bosch Internal)" or similar
        ln = re.sub(r'\s*\([^)]*Internal[^)]*\)', '', ln)
        items.append(f'\\textcolor{{accentcolor}}{{\\faIcon{{certificate}}}} \\textcolor{{textlight}}{{\\small {escape_latex(ln)}}}\\\\[0.2em]')
    
    return '\n'.join(items)


def build_languages(raw: str) -> str:
    """Build languages for LaTeX sidebar."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    
    items = []
    for ln in lines:
        ln = re.sub(r'^-\s*', '', ln)
        # Parse <b>Language</b>: Level
        m = re.match(r'<b>([^<]+)</b>:\s*(.*)', ln)
        if m:
            lang, level = m.groups()
            items.append(f'\\textcolor{{accentcolor}}{{\\faIcon{{language}}}} \\textbf{{\\textcolor{{textlight}}{{{escape_latex(lang.strip())}}}}} \\textcolor{{textlight}}{{\\small {escape_latex(level.strip())}}}\\\\[0.2em]')
    
    return '\n'.join(items)


def build_experience(raw: str) -> str:
    """Build work experience for LaTeX main content."""
    # Get company info
    company_match = re.search(r'@subsection\s+\w+\s+(.+?)(?=\n)', raw)
    company = company_match.group(1).strip() if company_match else 'Company'
    
    # Split by @subsubsection for positions
    positions = re.split(r'@subsubsection\s+\w+\s+', raw)
    positions = [p.strip() for p in positions[1:] if p.strip()]
    
    entries = []
    for i, pos in enumerate(positions):
        lines = pos.splitlines()
        if not lines:
            continue
        
        # Parse title and dates
        title_line = lines[0].strip()
        title_match = re.match(r'(.+?)\s*\|\s*(.+)', title_line)
        if title_match:
            position_title, dates = title_match.groups()
        else:
            position_title, dates = title_line, ''
        
        # Build content
        content_lines = lines[1:]
        content_parts = []
        current_list = []
        current_header = None
        
        for line in content_lines:
            line = line.rstrip()
            if not line or line.strip() == '---':
                continue
            
            stripped = line.strip()
            
            # Check for headers like <b>Customer:</b>
            header_match = re.match(r'^<b>([^<]+):</b>\s*(.*)', stripped)
            if header_match:
                # Save previous list
                if current_list:
                    content_parts.append('\\begin{itemize}')
                    content_parts.extend([f'\\item {escape_latex(item)}' for item in current_list])
                    content_parts.append('\\end{itemize}')
                    current_list = []
                
                header_name = header_match.group(1).strip()
                header_value = header_match.group(2).strip()
                
                if header_name in ['Customer', 'Product']:
                    content_parts.append(f'\\textbf{{{header_name}:}} {escape_latex(header_value)}\\\\')
                elif header_name in ['Responsibilities', 'Achievements']:
                    current_header = header_name
                else:
                    content_parts.append(f'\\textbf{{{escape_latex(header_name)}:}}\\\\')
            elif stripped.startswith('- '):
                # List item
                item_text = stripped[2:].strip()
                # Check for category header in list
                cat_match = re.match(r'<b>([^<]+):</b>\s*(.*)', item_text)
                if cat_match:
                    if current_list:
                        content_parts.append('\\begin{itemize}')
                        content_parts.extend([f'\\item {escape_latex(item)}' for item in current_list])
                        content_parts.append('\\end{itemize}')
                        current_list = []
                    content_parts.append(f'\\textbf{{{escape_latex(cat_match.group(1))}:}}')
                    if cat_match.group(2):
                        content_parts.append(f' {escape_latex(cat_match.group(2))}')
                    content_parts.append('\\\\')
                else:
                    # Handle bold items within achievements
                    item_text = re.sub(r'<b>([^<]+)</b>', r'\\textbf{\1}', item_text)
                    current_list.append(item_text)
            elif line.startswith('  - '):
                # Sub-list item
                item_text = stripped[2:].strip()
                item_text = re.sub(r'<b>([^<]+)</b>', r'\\textbf{\1}', item_text)
                current_list.append(item_text)
        
        # Save remaining list
        if current_list:
            content_parts.append('\\begin{itemize}')
            content_parts.extend([f'\\item {escape_latex(item)}' for item in current_list])
            content_parts.append('\\end{itemize}')
        
        # Build entry
        if i == 0:
            entry = f'\\experienceentry{{{escape_latex(company)}}}{{{escape_latex(position_title.strip())}}}{{{escape_latex(dates.strip())}}}{{\n'
        else:
            entry = f'\\experienceentry{{}}{{{escape_latex(position_title.strip())}}}{{{escape_latex(dates.strip())}}}{{\n'
        
        entry += '\n'.join(content_parts)
        entry += '\n}'
        entries.append(entry)
    
    return '\n\n'.join(entries)


def build_education(raw: str) -> str:
    """Build education for LaTeX main content."""
    parts = re.split(r'@subsection\s+\w+\s+', raw)
    parts = [p.strip() for p in parts if p.strip()]
    
    entries = []
    for part in parts:
        lines = [l.strip() for l in part.splitlines() if l.strip() and not l.strip().startswith('---')]
        if not lines:
            continue
        
        university = lines[0]
        degree_line = ''
        gpa_line = ''
        
        for line in lines[1:]:
            if '<b>' in line and '<em>' in line:
                degree_line = line
            elif line.startswith('GPA:'):
                gpa_line = line
        
        if degree_line:
            degree_match = re.search(r'<b>([^<]+)</b>\s*\|\s*<em>([^<]+)</em>', degree_line)
            if degree_match:
                degree, dates = degree_match.groups()
                entry = f'\\educationentry{{{escape_latex(university)}}}{{{escape_latex(degree.strip())}}}{{{escape_latex(dates.strip())}}}{{{escape_latex(gpa_line)}}}'
                entries.append(entry)
    
    return '\n\n'.join(entries)


def main():
    if not DOX_FILE.exists():
        print(f'Error: DOX file not found: {DOX_FILE}')
        return 1
    
    if not TEMPLATE_FILE.exists():
        print(f'Error: Template file not found: {TEMPLATE_FILE}')
        return 1
    
    print(f'Reading DOX file: {DOX_FILE}')
    dox_text = DOX_FILE.read_text(encoding='utf-8')
    sections = extract_sections(dox_text)
    
    print('Parsing content...')
    
    # Extract all content
    name = extract_name(dox_text)
    contact = extract_contact(dox_text)
    summary = extract_summary(dox_text)
    skills = build_skills(sections.get('skills', ''))
    certifications = build_certifications(sections.get('certifications', ''))
    languages = build_languages(sections.get('languages', ''))
    experience = build_experience(sections.get('work_experience', ''))
    education = build_education(sections.get('education', ''))
    
    print('Building LaTeX document...')
    
    # Read template
    template = TEMPLATE_FILE.read_text(encoding='utf-8')
    
    # Replace placeholders
    latex = template.replace('@@NAME@@', name)
    latex = latex.replace('@@CONTACT@@', contact)
    latex = latex.replace('@@SUMMARY@@', summary)
    latex = latex.replace('@@SKILLS@@', skills)
    latex = latex.replace('@@CERTIFICATIONS@@', certifications)
    latex = latex.replace('@@LANGUAGES@@', languages)
    latex = latex.replace('@@EXPERIENCE@@', experience)
    latex = latex.replace('@@EDUCATION@@', education)
    
    # Create temp directory for compilation
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tex_file = tmpdir / 'cv.tex'
        tex_file.write_text(latex, encoding='utf-8')
        
        print('Compiling PDF (this may take a moment)...')
        
        # Run pdflatex twice for proper layout
        for i in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'cv.tex'],
                cwd=tmpdir,
                capture_output=True,
            )
            if result.returncode != 0:
                print(f'LaTeX compilation failed (pass {i+1}):')
                # Decode with error handling for non-UTF8 output
                stdout = result.stdout.decode('utf-8', errors='replace')
                print(stdout[-2000:] if len(stdout) > 2000 else stdout)
                # Save log for debugging
                log_file = tmpdir / 'cv.log'
                if log_file.exists():
                    print('\n--- Last 50 lines of log ---')
                    log_lines = log_file.read_text(encoding='utf-8', errors='replace').splitlines()
                    print('\n'.join(log_lines[-50:]))
                return 1
        
        # Copy output
        pdf_file = tmpdir / 'cv.pdf'
        if pdf_file.exists():
            shutil.copy(pdf_file, OUTPUT_PDF)
            print(f'Success! Created: {OUTPUT_PDF}')
        else:
            print('Error: PDF was not generated')
            return 1
    
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

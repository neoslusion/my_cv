#!/usr/bin/env python3
"""Update docs/index.html placeholders from docs/LePhucDuc_CV.dox.

Markers in HTML:
  <!-- CONTACT_INFO_START --> ... <!-- CONTACT_INFO_END -->
  <!-- SKILLS_START --> ... <!-- SKILLS_END -->
  <!-- EDUCATION_START --> ... <!-- EDUCATION_END -->
  <!-- WORK_EXPERIENCE_START --> ... <!-- WORK_EXPERIENCE_END -->

Parses the DOX file which uses Doxygen format with <b>, <em> HTML tags.
"""
import re
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DOX_FILE = REPO_ROOT / 'docs' / 'LePhucDuc_CV.dox'
HTML_FILE = REPO_ROOT / 'docs' / 'index.html'

SECTION_PATTERN = re.compile(r'@section\s+(\w+)\s+[^\n]+\n(.*?)(?=@section|\*/)', re.DOTALL)

MARKERS = {
    'contact_info': ('<!-- CONTACT_INFO_START -->', '<!-- CONTACT_INFO_END -->'),
    'summary': ('<!-- SUMMARY_START -->', '<!-- SUMMARY_END -->'),
    'skills': ('<!-- SKILLS_START -->', '<!-- SKILLS_END -->'),
    'certifications': ('<!-- CERTIFICATIONS_START -->', '<!-- CERTIFICATIONS_END -->'),
    'languages': ('<!-- LANGUAGES_START -->', '<!-- LANGUAGES_END -->'),
    'education': ('<!-- EDUCATION_START -->', '<!-- EDUCATION_END -->'),
    'work_experience': ('<!-- WORK_EXPERIENCE_START -->', '<!-- WORK_EXPERIENCE_END -->'),
}

# Badge colors for different skill categories
SKILL_BADGE_COLORS = {
    'Programming Languages': 'primary',
    'Automotive Standards': 'primary',
    'Tools & Platforms': 'secondary',
    'DevOps': 'info',
    'Methodologies': 'success',
    'Soft Skills': 'warning',
}


def extract_sections(text: str):
    sections = {}
    for name, body in SECTION_PATTERN.findall(text):
        sections[name.strip()] = body.strip().strip('\n')
    return sections


def extract_contact_from_mainpage(text: str) -> str:
    """Extract contact info from @mainpage header line."""
    match = re.search(r'@mainpage\s+[^\n]+\n\n([^\n]+)', text)
    if match:
        return match.group(1).strip()
    return ''


def build_contact_info(raw: str) -> str:
    """Build contact info HTML from pipe-separated line."""
    parts = [p.strip() for p in raw.split('|') if p.strip()]
    items = []
    for p in parts:
        if re.search(r'@', p):  # email
            items.append('<li class="mb-2"><i class="fas fa-envelope-square fa-fw fa-lg mr-2"></i><a class="resume-link" href="mailto:{0}">{0}</a></li>'.format(p))
        elif re.search(r'linkedin', p, re.I):
            url = re.sub(r'^\[LinkedIn\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fab fa-linkedin fa-fw fa-lg mr-2"></i><a class="resume-link" href="{0}" target="_blank">LinkedIn</a></li>'.format(url))
        elif 'GitHub' in p or 'github' in p:
            url = re.sub(r'^\[GitHub\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fab fa-github fa-fw fa-lg mr-2"></i><a class="resume-link" href="{0}" target="_blank">GitHub</a></li>'.format(url))
        elif 'Online CV' in p:
            url = re.sub(r'^\[Online CV\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fas fa-external-link-alt fa-fw fa-lg mr-2"></i><a class="resume-link" href="{0}" target="_blank">Online CV</a></li>'.format(url))
        elif re.search(r'\(\+?\d', p):  # phone
            phone_digits = re.sub(r'[^0-9+]', '', p)
            items.append('<li class="mb-2"><i class="fas fa-phone-square fa-fw fa-lg mr-2"></i><a class="resume-link" href="tel:{0}">{1}</a></li>'.format(phone_digits, p))
        else:  # location
            items.append('<li class="mb-0"><i class="fas fa-map-marker-alt fa-fw fa-lg mr-2"></i>{0}</li>'.format(p))
    # Sort: phone, email, linkedin, github, location last
    order = {'fa-phone-square': 0, 'fa-envelope-square': 1, 'fa-linkedin': 2, 'fa-github': 3, 'fa-external-link-alt': 4, 'fa-map-marker-alt': 5}
    items.sort(key=lambda x: next((v for k, v in order.items() if k in x), 99))
    return '\n'.join(items)


def split_skills(vals: str) -> list:
    """Split skill values by comma, but not inside parentheses."""
    result = []
    current = ''
    paren_depth = 0
    for char in vals:
        if char == '(':
            paren_depth += 1
            current += char
        elif char == ')':
            paren_depth -= 1
            current += char
        elif char == ',' and paren_depth == 0:
            if current.strip():
                result.append(current.strip())
            current = ''
        else:
            current += char
    if current.strip():
        result.append(current.strip())
    return result


def build_skills(raw: str) -> str:
    """Build skills HTML from DOX format with <b>Category</b>: items."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    blocks = []
    for ln in lines:
        # Remove leading dash and parse <b>Category</b>: items
        ln = re.sub(r'^-\s*', '', ln)
        m = re.match(r'<b>([^<]+)</b>:\s*(.*)', ln)
        if m:
            cat, vals = m.groups()
            cat = cat.strip()
            badge_color = SKILL_BADGE_COLORS.get(cat, 'primary')
            vals_list = split_skills(vals)
            vals_html = '\n\t\t'.join([f'<span class="badge badge-{badge_color} mr-1 mb-1">{v}</span>' for v in vals_list])
            blocks.append(f'''<div class="item mb-3">
\t<h4 class="item-title">{cat}</h4>
\t<div class="item-content">
\t\t{vals_html}
\t</div>
</div>''')
    if not blocks:
        return f'<div class="item"><em>{raw}</em></div>'
    return '\n'.join(blocks)


def build_summary(raw: str) -> str:
    """Build summary HTML from DOX format - just extract the paragraph text."""
    # Remove any leading/trailing whitespace and return as paragraph
    text = raw.strip()
    return f'<p class="mb-0">{text}</p>'


def build_certifications(raw: str) -> str:
    """Build certifications HTML from DOX format with list items."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    items = []
    for ln in lines:
        # Remove leading dash
        cert = re.sub(r'^-\s*', '', ln).strip()
        items.append(f'<li class="mb-2"><i class="fas fa-certificate mr-2 text-primary"></i>{cert}</li>')
    return '\n'.join(items) if items else '<li>No certifications listed</li>'


def build_languages(raw: str) -> str:
    """Build languages HTML from DOX format with <b>Language</b>: Level."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    items = []
    for ln in lines:
        # Remove leading dash and parse <b>Language</b>: Level
        ln = re.sub(r'^-\s*', '', ln)
        m = re.match(r'<b>([^<]+)</b>:\s*(.*)', ln)
        if m:
            lang, level = m.groups()
            items.append(f'<li class="mb-2"><strong>{lang.strip()}:</strong> {level.strip()}</li>')
        else:
            items.append(f'<li class="mb-2">{ln}</li>')
    return '\n'.join(items) if items else '<li>No languages listed</li>'


def build_education(raw: str) -> str:
    """Build education HTML from DOX format with @subsection."""
    # Split by @subsection
    parts = re.split(r'@subsection\s+\w+\s+', raw)
    parts = [p.strip() for p in parts if p.strip()]
    
    items = []
    for part in parts:
        lines = [l.strip() for l in part.splitlines() if l.strip() and not l.strip().startswith('---')]
        if not lines:
            continue
        
        # First line is university name
        university = lines[0]
        
        # Find degree line with <b> and <em>
        degree_line = ''
        gpa_line = ''
        for line in lines[1:]:
            if '<b>' in line and '<em>' in line:
                degree_line = line
            elif line.startswith('GPA:'):
                gpa_line = line
        
        if degree_line:
            # Extract degree and dates
            degree_match = re.search(r'<b>([^<]+)</b>\s*\|\s*<em>([^<]+)</em>', degree_line)
            if degree_match:
                degree, dates = degree_match.groups()
                item_html = f'''<li class="mb-3">
\t<h4 class="mb-1">{university}</h4>
\t<strong>{degree.strip()}</strong> | <em>{dates.strip()}</em><br>
\t{gpa_line}
</li>'''
                items.append(item_html)
    
    return '<ul class="list-unstyled resume-education-list">\n' + '\n'.join(items) + '\n</ul>'


def build_work(raw: str) -> str:
    """Build work experience HTML from DOX format with @subsection and @subsubsection."""
    # First, get the company info from @subsection
    company_match = re.search(r'@subsection\s+\w+\s+(.+?)(?=\n)', raw)
    company = company_match.group(1).strip() if company_match else 'Company'
    
    # Split by @subsubsection for each position
    positions = re.split(r'@subsubsection\s+\w+\s+', raw)
    positions = [p.strip() for p in positions[1:] if p.strip()]  # Skip first empty part
    
    divs = []
    for i, pos in enumerate(positions):
        lines = pos.splitlines()
        if not lines:
            continue
        
        # First line has position title and dates
        title_line = lines[0].strip()
        # Parse "Software Engineer | Feb 2024 - Present"
        title_match = re.match(r'(.+?)\s*\|\s*(.+)', title_line)
        if title_match:
            position_title, dates = title_match.groups()
        else:
            position_title, dates = title_line, ''
        
        # Rest of the content
        content_lines = lines[1:]
        
        # Parse the content into sections
        sections = []
        current_section = None
        current_items = []
        
        for line in content_lines:
            line = line.rstrip()
            if not line or line.strip() == '---':
                continue
            
            stripped = line.strip()
            
            # Check for section header like <b>Customer:</b> or <b>Responsibilities:</b>
            header_match = re.match(r'^<b>([^<]+):</b>\s*(.*)', stripped)
            if header_match:
                # Save previous section
                if current_section:
                    sections.append((current_section, current_items))
                current_section = header_match.group(1).strip()
                remaining = header_match.group(2).strip()
                current_items = [remaining] if remaining else []
            elif stripped.startswith('- '):
                # List item (top level or nested)
                if line.startswith('  - ') or line.startswith('  -'):
                    # Nested item (sub-bullet)
                    item_text = re.sub(r'^\s*-\s*', '', stripped)
                    current_items.append(('sub', item_text))
                else:
                    # Top level item - could be a category header
                    item_text = re.sub(r'^-\s*', '', stripped)
                    # Check if it's a category header like <b>Category:</b> (with nothing after or only sub-items following)
                    cat_match = re.match(r'<b>([^<]+):</b>\s*(.*)', item_text)
                    if cat_match:
                        cat_name = cat_match.group(1).strip()
                        cat_rest = cat_match.group(2).strip()
                        if cat_rest:
                            # This is a bold-prefixed item (like an achievement with description)
                            current_items.append(('bold_item', cat_name, cat_rest))
                        else:
                            # This is a category header (only bold text, sub-items follow)
                            current_items.append(('category', cat_name))
                    else:
                        current_items.append(('item', item_text))
            else:
                # Plain text line
                if current_items or not current_section:
                    current_items.append(('text', stripped))
        
        # Save last section
        if current_section:
            sections.append((current_section, current_items))
        
        # Build HTML for this position
        html_parts = []
        
        # Add company header only for first position
        if i == 0:
            html_parts.append(f'<div class="item mb-4">')
            html_parts.append(f'\t<h4 class="resume-position-title font-weight-bold mb-1">{company}</h4>')
        else:
            html_parts.append(f'<div class="item mb-3">')
        
        html_parts.append(f'\t')
        html_parts.append(f'\t<div class="resume-position-time text-muted mb-2">{position_title.strip()} | <em>{dates.strip()}</em></div>')
        
        # Process each section
        for section_name, items in sections:
            if section_name == 'Customer':
                # Simple paragraph
                value = items[0] if items else ''
                html_parts.append(f'\t<p><strong>Customer:</strong> {value}</p>')
            elif section_name == 'Product':
                value = items[0] if items else ''
                html_parts.append(f'\t<p><strong>Product:</strong> {value}</p>')
            elif section_name == 'Responsibilities':
                # This section has categories with sub-bullets
                current_category = None
                for item in items:
                    if item[0] == 'category':
                        # Close previous list if any
                        if current_category:
                            html_parts.append('\t</ul>')
                        html_parts.append(f'\t')
                        html_parts.append(f'\t<p class="mb-2"><strong>{item[1]}:</strong></p>')
                        html_parts.append('\t<ul class="resume-list">')
                        current_category = item[1]
                    elif item[0] == 'sub':
                        html_parts.append(f'\t\t<li>{item[1]}</li>')
                if current_category:
                    html_parts.append('\t</ul>')
            elif section_name == 'Achievements':
                html_parts.append(f'\t')
                html_parts.append(f'\t<p class="mb-2"><strong>Achievements:</strong></p>')
                html_parts.append('\t<ul class="resume-list">')
                for item in items:
                    if item[0] == 'bold_item':
                        # Bold-prefixed item like "Top Performer Award (2024): description"
                        text = f'<strong>{item[1]}:</strong> {item[2]}'
                        html_parts.append(f'\t\t<li>{text}</li>')
                    elif item[0] == 'item':
                        # Regular item - convert <b> to <strong>
                        text = re.sub(r'<b>([^<]+)</b>', r'<strong>\1</strong>', item[1])
                        html_parts.append(f'\t\t<li>{text}</li>')
                html_parts.append('\t</ul>')
        
        html_parts.append('</div>')
        divs.append('\n'.join(html_parts))
    
    return '\n\n'.join(divs) if divs else '<div class="item mb-3"><em>No work experience parsed.</em></div>'


def replace_block(html: str, start: str, end: str, new_inner: str) -> str:
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.DOTALL)
    replacement = f'{start}\n{new_inner}\n{end}'
    if not pattern.search(html):
        print(f'Warning: markers {start}..{end} not found', file=sys.stderr)
        return html
    return pattern.sub(replacement, html, count=1)


def main():
    if not DOX_FILE.exists():
        print('DOX file not found', file=sys.stderr)
        return 1
    if not HTML_FILE.exists():
        print('HTML file not found', file=sys.stderr)
        return 1
    
    dox_text = DOX_FILE.read_text(encoding='utf-8')
    sections = extract_sections(dox_text)
    html = HTML_FILE.read_text(encoding='utf-8')

    # Contact info (from mainpage header)
    contact_raw = extract_contact_from_mainpage(dox_text)
    if contact_raw:
        html = replace_block(html, *MARKERS['contact_info'], build_contact_info(contact_raw))
    
    # Professional Summary
    if 'summary' in sections:
        html = replace_block(html, *MARKERS['summary'], build_summary(sections['summary']))
    
    # Skills
    if 'skills' in sections:
        html = replace_block(html, *MARKERS['skills'], build_skills(sections['skills']))
    
    # Certifications
    if 'certifications' in sections:
        html = replace_block(html, *MARKERS['certifications'], build_certifications(sections['certifications']))
    
    # Languages
    if 'languages' in sections:
        html = replace_block(html, *MARKERS['languages'], build_languages(sections['languages']))
    
    # Education
    if 'education' in sections:
        html = replace_block(html, *MARKERS['education'], build_education(sections['education']))
    
    # Work Experience
    if 'work_experience' in sections:
        html = replace_block(html, *MARKERS['work_experience'], build_work(sections['work_experience']))

    HTML_FILE.write_text(html + ('\n' if not html.endswith('\n') else ''), encoding='utf-8')
    print('index.html updated from DOX.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

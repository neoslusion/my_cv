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


def strip_internal_tags(text: str) -> str:
    """Remove @internal and @endinternal tags (but keep content) from text."""
    text = re.sub(r'@internal\b\s*', '', text)
    text = re.sub(r'@endinternal\b\s*', '', text)
    return text


def extract_sections(text: str):
    """Extract sections, cleaning up @internal/@endinternal tags from content."""
    sections = {}
    for name, body in SECTION_PATTERN.findall(text):
        # Clean up any @internal/@endinternal tags from the body content
        clean_body = strip_internal_tags(body.strip().strip('\n'))
        sections[name.strip()] = clean_body
    return sections


def extract_contact_from_mainpage(text: str) -> str:
    """Extract contact info from @mainpage header line."""
    match = re.search(r'@mainpage\s+[^\n]+\n\n([^\n]+)', text)
    if match:
        return match.group(1).strip()
    return ''


def build_contact_info(raw: str) -> str:
    """Build contact info HTML from pipe-separated line."""
    # Strip HTML tags like <center>, </center> from the raw string
    raw = re.sub(r'<[^>]+>', '', raw)
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
    # Remove any leading/trailing whitespace and horizontal rules
    text = raw.strip()
    text = re.sub(r'\n*---\n*', '', text)  # Remove horizontal rules
    text = text.strip()
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
    """Build education HTML from DOX format with inline HTML tags and @fill.
    
    The DOX format uses:
    - <b>University</b> @fill <em>Location</em> for university header (no digits in location)
    - <b>Degree</b> @fill <em>Dates</em> for each degree (has digits like 2024)
    - - GPA: X/Y for GPA info
    """
    lines = raw.strip().splitlines()
    
    # State tracking
    university_name = ''
    university_location = ''
    degrees = []  # List of (degree, dates, gpa)
    current_degree = None
    current_dates = None
    current_gpa = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue
        
        # Check for <b>...</b> @fill <em>...</em> pattern
        match = re.match(r'^<b>([^<]+)</b>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if match:
            left_part = match.group(1).strip()
            right_part = match.group(2).strip()
            
            # If right part contains digits, it's a degree line (dates like "2024 – Present")
            # Otherwise it's the university line (location like "Ho Chi Minh City")
            if re.search(r'\d', right_part):
                # This is a degree line
                if current_degree:
                    degrees.append((current_degree, current_dates, current_gpa))
                current_degree = left_part
                current_dates = right_part
                current_gpa = None
            else:
                # This is the university line
                university_name = left_part
                university_location = right_part
            continue
        
        # Check for GPA line: - GPA: X/Y
        if stripped.startswith('- '):
            gpa_text = stripped[2:].strip()
            if gpa_text.startswith('GPA:'):
                current_gpa = gpa_text
    
    # Save last degree
    if current_degree:
        degrees.append((current_degree, current_dates, current_gpa))
    
    # Build HTML
    if not degrees:
        return '<ul class="list-unstyled resume-education-list">\n<li>No education info</li>\n</ul>'
    
    degree_entries = []
    for degree, dates, gpa in degrees:
        entry = f'\t<div class="d-flex justify-content-between mb-2"><strong>{degree}</strong><em class="text-muted">{dates}</em></div>'
        if gpa:
            entry += f'\n\t<p class="mb-3 ml-2">{gpa}</p>'
        degree_entries.append(entry)
    
    item_html = f'''<li class="mb-4">
\t<h4 class="mb-3">{university_name}, {university_location}</h4>
{chr(10).join(degree_entries)}
</li>'''
    
    return '<ul class="list-unstyled resume-education-list">\n' + item_html + '\n</ul>'


def build_work(raw: str) -> str:
    """Build work experience HTML from DOX format with inline HTML tags and @fill.
    
    The DOX format uses:
    - <b>Company</b> @fill <em>Location</em> for company header
    - <b>Position</b> for position title
    - <i>Customer: X - Product: Y</i> @fill <em>Dates</em> for project info
    - <b>Responsibilities:</b> / <b>Achievements:</b> for sections
    - Nested bullet points for details
    """
    lines = raw.strip().splitlines()
    
    # State tracking
    company_name = ''
    company_location = ''
    current_position = ''
    projects = []  # List of project dicts
    current_project = None
    current_section = None  # 'Responsibilities' or 'Achievements'
    current_category = None  # e.g., 'Software Development with SaaP'
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue
        
        # Check for company line: <b>Company</b> @fill <em>Location</em>
        company_match = re.match(r'^<b>([^<]+)</b>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if company_match:
            company_name = company_match.group(1).strip()
            company_location = company_match.group(2).strip()
            continue
        
        # Check for position title: <b>Position</b> (standalone)
        position_match = re.match(r'^<b>([^<]+)</b>$', stripped)
        if position_match and 'Responsibilities' not in stripped and 'Achievements' not in stripped:
            current_position = position_match.group(1).strip()
            continue
        
        # Check for project line: <i>Customer: X - Product: Y</i> @fill <em>Dates</em>
        project_match = re.match(r'^<i>([^<]+)</i>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if project_match:
            # Save previous project
            if current_project:
                projects.append(current_project)
            current_project = {
                'info': project_match.group(1).strip(),
                'dates': project_match.group(2).strip(),
                'position': current_position,
                'responsibilities': [],
                'achievements': []
            }
            current_section = None
            current_category = None
            continue
        
        # Check for section headers: <b>Responsibilities:</b> or <b>Achievements:</b>
        section_match = re.match(r'^<b>(Responsibilities|Achievements):</b>$', stripped)
        if section_match:
            current_section = section_match.group(1)
            current_category = None
            continue
        
        # Check for category bullet or regular bullet
        if stripped.startswith('- '):
            item_text = re.sub(r'^-\s*', '', stripped)
            
            # Check for category with colon: - <b>Category:</b> (nothing after)
            cat_match_colon = re.match(r'^<b>([^<]+):</b>\s*$', item_text)
            if cat_match_colon and current_section == 'Responsibilities':
                current_category = cat_match_colon.group(1).strip()
                if current_project:
                    current_project['responsibilities'].append(('category', current_category))
                continue
            
            # Check for category WITHOUT colon: - <b>Category</b> (just bold text, no colon inside)
            cat_match_no_colon = re.match(r'^<b>([^<:]+)</b>\s*$', item_text)
            if cat_match_no_colon and current_section == 'Responsibilities':
                current_category = cat_match_no_colon.group(1).strip()
                if current_project:
                    current_project['responsibilities'].append(('category', current_category))
                continue
            
            # Check for bold-prefixed item (achievement with description like "Award: description")
            bold_item_match = re.match(r'^<b>([^<]+):</b>\s*(.+)$', item_text)
            if bold_item_match:
                if current_project and current_section == 'Achievements':
                    current_project['achievements'].append(('bold_item', bold_item_match.group(1).strip(), bold_item_match.group(2).strip()))
                continue
            
            # Regular list item
            if current_project:
                if current_section == 'Responsibilities':
                    # Could be a sub-item if line starts with two spaces
                    if line.startswith('  - ') or line.startswith('  -'):
                        current_project['responsibilities'].append(('sub', item_text))
                    else:
                        current_project['responsibilities'].append(('item', item_text))
                elif current_section == 'Achievements':
                    current_project['achievements'].append(('item', item_text))
            continue
        
        # Check for nested sub-bullet: starts with spaces then -
        if line.startswith('  - ') or line.startswith('  -'):
            sub_text = re.sub(r'^\s*-\s*', '', stripped)
            if current_project and current_section == 'Responsibilities':
                current_project['responsibilities'].append(('sub', sub_text))
    
    # Save last project
    if current_project:
        projects.append(current_project)
    
    # Build HTML
    divs = []
    for i, proj in enumerate(projects):
        html_parts = []
        
        # Add company header only for first project
        if i == 0:
            html_parts.append('<div class="item mb-5">')
            html_parts.append(f'\t<h4 class="resume-position-title font-weight-bold mb-2">{company_name} | {company_location}</h4>')
        else:
            html_parts.append('<div class="item mb-4">')
        
        # Position and dates
        html_parts.append(f'\t<div class="resume-position-time d-flex justify-content-between mb-3"><span class="font-weight-bold">{proj.get("position", "Software Engineer")}</span><em class="text-muted">{proj["dates"]}</em></div>')
        
        # Project info (Customer/Product)
        if proj['info']:
            html_parts.append(f'\t<p class="mb-3"><em>{proj["info"]}</em></p>')
        
        # Responsibilities
        if proj['responsibilities']:
            html_parts.append('\t<p class="mb-2 mt-3"><strong>Responsibilities:</strong></p>')
            current_cat = None
            for item in proj['responsibilities']:
                if item[0] == 'category':
                    if current_cat:
                        html_parts.append('\t</ul>')
                    html_parts.append(f'\t<p class="mb-2 ml-2"><strong>{item[1]}:</strong></p>')
                    html_parts.append('\t<ul class="resume-list mb-3">')
                    current_cat = item[1]
                elif item[0] == 'sub':
                    html_parts.append(f'\t\t<li class="mb-2">{item[1]}</li>')
                elif item[0] == 'item':
                    if not current_cat:
                        html_parts.append('\t<ul class="resume-list mb-3">')
                        current_cat = 'default'
                    html_parts.append(f'\t\t<li class="mb-2">{item[1]}</li>')
            if current_cat:
                html_parts.append('\t</ul>')
        
        # Achievements
        if proj['achievements']:
            html_parts.append('\t<p class="mb-2 mt-3"><strong>Achievements:</strong></p>')
            html_parts.append('\t<ul class="resume-list mb-3">')
            for item in proj['achievements']:
                if item[0] == 'bold_item':
                    text = f'<strong>{item[1]}:</strong> {item[2]}'
                    html_parts.append(f'\t\t<li class="mb-2">{text}</li>')
                elif item[0] == 'item':
                    text = re.sub(r'<b>([^<]+)</b>', r'<strong>\1</strong>', item[1])
                    html_parts.append(f'\t\t<li class="mb-2">{text}</li>')
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

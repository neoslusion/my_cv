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
    - <b>Position</b> @fill <em>Dates</em> for position with dates
    - <i>Customer: X - Product: Y</i> @fill <em>Dates</em> for project info
    - <b>Section Title</b> (standalone) for responsibility sections
    - <b>Achievements:</b> for achievements section
    - Bullet points under sections
    """
    lines = raw.strip().splitlines()
    
    # State tracking
    company_name = ''
    company_location = ''
    position_title = ''
    position_dates = ''
    projects = []  # List of project dicts
    current_project = None
    current_section = None  # 'responsibilities' or 'achievements'
    current_category = None
    global_achievements = []  # Achievements at the end (not per-project)
    in_global_achievements = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue
        
        # Check for company line: <b>Company</b> @fill <em>Location</em>
        # This is distinguished from position line by location not having digits (dates have digits)
        company_match = re.match(r'^<b>([^<]+)</b>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if company_match:
            left_part = company_match.group(1).strip()
            right_part = company_match.group(2).strip()
            # If right part has digits, it's position+dates; otherwise company+location
            if re.search(r'\d', right_part):
                position_title = left_part
                position_dates = right_part
            else:
                company_name = left_part
                company_location = right_part
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
                'sections': [],  # List of (section_name, items)
                'achievements': []
            }
            current_section = 'responsibilities'
            current_category = None
            in_global_achievements = False
            continue
        
        # Check for achievements header: <b>Achievements:</b>
        if stripped == '<b>Achievements:</b>':
            in_global_achievements = True
            current_section = 'achievements'
            continue
        
        # Check for section header (standalone bold): <b>Section Title</b>
        section_header_match = re.match(r'^<b>([^<]+)</b>$', stripped)
        if section_header_match and 'Achievements' not in stripped:
            section_name = section_header_match.group(1).strip()
            if current_project and not in_global_achievements:
                current_project['sections'].append((section_name, []))
                current_category = section_name
            continue
        
        # Check for bullet items
        if stripped.startswith('- '):
            item_text = re.sub(r'^-\s*', '', stripped)
            
            # Check for bold-prefixed item (like "Top Performer Award (2025): description")
            bold_item_match = re.match(r'^<b>([^<]+):</b>\s*(.+)$', item_text)
            if bold_item_match:
                bold_label = bold_item_match.group(1).strip()
                bold_desc = bold_item_match.group(2).strip()
                if in_global_achievements:
                    global_achievements.append(('bold_item', bold_label, bold_desc))
                elif current_project:
                    current_project['achievements'].append(('bold_item', bold_label, bold_desc))
                continue
            
            # Regular bullet item
            if in_global_achievements:
                global_achievements.append(('item', item_text))
            elif current_project:
                if current_category and current_project['sections']:
                    # Add to current section
                    current_project['sections'][-1][1].append(item_text)
                else:
                    # Add to general items (no section header)
                    if not current_project['sections']:
                        current_project['sections'].append((None, []))
                    current_project['sections'][-1][1].append(item_text)
            continue
    
    # Save last project
    if current_project:
        projects.append(current_project)
    
    # Build HTML
    html_parts = []
    
    # Company header
    html_parts.append('<div class="item mb-5">')
    html_parts.append(f'\t<h4 class="resume-position-title font-weight-bold mb-2">{company_name} | {company_location}</h4>')
    
    # Position and overall dates
    html_parts.append(f'\t<div class="resume-position-time d-flex justify-content-between mb-3"><span class="font-weight-bold">{position_title}</span><em class="text-muted">{position_dates}</em></div>')
    
    # Projects
    for proj in projects:
        # Project info (Customer/Product) with dates
        if proj['info']:
            html_parts.append(f'\t<p class="mb-3"><em>{proj["info"]}</em> <span class="text-muted">({proj["dates"]})</span></p>')
        
        # Sections with items
        for section_name, items in proj['sections']:
            if section_name:
                html_parts.append(f'\t<p class="mb-2 ml-2"><strong>{section_name}:</strong></p>')
            html_parts.append('\t<ul class="resume-list mb-3">')
            for item in items:
                html_parts.append(f'\t\t<li class="mb-2">{item}</li>')
            html_parts.append('\t</ul>')
    
    # Global achievements at the end
    if global_achievements:
        html_parts.append('\t<p class="mb-2 mt-3"><strong>Achievements:</strong></p>')
        html_parts.append('\t<ul class="resume-list mb-3">')
        for item in global_achievements:
            if item[0] == 'bold_item':
                text = f'<strong>{item[1]}:</strong> {item[2]}'
                html_parts.append(f'\t\t<li class="mb-2">{text}</li>')
            elif item[0] == 'item':
                text = re.sub(r'<b>([^<]+)</b>', r'<strong>\1</strong>', item[1])
                html_parts.append(f'\t\t<li class="mb-2">{text}</li>')
        html_parts.append('\t</ul>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts) if html_parts else '<div class="item mb-3"><em>No work experience parsed.</em></div>'


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

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
import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

# Default paths
DEFAULT_DOX = REPO_ROOT / 'docs' / 'LePhucDuc_CV.dox'
DEFAULT_HTML = REPO_ROOT / 'docs' / 'index.html'

SECTION_PATTERN = re.compile(r'@section\s+(\w+)\s+[^\n]+\n(.*?)(?=@section|\*/)', re.DOTALL)

MARKERS = {
    'tagline': ('<!-- TAGLINE_START -->', '<!-- TAGLINE_END -->'),
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


def extract_tagline(text: str) -> str:
    """Extract tagline from @subtitle line."""
    match = re.search(r'@subtitle\s+([^\n]+)', text)
    if match:
        return match.group(1).strip()
    return 'Software Engineer'


def extract_contact_from_mainpage(text: str) -> str:
    """Extract contact info from header area (lines containing common patterns)."""
    # Look for the line that has common contact info patterns
    lines = text.splitlines()
    for line in lines:
        # Ignore the @mainpage line itself
        if '@mainpage' in line:
            continue
        if any(p in line for p in ['@', 'LinkedIn', 'GitHub', 'Online CV']):
            return line.strip()
    return ''


def build_contact_info(raw: str) -> str:
    """Build contact info HTML from pipe-separated line."""
    # Strip HTML tags like <center>, </center> from the raw string
    raw = re.sub(r'<[^>]+>', '', raw)
    # Also handle the pipe separator which might be escaped in some DOX versions
    raw = raw.replace('$\vert$', '|')
    parts = [p.strip() for p in raw.split('|') if p.strip()]
    items = []
    for p in parts:
        if '@' in p and '.' in p:  # basic email check
            items.append('<li class="mb-2"><i class="fas fa-envelope-square fa-fw fa-lg mr-2" aria-hidden="true"></i><a class="resume-link" href="mailto:{0}">{0}</a></li>'.format(p))
        elif 'linkedin.com' in p.lower() or '[LinkedIn]' in p:
            url = re.sub(r'.*?\[LinkedIn\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fab fa-linkedin fa-fw fa-lg mr-2" aria-hidden="true"></i><a class="resume-link" href="{0}" target="_blank">LinkedIn</a></li>'.format(url))
        elif 'github.com' in p.lower() or '[GitHub]' in p:
            url = re.sub(r'.*?\[GitHub\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fab fa-github fa-fw fa-lg mr-2" aria-hidden="true"></i><a class="resume-link" href="{0}" target="_blank">GitHub</a></li>'.format(url))
        elif 'Online CV' in p:
            url = re.sub(r'.*?\[Online CV\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):
                url = 'https://' + url
            items.append('<li class="mb-2"><i class="fas fa-external-link-alt fa-fw fa-lg mr-2" aria-hidden="true"></i><a class="resume-link" href="{0}" target="_blank">Online CV</a></li>'.format(url))
        elif re.search(r'\(\+?\d', p):  # phone
            phone_digits = re.sub(r'[^0-9+]', '', p)
            items.append('<li class="mb-2"><i class="fas fa-phone-square fa-fw fa-lg mr-2" aria-hidden="true"></i><a class="resume-link" href="tel:{0}">{1}</a></li>'.format(phone_digits, p))
        else:  # location or other
            items.append('<li class="mb-0"><i class="fas fa-map-marker-alt fa-fw fa-lg mr-2" aria-hidden="true"></i>{0}</li>'.format(p))
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
    """Build skills HTML from DOX format with Category: items."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    blocks = []
    for ln in lines:
        # Remove leading dash
        ln = re.sub(r'^-\s*', '', ln)
        # Match either <b>Cat</b>: vals or **Cat**: vals
        m = re.match(r'(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*):\s*(.*)', ln)
        if m:
            cat, vals = m.groups()
            cat = cat.strip()
            badge_color = SKILL_BADGE_COLORS.get(cat, 'primary')
            vals_list = split_skills(vals)
            # Clean up trailing dots and spaces from each skill
            vals_list = [v.strip().rstrip('.') for v in vals_list if v.strip()]
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
    # Convert Markdown bolding to HTML
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return f'<p class="mb-0">{text}</p>'


def build_certifications(raw: str) -> str:
    """Build certifications HTML from DOX format with list items."""
    lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip().startswith('-')]
    items = []
    for ln in lines:
        # Remove leading dash
        cert = re.sub(r'^-\s*', '', ln).strip()
        # Convert Markdown bolding to HTML
        cert = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', cert)
        items.append(f'<li class="mb-2"><i class="fas fa-certificate mr-2 text-primary" aria-hidden="true"></i>{cert}</li>')
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
    """Build education HTML from DOX format."""
    lines = raw.strip().splitlines()
    html_parts = ['<ul class="list-unstyled resume-education-list">']
    
    current_university = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue
            
        # Check for <b>...</b> @fill <em>...</em> pattern (University or Degree)
        match = re.match(r'^(?:-\s*)?(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*)\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if match:
            title = match.group(1).strip()
            right_side = match.group(2).strip()
            
            # If right side has digits, it's a degree/date line
            if re.search(r'\d', right_side):
                html_parts.append(f'\t<div class="d-flex justify-content-between mb-2"><strong>{title}</strong><em class="text-muted">{right_side}</em></div>')
            else:
                # If we had a previous university, close its block if needed
                if current_university:
                    html_parts.append('</li>')
                html_parts.append(f'<li class="mb-4">')
                html_parts.append(f'\t<h4 class="mb-3">{title}, {right_side}</h4>')
                current_university = title
            continue
            
        # Check for regular detail bullets under a degree
        if stripped.startswith('- '):
            detail = stripped[2:].strip()
            # Convert bolding
            detail = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', detail)
            # Strip @fill
            detail = detail.replace('@fill', '').strip()
            html_parts.append(f'\t<p class="mb-2 ml-3">{detail}</p>')

    if current_university:
        html_parts.append('</li>')
    html_parts.append('</ul>')
    
    return '\n'.join(html_parts)


def build_work(raw: str) -> str:
    """Build work experience HTML from DOX format with nested bullet support."""
    lines = raw.strip().splitlines()
    
    company_name, company_location = '', ''
    position_title, position_dates = '', ''
    projects = []
    current_project = None
    
    # Process the raw text line-by-line using original line indent info
    raw_lines = raw.splitlines()
    
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue
        
        # 1. Company/Position line
        company_match = re.match(r'^<b>([^<]+)</b>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if company_match:
            left, right = company_match.group(1).strip(), company_match.group(2).strip()
            if re.search(r'\d', right):
                position_title, position_dates = left, right
            else:
                company_name, company_location = left, right
            continue
        
        # 2. Project line
        project_match = re.match(r'^<i>([^<]+)</i>\s*@fill\s*<em>([^<]+)</em>$', stripped)
        if project_match:
            if current_project: projects.append(current_project)
            current_project = {'info': project_match.group(1).strip(), 'dates': project_match.group(2).strip(), 'items': []}
            continue
        
        # 3. Handle Bullets (Level 1 and Level 2)
        if stripped.startswith('- '):
            # Check for indentation: if line starts with enough spaces, it's nested
            is_sub_bullet = line.startswith('  ') or line.startswith('\t')
            item_text = stripped[2:].strip()
            
            # Punctuation cleanup for Technical Lead line
            item_text = re.sub(r'^[,\s:-]+', '', item_text)
            
            # Convert bolding at start of line
            has_colon_after = bool(re.match(r'^(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*)\s*:', item_text))
            is_category = item_text.endswith(':') or (not is_sub_bullet and ('**' in stripped or '<b>' in stripped))
            
            if is_category and not has_colon_after:
                # Add colon for category headers, consume trailing space to normalize
                item_text = re.sub(r'^(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*)\s*', r'<strong>\1</strong>: ', item_text)
            else:
                # Just replace tags, PRESERVE existing whitespace/punctuation
                item_text = re.sub(r'^(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*)', r'<strong>\1</strong>', item_text)
            
            item_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_text)
            item_text = item_text.replace('@fill', '').strip()
            # Final check for trailing colons on bold parts that shouldn't have them
            item_text = re.sub(r'</strong>:\s*:', r'</strong>:', item_text)
            if not item_text.endswith(':'):
                item_text = re.sub(r'</strong>:\s*$', r'</strong>', item_text)
            
            if current_project:
                # If it's a sub-bullet and we have a previous item that is a category
                if is_sub_bullet and current_project['items'] and isinstance(current_project['items'][-1], dict):
                    current_project['items'][-1]['sub'].append(item_text)
                elif item_text.endswith(':') or '**' in stripped or '<b>' in stripped:
                    # Treat as a header bullet if it looks like a category or has bolding
                    current_project['items'].append({'head': item_text, 'sub': []})
                else:
                    current_project['items'].append(item_text)
            elif stripped.startswith('Key Achievement'):
                # Handle Bosch Top Performer Award case if outside a project
                projects.append({'info': '', 'dates': '', 'items': [item_text]})
            continue
            
        # 4. Handle standalone bold headers (like "Key Achievement")
        header_match = re.match(r'^(?:<b>|\*\*)([^*<]+)(?:</b>|\*\*):?\s*(.*)', stripped)
        if header_match:
            name, rest = header_match.group(1).strip(), header_match.group(2).strip()
            if "Achievement" in name:
                text = f"<strong>{name}</strong>: {rest}" if rest else f"<strong>{name}</strong>"
                if current_project:
                    current_project['items'].append(text)
                else:
                    projects.append({'info': '', 'dates': '', 'items': [text]})
            continue

    if current_project: projects.append(current_project)
    
    # Build HTML
    html_parts = ['<div class="item mb-5">']
    html_parts.append(f'\t<h4 class="resume-position-title font-weight-bold mb-2">{company_name} | {company_location}</h4>')
    html_parts.append(f'\t<div class="resume-position-time d-flex justify-content-between mb-3"><span class="font-weight-bold">{position_title}</span><em class="text-muted">{position_dates}</em></div>')
    
    for proj in projects:
        if proj['info']:
            html_parts.append(f'\t<p class="mb-3"><em>{proj["info"]}</em> <span class="text-muted">({proj["dates"]})</span></p>')
        
        html_parts.append('\t<ul class="resume-list mb-3">')
        for item in proj['items']:
            if isinstance(item, dict):
                html_parts.append(f'\t\t<li class="mb-2">{item["head"]}')
                if item['sub']:
                    html_parts.append('\t\t\t<ul class="resume-list my-2">')
                    for s in item['sub']:
                        html_parts.append(f'\t\t\t\t<li class="mb-1">{s}</li>')
                    html_parts.append('\t\t\t</ul>')
                html_parts.append('\t\t</li>')
            else:
                html_parts.append(f'\t\t<li class="mb-2">{item}</li>')
        html_parts.append('\t</ul>')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)


def replace_block(html: str, start: str, end: str, new_inner: str) -> str:
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.DOTALL)
    replacement = f'{start}\n{new_inner}\n{end}'
    if not pattern.search(html):
        print(f'Warning: markers {start}..{end} not found', file=sys.stderr)
        return html
    return pattern.sub(replacement, html, count=1)


def main():
    parser = argparse.ArgumentParser(description='Update HTML placeholders from DOX file.')
    parser.add_argument('--dox', type=str, help='Path to source DOX file')
    parser.add_argument('--html', type=str, help='Path to output HTML file')
    args = parser.parse_args()

    dox_file = Path(args.dox) if args.dox else DEFAULT_DOX
    html_file = Path(args.html) if args.html else DEFAULT_HTML

    if not dox_file.exists():
        print(f'DOX file not found: {dox_file}', file=sys.stderr)
        return 1
    if not html_file.exists():
        print(f'HTML file not found: {html_file}', file=sys.stderr)
        return 1
    
    dox_text = dox_file.read_text(encoding='utf-8')
    sections = extract_sections(dox_text)
    html = html_file.read_text(encoding='utf-8')

    # Tagline
    tagline = extract_tagline(dox_text)
    html = replace_block(html, *MARKERS['tagline'], tagline)

    # Contact info (from header area)
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

    html_file.write_text(html + ('\n' if not html.endswith('\n') else ''), encoding='utf-8')
    print(f'HTML file {html_file.name} updated from DOX.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

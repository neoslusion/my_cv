#!/usr/bin/env python3
"""Update docs/index.html placeholders from docs/LePhucDuc_CV.dox.

Markers in HTML:
  <!-- CONTACT_INFO_START --> ... <!-- CONTACT_INFO_END -->
  <!-- SKILLS_START --> ... <!-- SKILLS_END -->
  <!-- EDUCATION_START --> ... <!-- EDUCATION_END -->
  <!-- WORK_EXPERIENCE_START --> ... <!-- WORK_EXPERIENCE_END -->

Minimal markdown-like parsing of the DOX sections.
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
    'skills': ('<!-- SKILLS_START -->', '<!-- SKILLS_END -->'),
    'education': ('<!-- EDUCATION_START -->', '<!-- EDUCATION_END -->'),
    'work_experience': ('<!-- WORK_EXPERIENCE_START -->', '<!-- WORK_EXPERIENCE_END -->'),
}

def extract_sections(text: str):
    sections = {}
    for name, body in SECTION_PATTERN.findall(text):
        sections[name.strip()] = body.strip().strip('\n')
    return sections

def build_contact_info(raw: str) -> str:
    # Expect a single line with pipes
    line = ' '.join([l.strip() for l in raw.splitlines() if l.strip()])
    # Remove leading **NAME** if present
    line = re.sub(r'^\*\*[^*]+\*\*\s*', '', line).strip()
    parts = [p.strip() for p in line.split('|') if p.strip()]
    items = []
    for p in parts:
        if re.search(r'@', p):  # email
            items.append('<li class="mb-2"><i class="fas fa-envelope-square fa-fw fa-lg mr-2"></i><a class="resume-link" href="mailto:{0}">{0}</a></li>'.format(p))
        elif re.search(r'linkedin', p, re.I):
            url = re.sub(r'^\[LinkedIn\]\((.*?)\).*', r'\1', p)
            if not url.startswith('http'):  # add protocol if missing
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
    # Ensure location last
    items.sort(key=lambda x: 1 if 'fa-map-marker-alt' in x else 0)
    return '\n'.join(items)

def build_skills(raw: str) -> str:
    # Lines with **Category:** items separated by commas
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    blocks = []
    for ln in lines:
        m = re.match(r'^\*\*([^:]+):\*\*\s*(.*)', ln)
        if m:
            cat, vals = m.groups()
            vals_html = ', '.join([f'<span class="badge badge-primary mr-1 mb-1">{v.strip()}</span>' for v in re.split(r',\s*', vals)])
            blocks.append(f'<div class="item"><h4 class="item-title">{cat.strip()}</h4><div class="item-content">{vals_html}</div></div>')
    if not blocks:
        # fallback raw
        return f'<div class="item"><em>{raw}</em></div>'
    return '\n'.join(blocks)

def markdown_to_html(md: str) -> str:
    # Very light conversion
    html = md
    html = re.sub(r'^###\s+(.+)$', r'<h4 class="mb-1">\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<div class="text-muted">\1</div>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Lists
    # group consecutive - lines
    lines = html.splitlines()
    out = []
    buf = []
    def flush():
        nonlocal buf, out
        if buf:
            out.append('<ul class="resume-list">')
            cleaned_items = []
            for b in buf:
                cleaned_items.append('<li>' + re.sub(r'^-\s+', '', b).strip() + '</li>')
            out.extend(cleaned_items)
            out.append('</ul>')
            buf = []
    for l in lines:
        if re.match(r'^-\s+', l):
            buf.append(l)
        else:
            flush()
            out.append(l)
    flush()
    html = '\n'.join(out)
    # Clean extra blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()

def build_education(raw: str) -> str:
    chunks = [c.strip() for c in re.split(r'\n{2,}', raw) if c.strip()]
    lis = []
    for c in chunks:
        html = markdown_to_html(c)
        lis.append(f'<li class="mb-3">{html}</li>')
    return '<ul class="list-unstyled resume-education-list">\n' + '\n'.join(lis) + '\n</ul>'

def build_work(raw: str) -> str:
    # Split by top-level company headings '### '
    parts = [p.strip() for p in re.split(r'(?m)^###\s+', raw) if p.strip()]
    divs = []
    for p in parts:
        # First line until newline is heading text for company
        if '\n' in p:
            heading, rest = p.split('\n', 1)
        else:
            heading, rest = p, ''
        heading_html = f'<h4 class="resume-position-title font-weight-bold mb-1">{heading.strip()}</h4>'
        rest_html = markdown_to_html(rest)
        divs.append(f'<div class="item mb-3">{heading_html}\n{rest_html}</div>')
    return '\n'.join(divs) if divs else '<div class="item mb-3"><em>No work experience parsed.</em></div>'

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
    sections = extract_sections(DOX_FILE.read_text(encoding='utf-8'))
    html = HTML_FILE.read_text(encoding='utf-8')

    # Contact info
    if 'contact_info' in sections:
        html = replace_block(html, *MARKERS['contact_info'], build_contact_info(sections['contact_info']))
    # Skills
    if 'skills' in sections:
        html = replace_block(html, *MARKERS['skills'], build_skills(sections['skills']))
    # Education
    if 'education' in sections:
        edu_inner = build_education(sections['education'])
        # For education markers, we only replace inside list placeholder (strip surrounding ul in template). Replace entire block with our UL.
        html = replace_block(html, *MARKERS['education'], edu_inner)
    # Work Experience
    if 'work_experience' in sections:
        html = replace_block(html, *MARKERS['work_experience'], build_work(sections['work_experience']))

    HTML_FILE.write_text(html + ('\n' if not html.endswith('\n') else ''), encoding='utf-8')
    print('index.html updated from DOX.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

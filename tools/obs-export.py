"""
obs-export.py — Obsidian markdown export tool

Usage:
    python obs-export.py input.md output.md

What it does:
  - Detects ATX headings (# through ######), skipping lines in fenced code blocks.
  - Splits the document into PREAMBLE (before "Table of Contents" heading),
    TOC HEADING, and BODY.
  - Numbers non-skip body headings (H2+ only; H1 never numbered).
  - Appendix H2s ("Appendix ...") get letter numbering A., B., ...
  - Skip headings (ending in " ^skip") and their children are not numbered.
  - TODOs heading (^skip + text starts with "todo") and children excluded from TOC.
  - Rebuilds the TOC as a nested unordered list after the TOC heading.
  - Rewrites internal fragment links in the BODY and PREAMBLE using old→new slug map.
  - Handles both standard markdown [text](#fragment) and Obsidian [[#Anchor]] links.
  - Replaces link text for numbered targets with "Section X.Y." / "Appendix A.1."
  - Converts {{!RFC1234}} / {{?RFC1234}} to markdown links and builds a numbered
    References section (Normative + Informative) inserted before the first appendix.
  - Fetches RFC metadata from the RFC Editor API; caches results in .ref-cache.json
    next to this script. External URL titles are cached the same way.
  - All other outgoing [text](https://...) links are collected into Informative Refs.
  - Strips <!-- QueryToSerialize|SerializedQuery... --> HTML comments.
  - Strips tag strings: #technical, #documentation, #external, #public.
  - Preserves frontmatter, fenced code blocks, and all other content verbatim.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Reference cache (persisted as JSON next to this script)
# ---------------------------------------------------------------------------

_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.ref-cache.json')
_cache = None


def _load_cache():
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_CACHE_PATH, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
    except (OSError, json.JSONDecodeError):
        _cache = {}
    return _cache


def _save_cache():
    try:
        with open(_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(_cache, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"  Warning: could not save cache: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# RFC metadata fetch
# ---------------------------------------------------------------------------

def fetch_rfc_metadata(number):
    """
    Fetch RFC metadata from https://bib.ietf.org/public/rfc/bibxml/reference.RFC.{number}.xml.
    Returns dict with keys: title, authors (list of (initials, surname)), month, year.
    On error, returns {'error': str} so callers can surface the failure.
    Results are cached to .ref-cache.json.
    """
    cache = _load_cache()
    key = f'rfc:{number}'
    if key in cache:
        return cache[key]

    url = f'https://bib.ietf.org/public/rfc/bibxml/reference.RFC.{number}.xml'
    print(f'  Fetching RFC {number} metadata...', file=sys.stderr)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'obs-export/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        front = root.find('front')
        if front is None:
            result = {'error': f'no <front> element in {url}'}
            cache[key] = result
            _save_cache()
            return result
        title = (front.findtext('title') or '').strip()
        authors = []
        for a in front.findall('author'):
            initials = a.get('initials', '').strip()
            surname = a.get('surname', '').strip()
            if surname or initials:
                authors.append([initials, surname])
        date_el = front.find('date')
        month = (date_el.get('month', '') if date_el is not None else '').strip()
        year = (date_el.get('year', '') if date_el is not None else '').strip()
        result = {'title': title, 'authors': authors, 'month': month, 'year': year}
        cache[key] = result
        _save_cache()
        return result
    except Exception as e:
        msg = str(e)
        print(f'  Warning: could not fetch RFC {number}: {msg}', file=sys.stderr)
        result = {'error': msg}
        cache[key] = result
        _save_cache()
        return result


def _format_authors(authors):
    """Format author list in IETF citation style."""
    if not authors:
        return ''
    if len(authors) == 1:
        i, s = authors[0]
        return f'{s}, {i}' if s else i
    first_parts = [f'{s}, {i}' for i, s in authors[:-1]]
    li, ls = authors[-1]
    if len(authors) == 2:
        return f'{first_parts[0]} and {li} {ls}'
    return ', '.join(first_parts) + f', and {li} {ls}'


def build_rfc_citation(number):
    """Return formatted citation body (without label prefix) for an RFC."""
    meta = fetch_rfc_metadata(number)
    if meta is None or 'error' in meta:
        err = meta['error'] if meta else 'unknown error'
        return f'RFC {number}. [METADATA UNAVAILABLE: {err}]'
    parts = []
    authors_str = _format_authors(meta.get('authors', []))
    if authors_str:
        parts.append(authors_str)
    if meta.get('title'):
        parts.append(f'"{meta["title"]}"')
    parts.append(f'RFC {number}')
    date_parts = [p for p in [meta.get('month'), meta.get('year')] if p]
    if date_parts:
        parts.append(' '.join(date_parts))
    return ', '.join(parts) + '.'


# ---------------------------------------------------------------------------
# URL title fetch
# ---------------------------------------------------------------------------

def fetch_url_title(url):
    """
    Fetch the <title> of a URL. Returns string or None.
    Cached to .ref-cache.json.
    """
    cache = _load_cache()
    key = f'url:{url}'
    if key in cache:
        return cache[key]

    print(f'  Fetching title for {url[:70]}...', file=sys.stderr)
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 obs-export/1.0 (reference fetcher)'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read(65536).decode('utf-8', errors='ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = re.sub(r'\s+', ' ', m.group(1)).strip() if m else None
        cache[key] = title
        _save_cache()
        return title
    except Exception as e:
        print(f'  Warning: could not fetch title for {url}: {e}', file=sys.stderr)
        cache[key] = None
        _save_cache()
        return None


# ---------------------------------------------------------------------------
# Reference entry formatting
# ---------------------------------------------------------------------------

def _ref_label_pad(label):
    """Format [LABEL] left-padded so content starts at column 11."""
    bracket = f'[{label}]'
    return bracket + ' ' * max(2, 11 - len(bracket))


# ---------------------------------------------------------------------------
# GitHub slug algorithm
# ---------------------------------------------------------------------------

def github_slug(text):
    """Compute GitHub-style heading anchor slug from raw heading text."""
    s = text.lower()
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    s = re.sub(r'[^\w \-]', '', s, flags=re.ASCII)
    s = s.replace(' ', '-')
    s = re.sub(r'-{2,}', '-', s)
    s = s.strip('-')
    return s


def make_slug_map_with_duplicates(texts):
    """
    Given a list of strings, return a list of unique slugs matching GitHub's
    duplicate-handling: first occurrence gets plain slug, subsequent get -1, -2...
    """
    counts = {}
    result = []
    for text in texts:
        base = github_slug(text)
        if base not in counts:
            counts[base] = 0
            result.append(base)
        else:
            counts[base] += 1
            result.append(f"{base}-{counts[base]}")
    return result


# ---------------------------------------------------------------------------
# Fenced code block detection
# ---------------------------------------------------------------------------

def parse_lines_with_fence_state(lines):
    """
    Yield (line_index, line, in_fence) for every line.
    Tracks fenced code block state.
    """
    in_fence = False
    fence_char = None
    fence_len = 0
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        m = re.match(r'^(`{3,}|~{3,})', stripped)
        if m:
            char = m.group(1)[0]
            length = len(m.group(1))
            if not in_fence:
                in_fence = True
                fence_char = char
                fence_len = length
                yield i, line, False
                continue
            elif char == fence_char and length >= fence_len:
                in_fence = False
                fence_char = None
                fence_len = 0
                yield i, line, False
                continue
        yield i, line, in_fence


# ---------------------------------------------------------------------------
# Heading parser
# ---------------------------------------------------------------------------

ATX_RE = re.compile(r'^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$')


def parse_heading(line):
    """Parse an ATX heading line. Returns (level, text) or None."""
    m = ATX_RE.match(line.rstrip('\n'))
    if m:
        return len(m.group(1)), m.group(2).rstrip()
    return None


# ---------------------------------------------------------------------------
# Frontmatter detection
# ---------------------------------------------------------------------------

def split_frontmatter(lines):
    """
    If file starts with '---', return (frontmatter_lines, body_lines).
    frontmatter_lines includes both '---' delimiters.
    """
    if not lines or lines[0].rstrip('\n') != '---':
        return [], lines
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip('\n') == '---':
            end = i
            break
    if end is None:
        return [], lines
    return lines[:end + 1], lines[end + 1:]


# ---------------------------------------------------------------------------
# SerializedQuery block preprocessor
# ---------------------------------------------------------------------------

def preprocess_serialized_queries(text):
    """
    Find <!-- SerializedQuery: ... --> ... <!-- SerializedQuery END --> blocks.
    Within each block, reformat H1 Obsidian wiki-link section headers + their
    list items into a flat list, removing the filename prefix from the label.

    Input:
        # [[file.md#Anchor|filename > Section Name]]
            - item text here
    Output:
        - Section Name > item text here ([[#Anchor|link]])
    """
    BLOCK_RE = re.compile(
        r'<!-- SerializedQuery:.*?-->\n(.*?)<!-- SerializedQuery END -->',
        re.DOTALL
    )
    H1_WIKILINK_RE = re.compile(r'^# \[\[[^\]]*?#([^\]|]+)\|([^\]]+)\]\]\s*$')
    ITEM_RE = re.compile(r'^(\s+)- (?:\[.\] )?(.+)$')

    def reformat_block(m):
        content = m.group(1)
        lines = content.splitlines()
        result = []
        current_anchor = None
        current_prefix = None
        for line in lines:
            h1_m = H1_WIKILINK_RE.match(line)
            if h1_m:
                current_anchor = h1_m.group(1).strip()
                raw_prefix = h1_m.group(2).strip()
                parts = raw_prefix.split(' > ', 1)
                current_prefix = parts[1] if len(parts) > 1 else raw_prefix
                continue
            if line.strip() == '':
                continue
            item_m = ITEM_RE.match(line)
            if item_m and current_prefix is not None:
                item_text = item_m.group(2).strip()
                link = f'([[#{current_anchor}|link]])'
                result.append(f'- {current_prefix} > {item_text} {link}\n')
            else:
                result.append(line.strip() + '\n')
        return ''.join(result)

    return BLOCK_RE.sub(reformat_block, text)


# ---------------------------------------------------------------------------
# RFC citation template conversion
# ---------------------------------------------------------------------------

_NORM_RFC_RE = re.compile(r'\{\{!RFC(\d+)\}\}', re.IGNORECASE)
_INFO_RFC_RE = re.compile(r'\{\{\?RFC(\d+)\}\}', re.IGNORECASE)
_EXT_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')


def collect_references(body_lines):
    """
    Scan body lines (respecting fenced code blocks) for RFC citation templates
    and external markdown links.

    Returns:
        normative_rfcs: dict {number_str: True} in insertion order
        informative_rfcs: dict {number_str: True} in insertion order
        external_links: dict {label: url} in insertion order (first-seen wins)
    """
    normative = {}
    informative = {}
    external = {}

    for _i, line, in_fence in parse_lines_with_fence_state(body_lines):
        if in_fence:
            continue
        for m in _NORM_RFC_RE.finditer(line):
            n = str(int(m.group(1)))
            if n not in normative:
                normative[n] = True
        for m in _INFO_RFC_RE.finditer(line):
            n = str(int(m.group(1)))
            if n not in informative and n not in normative:
                informative[n] = True
        for m in _EXT_LINK_RE.finditer(line):
            label = m.group(1).strip()
            url = m.group(2).strip()
            if label not in external:
                external[label] = url

    # Anything that ended up in both: normative wins
    for n in list(informative.keys()):
        if n in normative:
            del informative[n]

    return normative, informative, external


def convert_rfc_citations(body_lines):
    """
    Replace {{!RFC...}} and {{?RFC...}} with markdown links in non-fenced lines.
    Returns new list of lines.
    """
    result = []
    for _i, line, in_fence in parse_lines_with_fence_state(body_lines):
        if not in_fence:
            line = _NORM_RFC_RE.sub(
                lambda m: f'[RFC{m.group(1)}](https://www.rfc-editor.org/info/rfc{m.group(1)})',
                line
            )
            line = _INFO_RFC_RE.sub(
                lambda m: f'[RFC{m.group(1)}](https://www.rfc-editor.org/info/rfc{m.group(1)})',
                line
            )
        result.append(line)
    return result


def build_references_section(normative, informative, external):
    """
    Fetch metadata and build the References section as a list of lines.
    Returns [] if there are no references.
    """
    if not normative and not informative and not external:
        return []

    lines = []
    lines.append('\n')
    lines.append('## References\n')
    lines.append('\n')

    if normative:
        lines.append('### Normative References\n')
        lines.append('\n')
        for n in normative:
            citation = build_rfc_citation(n)
            lines.append(_ref_label_pad(f'RFC{n}') + citation + '\n')
            lines.append('\n')

    if informative or external:
        lines.append('### Informative References\n')
        lines.append('\n')
        for n in informative:
            citation = build_rfc_citation(n)
            lines.append(_ref_label_pad(f'RFC{n}') + citation + '\n')
            lines.append('\n')
        for label, url in external.items():
            title = fetch_url_title(url)
            content = f'"{title}", {url}.' if title else f'{url}.'
            lines.append(_ref_label_pad(label) + content + '\n')
            lines.append('\n')

    return lines


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process(input_text):
    all_lines = input_text.splitlines(keepends=True)

    # --- Frontmatter ---
    frontmatter, content_lines = split_frontmatter(all_lines)

    # --- Preprocess SerializedQuery blocks ---
    content_text = preprocess_serialized_queries(''.join(content_lines))
    content_lines = content_text.splitlines(keepends=True)

    # --- Find TOC heading ---
    annotated = list(parse_lines_with_fence_state(content_lines))
    toc_idx = None
    for i, line, in_fence in annotated:
        if not in_fence:
            h = parse_heading(line)
            if h and h[1].strip().lower() == 'table of contents':
                toc_idx = i
                break
    if toc_idx is None:
        raise ValueError("No 'Table of Contents' heading found in document.")

    # Split zones
    preamble_lines = content_lines[:toc_idx]
    toc_heading_line = content_lines[toc_idx]
    body_lines = content_lines[toc_idx + 1:]

    # Drop existing TOC content (list lines immediately after TOC heading)
    old_toc_end = 0
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        if stripped == '' or stripped.startswith('- '):
            old_toc_end = i + 1
        else:
            break
    body_lines = body_lines[old_toc_end:]

    # --- Collect references and convert {{!RFC...}} / {{?RFC...}} ---
    normative_refs, informative_refs, external_refs = collect_references(body_lines)

    if normative_refs or informative_refs or external_refs:
        print('Fetching reference metadata...', file=sys.stderr)

    refs_lines = build_references_section(normative_refs, informative_refs, external_refs)

    # Convert citation templates to markdown links
    body_lines = convert_rfc_citations(body_lines)

    # Inject references section before first Appendix H2 (or at end)
    if refs_lines:
        insert_at = len(body_lines)
        for i, line, in_fence in parse_lines_with_fence_state(body_lines):
            if not in_fence:
                h = parse_heading(line)
                if h and h[0] == 2 and h[1].strip().lower().startswith('appendix '):
                    insert_at = i
                    break
        body_lines = body_lines[:insert_at] + refs_lines + body_lines[insert_at:]

    # --- Parse body headings ---
    body_annotated = list(parse_lines_with_fence_state(body_lines))

    body_headings = []
    for i, line, in_fence in body_annotated:
        if not in_fence:
            h = parse_heading(line)
            if h:
                level, text = h
                is_skip = text.endswith(' ^skip')
                skip_stripped = text[:-6] if is_skip else text
                is_appendix = (
                    level == 2
                    and skip_stripped.strip().lower().startswith('appendix ')
                    and not is_skip
                )
                body_headings.append({
                    'idx': i,
                    'level': level,
                    'raw_text': text,
                    'skip_stripped': skip_stripped,
                    'is_skip': is_skip,
                    'is_appendix': is_appendix,
                    'parent_skip': False,
                    'toc_excluded': False,
                })

    # Mark children of skip headings
    for j, hinfo in enumerate(body_headings):
        if hinfo['is_skip'] or hinfo['parent_skip']:
            parent_level = hinfo['level']
            for k in range(j + 1, len(body_headings)):
                if body_headings[k]['level'] <= parent_level:
                    break
                body_headings[k]['parent_skip'] = True

    # Exclude TODOs heading and all its children from the TOC
    for j, hinfo in enumerate(body_headings):
        if hinfo['is_skip'] and hinfo['skip_stripped'].strip().lower().startswith('todo'):
            hinfo['toc_excluded'] = True
            parent_level = hinfo['level']
            for k in range(j + 1, len(body_headings)):
                if body_headings[k]['level'] <= parent_level:
                    break
                body_headings[k]['toc_excluded'] = True

    def is_effectively_skipped(hinfo):
        return hinfo['is_skip'] or hinfo['parent_skip']

    # --- Number headings ---
    regular_counters = [0] * 6
    appendix_counter = 0
    appendix_sub_counters = [0] * 5
    in_appendix = False
    current_appendix_letter = None

    for hinfo in body_headings:
        if is_effectively_skipped(hinfo):
            hinfo['number'] = None
            hinfo['final_text'] = hinfo['skip_stripped']
            continue

        level = hinfo['level']

        if level == 1:
            hinfo['number'] = None
            hinfo['final_text'] = hinfo['skip_stripped']
            continue

        if hinfo['is_appendix']:
            in_appendix = True
            appendix_counter += 1
            current_appendix_letter = chr(ord('A') + appendix_counter - 1)
            appendix_sub_counters = [0] * 5
            rest = re.sub(r'^appendix\s+', '', hinfo['skip_stripped'], flags=re.IGNORECASE)
            hinfo['number'] = f"Appendix {current_appendix_letter}."
            hinfo['final_text'] = f"Appendix {current_appendix_letter}. {rest}"
            hinfo['appendix_letter'] = current_appendix_letter
            hinfo['appendix_sub'] = None
        elif in_appendix and level >= 3:
            depth = level - 3
            appendix_sub_counters[depth] += 1
            for d in range(depth + 1, len(appendix_sub_counters)):
                appendix_sub_counters[d] = 0
            sub_nums = '.'.join(str(appendix_sub_counters[d]) for d in range(depth + 1))
            label = f"{current_appendix_letter}.{sub_nums}."
            hinfo['number'] = label
            hinfo['final_text'] = f"{label} {hinfo['skip_stripped']}"
            hinfo['appendix_letter'] = current_appendix_letter
            hinfo['appendix_sub'] = sub_nums
        else:
            if level == 2:
                in_appendix = False
                current_appendix_letter = None
            depth = level - 2
            regular_counters[depth] += 1
            for d in range(depth + 1, len(regular_counters)):
                regular_counters[d] = 0
            nums = '.'.join(str(regular_counters[d]) for d in range(depth + 1))
            label = f"{nums}."
            hinfo['number'] = label
            hinfo['final_text'] = f"{label} {hinfo['skip_stripped']}"
            hinfo['appendix_letter'] = None
            hinfo['appendix_sub'] = None

    # --- Build slug maps ---
    preamble_annotated = list(parse_lines_with_fence_state(preamble_lines))
    preamble_heading_texts = []
    for i, line, in_fence in preamble_annotated:
        if not in_fence:
            h = parse_heading(line)
            if h:
                preamble_heading_texts.append(h[1])

    toc_h = parse_heading(toc_heading_line)
    toc_heading_text = toc_h[1] if toc_h else 'Table of Contents'

    all_old_texts = preamble_heading_texts + [toc_heading_text] + [
        hinfo['skip_stripped'] for hinfo in body_headings
    ]
    all_new_texts = preamble_heading_texts + [toc_heading_text] + [
        hinfo['final_text'] for hinfo in body_headings
    ]

    old_slugs = make_slug_map_with_duplicates(all_old_texts)
    new_slugs = make_slug_map_with_duplicates(all_new_texts)

    n_preamble = len(preamble_heading_texts)
    body_heading_old_slugs = old_slugs[n_preamble + 1:]
    body_heading_new_slugs = new_slugs[n_preamble + 1:]

    for j, hinfo in enumerate(body_headings):
        hinfo['old_slug'] = body_heading_old_slugs[j]
        hinfo['new_slug'] = body_heading_new_slugs[j]

    old_to_new = {}
    for j, hinfo in enumerate(body_headings):
        old_to_new[hinfo['old_slug']] = hinfo['new_slug']
    for j in range(n_preamble):
        old_to_new[old_slugs[j]] = new_slugs[j]
    old_to_new[old_slugs[n_preamble]] = new_slugs[n_preamble]

    slug_to_hinfo = {}
    for hinfo in body_headings:
        slug_to_hinfo[hinfo['old_slug']] = hinfo

    # raw_slug→hinfo for Obsidian [[#Anchor]] links
    # Uses github_slug(raw_text) so "Foo ^skip" and "Foo skip" map to the same slug
    raw_slug_to_hinfo = {}
    for hinfo in body_headings:
        rs = github_slug(hinfo['raw_text'])
        if rs not in raw_slug_to_hinfo:
            raw_slug_to_hinfo[rs] = hinfo

    def _numbered_link_text(hinfo):
        if hinfo.get('appendix_letter') and hinfo.get('appendix_sub') is None:
            return f"Appendix {hinfo['appendix_letter']}."
        elif hinfo.get('appendix_letter'):
            return f"Appendix {hinfo['appendix_letter']}.{hinfo['appendix_sub']}."
        else:
            return f"Section {hinfo['number']}"

    # --- Link rewriters ---
    LINK_RE = re.compile(r'\[([^\]]*)\]\((#[^)]*)\)')

    def rewrite_link(m):
        link_text = m.group(1)
        fragment = m.group(2)
        anchor = fragment.lstrip('#')
        new_anchor = old_to_new.get(anchor, anchor)
        new_fragment = '#' + new_anchor
        hinfo = slug_to_hinfo.get(anchor)
        if hinfo and not is_effectively_skipped(hinfo) and hinfo.get('number'):
            return f"[{_numbered_link_text(hinfo)}]({new_fragment})"
        return f"[{link_text}]({new_fragment})"

    WIKILINK_RE = re.compile(r'\[\[#([^\]|]+?)(?:\|([^\]]*))?\]\]')

    def rewrite_wikilink(m):
        anchor = m.group(1).strip()
        provided_display = m.group(2).strip() if m.group(2) is not None else None
        wiki_slug = github_slug(anchor)
        hinfo = raw_slug_to_hinfo.get(wiki_slug)
        if hinfo is None:
            display = provided_display or re.sub(r'\s+skip\s*$', '', anchor, flags=re.IGNORECASE).strip()
            return f'[{display}](#{wiki_slug})'
        new_slug = hinfo['new_slug']
        if is_effectively_skipped(hinfo):
            display = provided_display if provided_display is not None else hinfo['skip_stripped']
            return f'[{display}](#{new_slug})'
        elif hinfo.get('number'):
            return f'[{_numbered_link_text(hinfo)}](#{new_slug})'
        display = provided_display if provided_display is not None else hinfo['skip_stripped']
        return f'[{display}](#{new_slug})'

    def rewrite_links_in_line(line):
        line = LINK_RE.sub(rewrite_link, line)
        line = WIKILINK_RE.sub(rewrite_wikilink, line)
        return line

    # --- Rewrite body lines ---
    new_body_lines = []
    body_heading_by_idx = {hinfo['idx']: hinfo for hinfo in body_headings}

    for i, line, in_fence in body_annotated:
        if not in_fence and i in body_heading_by_idx:
            hinfo = body_heading_by_idx[i]
            hashes = '#' * hinfo['level']
            new_body_lines.append(f"{hashes} {hinfo['final_text']}\n")
        elif not in_fence:
            new_body_lines.append(rewrite_links_in_line(line))
        else:
            new_body_lines.append(line)

    # --- Generate TOC ---
    toc_entries = []
    for hinfo in body_headings:
        level = hinfo['level']
        if level == 1 or hinfo.get('toc_excluded'):
            continue
        indent = '  ' * (level - 2)
        toc_entries.append(f"{indent}- [{hinfo['final_text']}](#{hinfo['new_slug']})\n")

    toc_block = ''.join(toc_entries)

    # --- Strip tags and serialized query comments ---
    SERIAL_QUERY_RE = re.compile(r'<!--\s*(QueryToSerialize|SerializedQuery)\b.*?-->', re.DOTALL)
    # (?![\w-]) prevents stripping #documentation inside URL slugs like #documentation-issues
    TAG_RE = re.compile(r'#(?:technical|documentation|external|public)(?![\w-])')

    def clean_lines(lines):
        text = ''.join(lines)
        text = SERIAL_QUERY_RE.sub('', text)
        text = TAG_RE.sub('', text)
        text = re.sub(r'^[ \t]+$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.splitlines(keepends=True)

    # --- Rewrite links in preamble (headings stay unnumbered) ---
    new_preamble_lines = []
    for i, line, in_fence in preamble_annotated:
        if not in_fence:
            new_preamble_lines.append(rewrite_links_in_line(line))
        else:
            new_preamble_lines.append(line)

    clean_preamble = clean_lines(new_preamble_lines)
    clean_body = clean_lines(new_body_lines)

    # --- Assemble output ---
    output_parts = []
    output_parts.extend(frontmatter)
    output_parts.extend(clean_preamble)
    output_parts.append(toc_heading_line)
    if toc_block:
        output_parts.append('\n')
        output_parts.append(toc_block)
        output_parts.append('\n')
    output_parts.extend(clean_body)

    return ''.join(output_parts)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python obs-export.py input.md output.md", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except OSError as e:
        print(f"Error reading {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output_text = process(input_text)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
    except OSError as e:
        print(f"Error writing {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Done: {output_path}")


if __name__ == '__main__':
    main()

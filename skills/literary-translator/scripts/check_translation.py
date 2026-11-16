#!/usr/bin/env python3
"""Mechanical check of a literary translation.

Usage:
  python3 check_translation.py ORIGINAL TRANSLATION [--brief BRIEF.md] [--draft DRAFT]
          [--from it] [--to en-us|en-gb|en|es|fr|de|pt|ru|uk|ja|zh|ko|ar] [--paragraphs auto|lines|blocks]
  python3 check_translation.py ORIGINAL --candidates [--brief BRIEF.md]

Formats: .docx, .txt, .md (one paragraph per line, or blocks separated by blank lines).
Languages: uk is Ukrainian (British English is en-gb).
From the translation brief it reads the "Glossary" and "Banned words" sections.
The script FLAGS, it doesn't decide: every item is checked by reading the two texts.
Standard library only; it reads the files it is given and prints a report.
"""
import argparse
import difflib
from collections import Counter
import math
import re
import statistics
import sys
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def char_ranges(*pairs):
    """Unicode ranges for character classes. They are built with chr() rather than with escape
    sequences, so that tools which turn escape sequences into characters (and drop the invisible
    ones) cannot alter them."""
    return ''.join(chr(a) + '-' + chr(b) for a, b in pairs)


ARABIC, CYRILLIC, KANA, HAN = (char_ranges((0x600, 0x6FF)), char_ranges((0x400, 0x4FF)),
                               char_ranges((0x3040, 0x30FF)), char_ranges((0x4E00, 0x9FFF)))
# scripts in which words attach to particles or have no spaces: Arabic, kana, ideographs, Hangul
NO_SPACES = re.compile('[' + char_ranges((0x600, 0x6FF), (0x3040, 0x30FF), (0x3400, 0x9FFF),
                                         (0xAC00, 0xD7AF), (0xF900, 0xFAFF)) + ']')
NON_LATIN = ('ru', 'uk', 'ja', 'zh', 'ko', 'ar')
NO_ITALICS = ('ja', 'zh', 'ko', 'ar')  # italics are not part of their typography
MD_ITALIC = re.compile(r'(?<![*\w])\*(?![*\s])[^*\n]+?(?<![*\s])\*(?![*\w])'
                       r'|(?<![_\w])_(?![_\s])[^_\n]+?(?<![_\s])_(?![_\w])')


def italic_styles(z):
    """Word styles: id -> italic yes/no (None if the style doesn't say), and the default paragraph style."""
    try:
        root = ET.fromstring(z.read('word/styles.xml'))
    except KeyError:
        return {}, None
    based_on, own, default = {}, {}, None
    for st in root.iter(W + 'style'):
        sid = st.get(W + 'styleId')
        b, i = st.find(W + 'basedOn'), st.find(W + 'rPr/' + W + 'i')
        based_on[sid] = b.get(W + 'val') if b is not None else None
        own[sid] = None if i is None else i.get(W + 'val', 'true') not in ('0', 'false', 'off')
        if st.get(W + 'type') == 'paragraph' and st.get(W + 'default') in ('1', 'true'):
            default = sid

    def resolve(sid, seen=()):
        if sid not in own or sid in seen:
            return None
        return own[sid] if own[sid] is not None else resolve(based_on[sid], seen + (sid,))
    return {sid: resolve(sid) for sid in own}, default


def read_paragraphs(path, mode):
    """Paragraphs of the text and, for .docx and .md, how many italic spans each one has (otherwise None)."""
    if path.lower().endswith('.docx'):
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read('word/document.xml'))
            styles, default = italic_styles(z)
        pairs = []
        for p in root.iter(W + 'p'):
            ps = p.find(W + 'pPr/' + W + 'pStyle')
            par_italic = bool(styles.get(ps.get(W + 'val') if ps is not None else default))
            text, spans, inside = [], 0, False
            for r in p.iter(W + 'r'):
                t = ''.join((n.text or '') if n.tag == W + 't' else ' '
                            for n in r.iter() if n.tag in (W + 't', W + 'tab', W + 'br'))
                text.append(t)
                if not t.strip():
                    continue
                rpr = r.find(W + 'rPr')
                i = rpr.find(W + 'i') if rpr is not None else None
                rs = rpr.find(W + 'rStyle') if rpr is not None else None
                if i is not None:
                    c = i.get(W + 'val', 'true') not in ('0', 'false', 'off')
                elif rs is not None and styles.get(rs.get(W + 'val')) is not None:
                    c = styles[rs.get(W + 'val')]
                else:
                    c = par_italic
                if c and not inside:
                    spans += 1
                inside = c
            pairs.append((''.join(text), spans))
        has_italics = True
    else:
        with open(path, encoding='utf-8-sig', errors='replace') as f:
            lines = f.read().replace('\r\n', '\n').replace('\r', '\n').split('\n')
        filled = [r for r in lines if r.strip()]
        if mode == 'auto':  # hard-wrapped every ~80 characters: the paragraphs are the blocks
            blocks = sum(1 for k, r in enumerate(lines) if r.strip() and (k == 0 or not lines[k - 1].strip()))
            lengths = [len(r) for r in filled] or [0]
            hard_wrapped = max(lengths) <= 100 and sum(x >= 0.75 * max(lengths) for x in lengths) >= 0.4 * len(lengths)
            mode = 'blocks' if 2 <= blocks < len(filled) and hard_wrapped else 'lines'
        if mode == 'lines':
            paras = filled
        else:
            paras, cur = [], []
            for r in lines + ['']:
                if r.strip():
                    cur.append(r.strip())
                elif cur:
                    paras.append(' '.join(cur))
                    cur = []
        has_italics = path.lower().endswith(('.md', '.markdown'))
        pairs = [(p, len(MD_ITALIC.findall(p)) if has_italics else 0) for p in paras]
    pairs = [(re.sub(r'[ \t\r\n\f\v]+', ' ', p).strip(), c) for p, c in pairs if p.strip()]  # keeps non-breaking spaces
    return [p for p, _ in pairs], ([c for _, c in pairs] if has_italics else None)


# Length-based alignment (Gale and Church, 1993): kinds of match and their prior probabilities.
BEADS = ((1, 1, 0.94), (1, 0, 0.01), (0, 1, 0.01), (2, 1, 0.02), (1, 2, 0.02))


def align(ls, lt):
    n, m = len(ls), len(lt)
    c = sum(lt) / max(sum(ls), 1)
    ps, pt = [0], [0]
    for x in ls:
        ps.append(ps[-1] + x)
    for x in lt:
        pt.append(pt[-1] + x)

    def cost(a, b):
        if a == 0 or b == 0:  # omission or addition: only the prior probability counts
            return 0.0
        mean = (a + b / c) / 2
        delta = (b - a * c) / math.sqrt(6.8 * mean)
        return -math.log(max(math.erfc(abs(delta) / math.sqrt(2)), 1e-300))

    band = abs(n - m) + 60
    D = [dict() for _ in range(n + 1)]
    D[0][0] = (0.0, None)
    for i in range(n + 1):
        center = round(i * m / n)
        for j in range(max(0, center - band), min(m, center + band) + 1):
            if i == 0 and j == 0:
                continue
            best = None
            for a, b, p in BEADS:
                pi, pj = i - a, j - b
                if pi < 0 or pj < 0 or pj not in D[pi]:
                    continue
                v = D[pi][pj][0] + cost(ps[i] - ps[pi], pt[j] - pt[pj]) - math.log(p)
                if best is None or v < best[0]:
                    best = (v, (a, b))
            if best:
                D[i][j] = best
    out, i, j = [], n, m
    while i or j:
        a, b = D[i][j][1]
        out.append((i - a, i, j - b, j))
        i, j = i - a, j - b
    return out[::-1]


ABBR = set('mr mrs ms dr st sr jr prof gen col lt sgt capt sig sigg dott ing avv ecc etc vs nr pag pp '
           'mme mlle sra dra hr fr bzw usw'.split())
SENTENCE_END = re.compile(r'[。！？]+[」』”’）]*|(?:[.!?…؟]+|—(?=[»"”’]))[»"”’\')\]]*(?=\s|$)')


def count_sentences(t):
    n = 0
    for mt in SENTENCE_END.finditer(t):
        if mt.group()[0] == '.':
            w = re.search(r'(\w+)\.$', t[:mt.start() + 1])
            if w and (w.group(1).lower() in ABBR or (len(w.group(1)) == 1 and w.group(1).isupper())):
                continue
        n += 1
    return max(n, 1)


def glossary_regex(cell):
    """Glossary cell -> regex. '*' = any ending, ';' separates the accepted alternatives.
    In Chinese, Japanese, Korean and Arabic the term is also found attached to other words or particles."""
    cell = re.sub(r'\([^)]*\)', '', cell).replace('**', '').replace('__', '').replace('`', '')
    alternatives = []
    for a in cell.split(';'):
        a = re.sub(r'\s+', ' ', a).strip()
        if a:
            body = ''.join(r'\w*' if ch == '*' else r'\s+' if ch == ' ' else re.escape(ch) for ch in a)
            alternatives.append(body if NO_SPACES.search(a) else r'(?<!\w)' + body + r'(?!\w)')
    return re.compile('|'.join(alternatives), re.I) if alternatives else None


HEADER_WORDS = {'source', 'original', 'term', 'word', 'banned',
                'originale', 'origine', 'termine', 'italiano', 'it', 'parola', 'vietato', 'vietata'}
GLOSSARY_HEADING = r'glossar'  # Glossary, Glossario, Glossar
BANNED_HEADING = r'(?:banned|forbidden)\s+(?:words|vocabulary)|lessico\s+vietat'


def brief_section(lines, heading):
    """Lines of the brief section whose heading starts with `heading`, up to the next heading."""
    for k, r in enumerate(lines):
        if re.match(r'\s*#+\s*(?:' + heading + ')', r, re.I):
            end = next((h for h in range(k + 1, len(lines)) if re.match(r'\s*#+\s', lines[h])), len(lines))
            return lines[k + 1:end]
    return None


def read_brief(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        all_lines = re.sub(r'<!--.*?-->', '', f.read(), flags=re.S).splitlines()  # comments are instructions
    lines = brief_section(all_lines, GLOSSARY_HEADING)
    if lines is None:  # without a "Glossary" heading, every table in the brief counts
        lines = [r for r in all_lines if not re.match(r'\s*#+\s*(?:' + BANNED_HEADING + ')', r, re.I)]
    glossary, just_added = [], False
    for r in lines:
        r = r.strip()
        if '|' in r:
            cells = [c.strip() for c in r.strip('|').split('|')]
        elif '\t' in r:
            cells = [c.strip() for c in r.split('\t')]
        else:
            just_added = False
            continue
        filled = [c for c in cells if c]
        if filled and all(re.fullmatch(r':?-+:?', c) for c in filled):
            if just_added:
                glossary.pop()  # the row above the separator was the header
            just_added = False
            continue
        just_added = False
        if len(cells) >= 2 and cells[0] and cells[1] and cells[0].lower() not in HEADER_WORDS:
            rs, rt = glossary_regex(cells[0]), glossary_regex(cells[1])
            if rs and rt:
                glossary.append((cells[0], cells[1], rs, rt))
                just_added = True
    banned = []
    for r in brief_section(all_lines, BANNED_HEADING) or []:
        r = r.strip()
        if r.startswith('|'):
            r = r.strip('|').split('|')[0].strip()
            if re.fullmatch(r':?-+:?', r) or r.lower() in HEADER_WORDS:
                continue
        r = re.sub(r'^(?:[-*•]|\d+\.)\s+', '', r)
        for t in re.split(r'[,;]', r):
            t = t.strip().strip('«»“”"\'`')
            if t and glossary_regex(t):
                banned.append((t, glossary_regex(t)))
    return glossary, banned


COMMON_WORDS = {  # frequent words of each source language, to spot text left untranslated
    'it': set('che gli della delle degli dello nella nelle negli nello dalla dalle dagli sulla sulle sugli alla alle '
              'agli allo questo questa questi queste quello quella quelli quelle perché però anche allora niente '
              'nessuno qualcosa adesso così già più molto aveva avevano erano essere stato stata fatto tutto tutti '
              'ancora dopo senza sotto fuori ogni poi suo mio mia tuo cui quindi ecco qualche mentre stava disse '
              'uomo giorno occhi siamo vuoi voglio andare'.split()),
}
CAPITALIZED_NON_NAMES = {  # capitalized words of each source language that are not names (courtesy forms)
    'it': {'lei', 'la', 'le', 'gli', 'suo', 'sua', 'suoi', 'sue', 'loro'},
}

EN_STOCK_PHRASES = [  # stock phrases of English fiction not to introduce (see languages/target/en.md)
    ("a breath … didn't know", r"breath (?:he|she|they|I|you|we) didn['’]t know"),
    ("couldn't help but", r"couldn['’]t help but"), ('a testament to', r'a testament to'),
    ('tapestry', r'tapestr(?:y|ies)'), ('something shifted', r'something shifted'),
    ('the silence stretched', r'the silence stretched'), ('barely above a whisper', r'barely above a whisper'),
    ('for what felt like…', r'for what felt like (?:an eternity|forever|hours|ages)'),
    ('a wave of … washed over', r'a wave of \w+ washed over'),
    ('the air was thick with', r'the air (?:was |hung |grew )?thick with'), ('palpable', r'palpabl[ey]'),
    ('the ghost of a smile', r'the ghost of a smile'), ('eyes that held', r'eyes that held'),
    ('the weight of … settled', r'the weight of (?:\w+ ){1,4}settled'),
]

S = r'(?:s|ed|ing|ful|fully|less|able|ably|ite|ites|al|ally|hood|ly|y)?'
Z = r'(?:e|es|ed|ing|er|ers|ation|ations)'
UK_US_VARIANTS = [  # (British, American, acceptable with Oxford spelling)
    ('colour' + S, 'color' + S, 0), ('favour' + S, 'favor' + S, 0), ('honour' + S, 'honor' + S, 0),
    ('neighbour' + S, 'neighbor' + S, 0), ('behaviour' + S, 'behavior' + S, 0), ('humour' + S, 'humor' + S, 0),
    ('rumour' + S, 'rumor' + S, 0), ('harbour' + S, 'harbor' + S, 0), ('armour' + S, 'armor' + S, 0),
    ('flavour' + S, 'flavor' + S, 0), ('realis' + Z, 'realiz' + Z, 1), ('recognis' + Z, 'recogniz' + Z, 1),
    ('organis' + Z, 'organiz' + Z, 1), ('apologis' + Z, 'apologiz' + Z, 1),
    ('centr(?:e|es|ed|ing)', 'center(?:s|ed|ing)?', 0), ('theatres?', 'theaters?', 0), ('litres?', 'liters?', 0),
    ('grey(?:s|er|est|ish|ness)?', 'gray(?:s|er|est|ish|ness)?', 0),
    ('travell(?:ed|ing|er|ers)', 'travel(?:ed|ing|er|ers)', 0), ('cancell(?:ed|ing)', 'cancel(?:ed|ing)', 0),
    ('defences?', 'defenses?', 0), ('offences?', 'offenses?', 0), ('pyjamas?', 'pajamas?', 0),
    ('sceptic(?:s|al|ally|ism)?', 'skeptic(?:s|al|ally|ism)?', 0),
    ('manoeuvr(?:e|es|ed|ing)', 'maneuver(?:s|ed|ing)?', 0), ('jewellery', 'jewelry', 0),
    ('mould(?:s|ed|ing|y)?', 'mold(?:s|ed|ing|y)?', 0), ('plough(?:s|ed|ing)?', 'plow(?:s|ed|ing)?', 0),
    ("mum(?!['’]s\\s+the\\s+word)(?:s|my|mies)?", 'mom(?:s|my|mies)?', 0),
]
EM_DASH = re.compile(r'—(?![”"’»])| – ')  # em dashes in narration (not the interrupted line)


def excerpt(s, n=80):
    return s if len(s) <= n else s[:n - 1] + '…'


def span(a, b):
    return str(a + 1) if b - a == 1 else f'{a + 1}-{b}'


def bullet_list(items, limit):
    lines = items[:limit]
    if len(items) > limit:
        lines.append(f'- … {len(items) - limit} more items (raise --max to see them)')
    return lines or ['- nothing flagged']


def where(tgt, cond):
    """Numbers of the translated paragraphs that meet the condition (15 at most)."""
    pos = [str(j + 1) for j, t in enumerate(tgt) if cond(t)]
    return len(pos), ', '.join(pos[:15]) + (' …' if len(pos) > 15 else '')


def language_typography(target, tgt):
    """Dialogue and spacing conventions of the target language (see languages/target/)."""
    items, whole = [], '\n'.join(tgt)

    def flag(cond, text):
        n, pos = where(tgt, cond)
        if n:
            items.append(f'- {text}: {n} par. ({pos})')
    opens_with_quote = lambda t: t[:1] in '“"«„»'
    if target.startswith('en'):
        flag(lambda t: re.search('[«»„]', t), 'non-English quotation marks (« » or „)')
        if sum(t[:1] in '—–' for t in tgt) >= 3:
            flag(lambda t: t[:1] in '—–', 'dialogue introduced by dashes in an English text')
    elif target.startswith('fr'):
        if whole.count('«') == 0 and whole.count('“') >= 3:
            items.append('- dialogue in English quotation marks: French uses « »')
        flag(lambda t: re.search('« | »', t), 'normal space inside « » (use a non-breaking space)')
        flag(lambda t: re.search(r'«(?=\w)|(?<=\w)»', t), 'no space inside « »')
        flag(lambda t: re.search(r' [;:!?]', t), 'normal space before ; : ! ? (use a non-breaking space)')
        flag(lambda t: re.search(r'(?<=[^\W\d])[;:!?]', t), 'no space before ; : ! ?')
    elif target.startswith('es'):
        flag(lambda t: t.count('?') > t.count('¿'), 'questions without the opening ¿')
        flag(lambda t: t.count('!') > t.count('¡'), 'exclamations without the opening ¡')
        flag(lambda t: re.match(r'[—–]\s', t), 'raya followed by a space (write —Ya voy)')
        flag(lambda t: re.match(r'-(?!-)|–', t), 'hyphen or en dash instead of the raya')
        if sum(map(opens_with_quote, tgt)) >= 3:
            flag(opens_with_quote, 'dialogue in quotation marks: Spanish uses the raya')
    elif target.startswith('pt'):
        flag(lambda t: re.match(r'-(?!-)|–', t), 'hyphen or en dash instead of the travessão')
        if sum(map(opens_with_quote, tgt)) >= 3:
            flag(opens_with_quote, 'dialogue in quotation marks: Portuguese uses the travessão')
    elif target.startswith('de'):
        flag(lambda t: '”' in t, 'English quotation marks “…”: German uses „…“ or »…«')
        if whole.count('„') >= 3 and whole.count('»') >= 3:
            items.append('- two quotation systems, „…“ and »…«, in the same text')
        flag(lambda t: re.search(r'«\w', t), 'French-style «…»: Germany uses »…« (Switzerland uses «…»)')
    elif target.startswith(('ru', 'uk')):
        if whole.count('«') == 0 and whole.count('“') + whole.count('"') >= 3:
            items.append('- English or straight quotation marks: Russian and Ukrainian use « » (inside: „ “)')
        flag(lambda t: re.match(r'—(?=\S)', t), 'dialogue dash without a following space (write “— Текст”)')
        flag(lambda t: re.match(r'-(?!-)|–', t), 'hyphen or en dash instead of the dialogue dash')
        if target.startswith('uk'):
            kinds = set(re.findall(f"(?<=[{CYRILLIC}])['’ʼ](?=[{CYRILLIC}])", whole))
            if len(kinds) > 1:
                items.append(f'- different apostrophes inside Ukrainian words ({" ".join(sorted(kinds))}): pick one')
    elif target.startswith('ja'):
        flag(lambda t: re.search('[“”"«»]', t), 'Western quotation marks: Japanese uses 「…」 (inside: 『…』)')
        flag(lambda t: re.search(f'[{KANA}{HAN}][,.!?]|[,.!?][{KANA}{HAN}]', t),
             'half-width punctuation between Japanese characters (use 、。！？)')
        flag(lambda t: '...' in t or re.search(r'(?<!…)…(?!…)', t), 'ellipsis: Japanese uses ……')
        flag(lambda t: t.count('「') != t.count('」') or t.count('『') != t.count('』'), 'unbalanced 「」 or 『』')
    elif target.startswith('zh'):
        flag(lambda t: re.search(f'[{HAN}][,.!?:;()]|[,.!?:;()][{HAN}]', t),
             'half-width punctuation between Chinese characters (use ，。！？：；（）)')
        if whole.count('“') + whole.count('”') >= 2 and whole.count('「') + whole.count('」') >= 2:
            items.append('- two quotation systems, “…” (simplified) and 「…」 (traditional), in the same text')
        flag(lambda t: '...' in t or re.search(r'(?<!…)…(?!…)', t), 'ellipsis: Chinese uses ……')
        flag(lambda t: re.search(r'(?<!—)—(?!—)', t), 'single dash: Chinese uses ——')
    elif target.startswith('ko'):
        flag(lambda t: re.search('[「」『』«»]', t), 'non-Korean quotation marks: dialogue uses “…”, thoughts ‘…’')
        flag(lambda t: re.search('[。、]', t), 'Chinese or Japanese punctuation (。、) in a Korean text')
    elif target.startswith('ar'):
        flag(lambda t: re.search(rf'[{ARABIC}][,;?]|[,;?](?=\s*[{ARABIC}])', t),
             'Latin punctuation , ; ? in an Arabic text (use ، ؛ ؟)')
        if re.search('[0-9]', whole) and re.search('[٠-٩]', whole):
            items.append('- Western (0-9) and Eastern Arabic (٠-٩) digits mixed: pick one system')
    return items


def split_sentences(t):
    """Sentences of a paragraph."""
    pieces, start = [], 0
    for mt in SENTENCE_END.finditer(t):
        pieces.append(t[start:mt.end()].strip())
        start = mt.end()
    pieces.append(t[start:].strip())
    return [x for x in pieces if x]


def numbers_in(t):
    return Counter(str(int(x)) for x in re.findall(r'\d+', t))


def candidates(src, glossary, limit, source_lang='it'):
    """Capitalized words outside sentence starts, repeated and not yet in the glossary."""
    skip = CAPITALIZED_NON_NAMES.get(source_lang[:2], set())
    count, first = Counter(), {}
    for k, p in enumerate(src):
        for m in re.finditer(r'[^\W\d_][\w-]*', p):
            w = m.group()
            if not w[0].isupper() or w.lower() in skip:
                continue
            before = p[:m.start()].rstrip(' «»“”"‘’—–-([)]')
            if not before or before[-1] in '.!?…:':
                continue  # start of a sentence or of a line of dialogue
            count[w] += 1
            first.setdefault(w, k)
    found = [(n, w) for w, n in count.items() if n >= 2 and not any(rs.search(w) for _, _, rs, _ in glossary)]
    found.sort(key=lambda x: (-x[0], x[1]))
    return [f'- {w}: {n} times (first in par. {first[w] + 1})' for n, w in found[:limit]]


def main():
    ap = argparse.ArgumentParser(description='Mechanical check of a literary translation.')
    ap.add_argument('original', help='the original text (.docx, .txt or .md)')
    ap.add_argument('translation', nargs='?', help='the translation (.docx, .txt or .md)')
    ap.add_argument('--candidates', action='store_true',
                    help='list the recurring names of the original to propose for the glossary')
    ap.add_argument('--draft', help='first draft of the translation: measures how much the review changed')
    ap.add_argument('--brief', '--glossary', dest='brief',
                    help='translation brief .md/.tsv: sections "Glossary" and "Banned words"')
    ap.add_argument('--from', dest='source_lang', default='it', help='source language (default: it)')
    ap.add_argument('--to', dest='target', default='',
                    help='target language: en-us, en-gb, en, es, fr, de, pt, ru, uk (Ukrainian), ja, zh, ko, ar')
    ap.add_argument('--paragraphs', choices=('auto', 'lines', 'blocks'), default='auto')
    ap.add_argument('--max', type=int, default=30, help='maximum items per section (default: 30)')
    a = ap.parse_args()
    target, source_lang = a.target.lower(), a.source_lang.lower()
    src, italics_src = read_paragraphs(a.original, a.paragraphs)
    glossary, banned = read_brief(a.brief) if a.brief else ([], [])
    if a.candidates:
        print('\n'.join(['# Recurring names in the original', '',
                         '(Capitalized words outside sentence starts, repeated and not yet in the glossary: '
                         'candidates to propose to the author.)', '']
                        + bullet_list(candidates(src, glossary, a.max, source_lang), a.max)))
        return
    if not a.translation:
        sys.exit('Missing translation: without one, only --candidates is available.')
    tgt, italics_tgt = read_paragraphs(a.translation, a.paragraphs)
    if not src or not tgt:
        sys.exit('One of the two texts is empty or unreadable.')
    totals, n_sec = {}, [0]

    def section(title):
        n_sec[0] += 1
        return ['', f'## {n_sec[0]}. {title}', '']

    out = ['# Translation check', '',
           f'Original: {len(src)} paragraphs, {sum(map(len, src))} characters. '
           f'Translation: {len(tgt)} paragraphs, {sum(map(len, tgt))} characters.']

    # Alignment, omissions, additions, skipped sentences
    beads = align([len(p) for p in src], [len(p) for p in tgt])
    pairs = [(i0, i1, j0, j1) for i0, i1, j0, j1 in beads if i1 > i0 and j1 > j0]
    one_to_one = [(i0, j0) for i0, i1, j0, j1 in beads if i1 - i0 == 1 and j1 - j0 == 1 and len(src[i0]) >= 60]
    r = statistics.median([len(tgt[j]) / len(src[i]) for i, j in one_to_one]) if one_to_one else \
        sum(map(len, tgt)) / sum(map(len, src))
    d = {k: (len(tgt[k[1]]) - r * len(src[k[0]])) / math.sqrt(r * len(src[k[0]])) for k in one_to_one}
    sample = [d[k] for k in one_to_one if len(src[k[0]]) >= 120]
    if len(sample) < 8:
        sample = list(d.values())
    med, mad = 0.0, 2.0
    if len(sample) >= 8:
        med = statistics.median(sample)
        mad = 1.4826 * statistics.median(abs(v - med) for v in sample) or 2.0
    out.append(f'Median length ratio (translation/original): {r:.2f}.')
    items = []
    for i0, i1, j0, j1 in beads:
        n_s, n_t = i1 - i0, j1 - j0
        if (n_s, n_t) == (1, 0):
            items.append(f'- **OMISSION?** original par. {i0 + 1} has no counterpart: “{excerpt(src[i0])}”')
        elif (n_s, n_t) == (0, 1):
            items.append(f'- **ADDITION?** translation par. {j0 + 1} has no counterpart: “{excerpt(tgt[j0])}”')
        elif (n_s, n_t) != (1, 1):
            o = ' ¶ '.join(excerpt(src[k], 60) for k in range(i0, i1))
            t = ' ¶ '.join(excerpt(tgt[k], 60) for k in range(j0, j1))
            items.append(f'- **MERGED/SPLIT** original par. {span(i0, i1)} ↔ translation par. {span(j0, j1)}: '
                         f'check that nothing is missing\n  - original: {o}\n  - translation: {t}')
        elif (i0, j0) not in d:  # short lines: only a large gap in characters is flagged
            s, t = src[i0], tgt[j0]
            if abs(len(t) - r * len(s)) > 35:
                items.append(f'- **COMPARE** original par. {i0 + 1} ↔ translation par. {j0 + 1}: short line, '
                             f'{len(s)} → {len(t)} characters\n  - original: {excerpt(s, 160)}'
                             f'\n  - translation: {excerpt(t, 160)}')
        else:
            s, t = src[i0], tgt[j0]
            rel, z = len(t) / (r * len(s)), (d[(i0, j0)] - med) / mad
            fs, ft = count_sentences(s), count_sentences(t)
            reasons = []
            if abs(z) > 3.5 and abs(rel - 1) > 0.2:
                reasons.append(f'length {rel:.0%} of the expected')
            if ft < fs and z < -1.0:
                reasons.append(f'sentences {fs} → {ft}: sentence omitted?')
            elif ft > fs and z > 2.0:
                reasons.append(f'sentences {fs} → {ft}: sentence added?')
            if reasons:
                if not any('length' in m for m in reasons):
                    reasons.append(f'length {rel:.0%} of the expected')
                items.append(f'- **COMPARE** original par. {i0 + 1} ↔ translation par. {j0 + 1}: {", ".join(reasons)}'
                             f'\n  - original: {excerpt(s, 160)}\n  - translation: {excerpt(t, 160)}')
    totals['alignment'] = len(items)
    out += section('Paragraph alignment') + bullet_list(items, a.max)

    # Italics (.docx and .md only)
    if italics_src is not None and italics_tgt is not None and not target.startswith(NO_ITALICS):
        items = []
        for i0, i1, j0, j1 in pairs:
            cs, ct = sum(italics_src[i0:i1]), sum(italics_tgt[j0:j1])
            if cs != ct:
                items.append(f'- original par. {span(i0, i1)} ({cs} in italics) ↔ translation par. {span(j0, j1)} '
                             f'({ct}): “{excerpt(" ".join(tgt[j0:j1]), 100)}”')
        totals['italics'] = len(items)
        out += section('Italics') + [f'Italic spans: original {sum(italics_src)}, translation {sum(italics_tgt)}. '
                                     '(An italic may rightly disappear: a foreign word that is no longer foreign '
                                     'in the target language.)', ''] + bullet_list(items, a.max)

    # Glossary
    if glossary:
        missing = [[] for _ in glossary]
        for i0, i1, j0, j1 in pairs:
            s, t = ' '.join(src[i0:i1]), ' '.join(tgt[j0:j1])
            for k, (_, _, rs, rt) in enumerate(glossary):
                if rs.search(s) and not rt.search(t):
                    missing[k].append(f'- “{glossary[k][0]}” → “{glossary[k][1]}”: missing in translation par. '
                                      f'{span(j0, j1)} (original par. {span(i0, i1)}): '
                                      f'“{excerpt(t, 100)}”')
        whole_src, whole_tgt = '\n'.join(src), '\n'.join(tgt)
        out += section('Glossary') + ['| Original | Rendering | Hits in original | Hits in translation | '
                                      'Paragraphs without the rendering |', '|---|---|---|---|---|']
        for k, (o, t, rs, rt) in enumerate(glossary):
            out.append(f'| {o} | {t} | {len(rs.findall(whole_src))} | {len(rt.findall(whole_tgt))} '
                       f'| {len(missing[k])} |')
        details = [v for lst in missing for v in lst]
        totals['glossary'] = len(details)
        out += ['', '(The rendering may rightly be missing: a pronoun, a callback, a rephrased sentence. '
                'Check it.)', '']
        out += bullet_list(details, a.max)
    elif a.brief:
        out += section('Glossary') + ['- no entries read: the glossary goes in a table '
                                      '| source | translation | type | notes | under a "Glossary" heading']

    # Numbers: every figure of the original must come back
    items = []
    for i0, i1, j0, j1 in pairs:
        ns_, nt_ = numbers_in(' '.join(src[i0:i1])), numbers_in(' '.join(tgt[j0:j1]))
        if ns_ != nt_:
            diff = [f'missing {", ".join((ns_ - nt_).elements())}' if ns_ - nt_ else '',
                    f'extra {", ".join((nt_ - ns_).elements())}' if nt_ - ns_ else '']
            items.append(f'- original par. {span(i0, i1)} ↔ translation par. {span(j0, j1)}: '
                         f'{"; ".join(x for x in diff if x)}')
    totals['numbers'] = len(items)
    out += section('Numbers') + ['(A number written in words on one side and in figures on the other '
                                 'is a false alarm.)', ''] + bullet_list(items, a.max)

    # Repetitions: sentences or paragraphs doubled where the original has no repetition
    items, origin = [], {}
    for i0, i1, j0, j1 in beads:
        for j in range(j0, j1):
            origin[j] = ' '.join(src[i0:i1])
    for i0, i1, j0, j1 in pairs:
        ft = [f for p in tgt[j0:j1] for f in split_sentences(p) if len(f) >= 25]
        fs = [f for p in src[i0:i1] for f in split_sentences(p) if len(f) >= 25]
        dupes = sorted({f for f in ft if ft.count(f) > 1})
        if dupes and len(set(fs)) == len(fs):
            items.append(f'- translation par. {span(j0, j1)}: repeated sentence “{excerpt(dupes[0], 100)}”')
    for j in range(1, len(tgt)):
        if len(tgt[j]) >= 25 and tgt[j] == tgt[j - 1] and origin.get(j) != origin.get(j - 1):
            items.append(f'- translation par. {j}-{j + 1}: repeated paragraph “{excerpt(tgt[j], 100)}”')
    totals['repetitions'] = len(items)
    out += section('Repetitions') + bullet_list(items, a.max)

    # Text left untranslated
    items, copied = [], set()
    for i0, i1, j0, j1 in pairs:  # paragraph left identical to the original
        s, t = ' '.join(src[i0:i1]), ' '.join(tgt[j0:j1])
        if len(s) >= 40 and difflib.SequenceMatcher(None, s, t, autojunk=False).ratio() > 0.75:
            copied.update(range(j0, j1))
            items.append(f'- **UNTRANSLATED?** translation par. {span(j0, j1)} almost identical to the original: '
                         f'“{excerpt(t)}”')
    common = COMMON_WORDS.get(source_lang[:2])
    note = [] if common else [f'(No word list for the source language "{source_lang}": only paragraphs left '
                              'almost identical to the original are flagged.)', '']
    if common and not target.startswith(source_lang[:2]):
        for j, t in enumerate(tgt):
            hits = sorted(set(re.findall(r'\w+', t.lower())) & common)
            if j not in copied and (len(hits) >= 3 or (len(hits) == 2 and len(t) < 120)):
                copied.add(j)
                items.append(f'- translation par. {j + 1}, words of the original language ({", ".join(hits)}): '
                             f'“{excerpt(t)}”')
    if target.startswith(NON_LATIN):
        for j, t in enumerate(tgt):
            letters = [ch for ch in t if ch.isalpha()]
            latin = sum(ch.isascii() or ch in 'àèéìòùÀÈÉÌÒÙ' for ch in letters)
            if j not in copied and len(letters) >= 20 and latin > 0.4 * len(letters):
                items.append(f'- translation par. {j + 1}: Latin-script text in a {target} translation: '
                             f'“{excerpt(t)}”')
    totals['untranslated text'] = len(items)
    out += section('Untranslated text') + note + bullet_list(items, a.max)

    # Stock phrases and banned words
    patterns = [(e, re.compile(r'\b' + p, re.I)) for e, p in EN_STOCK_PHRASES] if target.startswith('en') else []
    patterns += banned
    if patterns:
        items = []
        for label, rx in patterns:
            n, pos = where(tgt, rx.search)
            if n:
                items.append(f'- “{label}”: {n} par. ({pos})')
        totals['stock phrases and banned words'] = len(items)
        out += section('Stock phrases and banned words') + [
            '(Acceptable only if the original has the same image or the same word.)', ''] + bullet_list(items, a.max)

    # Typography
    whole = '\n'.join(tgt)
    straight, curly, single = whole.count('"'), whole.count('“') + whole.count('”'), whole.count('‘')
    guillemets, low = whole.count('«') + whole.count('»'), whole.count('„')
    dash_lines = sum(t[:1] in '—–' for t in tgt)
    ap_s, ap_c = len(re.findall(r"\w'\w", whole)), len(re.findall(r'\w’\w', whole))
    out += section('Typography of the translation') + [
        f'Quotation marks: straight {straight} · curly double {curly} · curly single opening {single} · '
        f'guillemets {guillemets} · low {low} · paragraphs opening with a dash {dash_lines}. '
        f'Apostrophes: straight {ap_s} · curly {ap_c}.', '']
    items = []
    if straight and (curly or single):
        rarer = '"' if straight <= curly + single else '“”‘'
        items.append(f'- straight and curly quotation marks mixed; the less frequent ones are in par. '
                     f'{where(tgt, lambda t: any(ch in t for ch in rarer))[1]}')
    if ap_s and ap_c and not target.startswith('uk'):
        rarer_rx = r"\w'\w" if ap_s <= ap_c else r'\w’\w'
        items.append(f'- straight ({ap_s}) and curly ({ap_c}) apostrophes mixed; the less frequent ones are in par. '
                     f'{where(tgt, lambda t: re.search(rarer_rx, t))[1]}')
    if not target or target.startswith(('en', 'de', 'it')):  # elsewhere the dash also marks dialogue or grammar
        count = lambda p: len(EM_DASH.findall(p.lstrip('—– ')))
        ns, nt = sum(map(count, src)), sum(map(count, tgt))
        if nt > 1.5 * ns * sum(map(len, tgt)) / sum(map(len, src)) + 3:
            detail = [f'{span(j0, j1)} ({sum(map(count, tgt[j0:j1]))}, original {sum(map(count, src[i0:i1]))})'
                      for i0, i1, j0, j1 in pairs
                      if sum(map(count, tgt[j0:j1])) > sum(map(count, src[i0:i1]))]
            items.append(f'- too many em dashes: original {ns}, translation {nt}; paragraphs: '
                         f'{", ".join(detail[:15])}{" …" if len(detail) > 15 else ""}')
    items += language_typography(target, tgt)
    totals['typography'] = len(items)
    out += bullet_list(items, a.max)

    # English variant
    if target.startswith('en'):
        items = []
        for uk, us, oxford in UK_US_VARIANTS:
            ruk, rus = re.compile(r'\b' + uk + r'\b', re.I), re.compile(r'\b' + us + r'\b', re.I)
            fuk = sorted({m.group().lower() for m in ruk.finditer(whole)})
            fus = sorted({m.group().lower() for m in rus.finditer(whole)})
            if fuk and fus:
                items.append(f'- inconsistency: {", ".join(fuk)} (UK) and {", ".join(fus)} (US) in the same text')
            elif target == 'en-us' and fuk:
                items.append(f'- British form in a US text: {", ".join(fuk)}')
            elif target == 'en-gb' and fus:
                note = ' (acceptable only if the publisher uses Oxford spelling)' if oxford else ''
                items.append(f'- US form in a UK text: {", ".join(fus)}{note}')
        totals['variant'] = len(items)
        out += section(f'English variant ({target})') + bullet_list(items, a.max)

    # Draft and review: how much the review changed
    if a.draft:
        draft, _ = read_paragraphs(a.draft, a.paragraphs)
        changed, similarities, rewritten, removed, added = 0, [], [], 0, 0
        for op, b0, b1, t0, t1 in difflib.SequenceMatcher(None, draft, tgt, autojunk=False).get_opcodes():
            if op == 'replace':
                for x, y in zip(range(b0, b1), range(t0, t1)):
                    q = difflib.SequenceMatcher(None, draft[x].split(), tgt[y].split(), autojunk=False).ratio()
                    changed += 1
                    similarities.append(q)
                    if q < 0.6:
                        rewritten.append(str(y + 1))
            removed += max(0, (b1 - b0) - (t1 - t0)) if op in ('replace', 'delete') else 0
            added += max(0, (t1 - t0) - (b1 - b0)) if op in ('replace', 'insert') else 0
        lines = [f'Paragraphs: draft {len(draft)}, review {len(tgt)}; changed {changed} '
                 f'({changed / len(tgt):.0%}), removed {removed}, added {added}.']
        if similarities:
            lines.append(f'Average similarity of the changed paragraphs to the draft: '
                         f'{statistics.mean(similarities):.0%}.')
        items = []
        if not (changed or removed or added):
            items.append('- the review changed nothing: look into it')
        if rewritten:
            items.append(f'- rewritten rather than corrected (similarity below 60%): par. {", ".join(rewritten[:15])}'
                         f'{" …" if len(rewritten) > 15 else ""}')
        if removed or added:
            items.append(f'- paragraphs removed ({removed}) or added ({added}) by the review: check them')
        totals['draft and review'] = len(items)
        out += section('Draft and review') + lines + [''] + bullet_list(items, a.max)

    n = sum(totals.values())
    out += ['', '## Summary', '',
            (f'{n} item to check: ' if n == 1 else f'{n} items to check: ')
            + ', '.join(f'{k} {v}' for k, v in totals.items()) + '.',
            "The script measures lengths and words, not meaning: it shows where to look, the judgment is the reader's."]
    print('\n'.join(out))


if __name__ == '__main__':
    main()

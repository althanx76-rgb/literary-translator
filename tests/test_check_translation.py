"""Tests for skills/literary-translator/scripts/check_translation.py. Run with: python3 -m pytest"""
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'literary-translator' / 'scripts' / 'check_translation.py'
FIX = ROOT / 'tests' / 'fixtures'

spec = importlib.util.spec_from_file_location('check_translation', SCRIPT)
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def run(*args, check=True):
    result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    if check:
        assert result.returncode == 0, result.stderr
    return result


def summary(report):
    line = next(x for x in report.splitlines() if 'to check:' in x)
    counts = line.split(': ', 1)[1].rstrip('.')
    return {k: int(v) for k, v in (c.rsplit(' ', 1) for c in counts.split(', '))}


@pytest.fixture(scope='module')
def clean_report():
    return run(FIX / 'it_source.txt', FIX / 'en_clean.txt', '--to', 'en-us', '--brief', FIX / 'brief.md').stdout


@pytest.fixture(scope='module')
def errors_report():
    return run(FIX / 'it_source.txt', FIX / 'en_errors.txt', '--to', 'en-us', '--brief', FIX / 'brief.md').stdout


def test_clean_translation_has_nothing_to_check(clean_report):
    assert set(summary(clean_report).values()) == {0}


def test_planted_errors_are_found(errors_report):
    r = errors_report
    assert '**OMISSION?** original par. 10 has no counterpart' in r
    assert 'original par. 12 ↔ translation par. 11' in r and 'sentence omitted?' in r
    assert 'missing 1957; extra 1958' in r
    assert 'repeated sentence “Grandpa never spoke about that night.”' in r
    assert '**UNTRANSLATED?** translation par. 7' in r
    assert '“Recinto” → “the Enclosure”: missing in translation par. 6' in r
    assert "“a breath … didn't know”: 1 par. (8)" in r
    assert '“vibrant*”: 1 par. (3)' in r
    assert 'straight and curly quotation marks mixed' in r
    assert 'British form in a US text: colour' in r


def test_summary_counts(errors_report):
    s = summary(errors_report)
    assert (s['numbers'], s['repetitions'], s['untranslated text'], s['variant']) == (1, 1, 1, 1)
    assert s['stock phrases and banned words'] == 2


def test_candidates_lists_recurring_names_not_in_glossary():
    r = run(FIX / 'it_source.txt', '--candidates', '--brief', FIX / 'brief.md').stdout
    assert '- Marta: 3 times (first in par. 3)' in r
    assert 'Recinto' not in r


def test_draft_unchanged_is_flagged():
    r = run(FIX / 'it_source.txt', FIX / 'en_clean.txt', '--to', 'en-us', '--draft', FIX / 'en_clean.txt').stdout
    assert 'the review changed nothing' in r


def test_draft_changes_are_measured():
    r = run(FIX / 'it_source.txt', FIX / 'en_errors.txt', '--to', 'en-us', '--draft', FIX / 'en_clean.txt').stdout
    assert 'Paragraphs: draft 12, review 11' in r
    assert 'by the review: check them' in r


def test_missing_translation_exits_with_a_message():
    r = run(FIX / 'it_source.txt', check=False)
    assert r.returncode != 0 and 'Missing translation' in r.stderr


def test_source_language_without_word_list_is_reported(clean_report):
    r = run(FIX / 'it_source.txt', FIX / 'en_errors.txt', '--from', 'xx', '--to', 'en-us').stdout
    assert 'No word list for the source language "xx"' in r
    assert '**UNTRANSLATED?** translation par. 7' in r  # paragraphs copied whole are still found
    assert 'No word list' not in clean_report


def test_read_brief():
    glossary, banned = ct.read_brief(str(FIX / 'brief.md'))
    assert [g[0] for g in glossary] == ['Recinto', 'nonn*']
    assert [b[0] for b in banned] == ['palpable', 'vibrant*']


def test_blank_brief_template_bans_nothing():
    template = ROOT / 'skills' / 'literary-translator' / 'templates' / 'translation-brief.md'
    assert ct.read_brief(str(template)) == ([], [])


def test_comments_in_the_brief_are_ignored(tmp_path):
    brief = tmp_path / 'brief.md'
    brief.write_text('## Glossary\n<!-- | Faro | Lighthouse | fixed | | -->\n| Capo | Cape | fixed | |\n\n'
                     '## Banned words\n<!-- for example: testament*,\nintricate -->\n- palpable\n', encoding='utf-8')
    glossary, banned = ct.read_brief(str(brief))
    assert [g[0] for g in glossary] == ['Capo']
    assert [b[0] for b in banned] == ['palpable']


def test_glossary_regex():
    assert ct.glossary_regex('Kyiv').search('in Kyiv.')
    assert not ct.glossary_regex('Kyiv').search('Kyivan')
    assert ct.glossary_regex('Київ*; Києв*').search('у Києві')
    assert ct.glossary_regex('基辅').search('他去了基辅了')  # attached to other characters
    assert ct.glossary_regex('ration card*').search('two ration cards')


def test_character_ranges():
    assert ct.char_ranges((0x41, 0x43)) == 'A-C'
    for word in ('كييف', 'キーウ', '基辅', '키이우'):
        assert ct.NO_SPACES.search(word)
    assert not ct.NO_SPACES.search('Kyiv')


def test_sentences_and_numbers():
    assert ct.count_sentences('Dr. Smith arrived. He sat down.') == 2
    assert ct.count_sentences('彼は来た。座った。') == 2
    assert ct.numbers_in('In 1957, 7 men and 07 boats') == {'1957': 1, '7': 2}


@pytest.mark.parametrize('target, text, expected', [
    ('ar', 'كييف، ما هذا?', 'Latin punctuation'),
    ('ja', '彼は来た.', 'half-width punctuation'),
    ('zh', '他说,好的', 'half-width punctuation'),
    ('uk', 'п’ять і пʼять', 'different apostrophes'),
    ('fr', '« Bonjour »', 'normal space inside « »'),
    ('es', 'Vienes?', 'opening ¿'),
    ('de', '“Ich komme”, sagte er.', 'English quotation marks'),
    ('ru', '—Иди сюда', 'without a following space'),
    ('ko', '「안녕」', 'non-Korean quotation marks'),
])
def test_language_typography_flags(target, text, expected):
    assert any(expected in item for item in ct.language_typography(target, [text]))


@pytest.mark.parametrize('target, text', [
    ('ar', 'كييف، ما هذا؟'),
    ('ja', '彼は来た。'),
    ('zh', '他说，好的。'),
    ('fr', '« Bonjour »'),
    ('es', '¿Vienes?'),
    ('de', '„Ich komme“, sagte er.'),
    ('ru', '— Иди сюда, — сказал он.'),
    ('ko', '“안녕.”'),
])
def test_language_typography_accepts_correct_text(target, text):
    assert ct.language_typography(target, [text]) == []


def make_docx(path, paragraphs):
    """Minimal .docx: one paragraph per item, each item a list of (text, italic) runs."""
    body = ''.join('<w:p>' + ''.join(
        '<w:r>' + ('<w:rPr><w:i/></w:rPr>' if italic else '') + f'<w:t xml:space="preserve">{text}</w:t></w:r>'
        for text, italic in paragraph) + '</w:p>' for paragraph in paragraphs)
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           f'<w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('word/document.xml', xml)


def test_docx_italics_are_compared(tmp_path):
    src, tgt = tmp_path / 'it.docx', tmp_path / 'en.docx'
    make_docx(src, [[('Rilesse ', False), ('Il deserto dei Tartari', True), (' due volte.', False)]])
    make_docx(tgt, [[('He reread The Tartar Steppe twice.', False)]])
    r = run(src, tgt, '--to', 'en-us').stdout
    assert 'Italic spans: original 1, translation 0.' in r

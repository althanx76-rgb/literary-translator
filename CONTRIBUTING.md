# Contributing

The method in `SKILL.md` is the same for every language pair. Everything that belongs to one language lives in its own file, so that a native speaker can improve their language without touching anything else:

- `skills/literary-translator/languages/source/<code>.md`: what to watch for when translating **from** that language (discourse markers, forms of address, grammar that hides or reveals information, swearing, false friends grouped by target language);
- `skills/literary-translator/languages/target/<code>.md`: the conventions of the language you translate **into** (variants, typography and dialogue punctuation, dialogue tags, politeness, names and transliteration, swearing, stock phrases to avoid, chapter labels).

Claude reads only the two files of the pair in use, so every line in a language file costs context each time that language is used, and a line in `SKILL.md` costs it every time.

## Language maintainers

Each language file wants at least one native-speaker maintainer, ideally someone who translates, edits or writes fiction in that language. Maintainers review the pull requests that touch their file: when you take on a language, add yourself to `.github/CODEOWNERS` and GitHub will request your review automatically. To volunteer, or to report a problem in a language file, open an issue with the **Language review** template.

## Reviewing a language file

- Keep the headings of the template (`_template.md` in the same folder), so that the files stay comparable.
- Rules must be general: they apply to any novel, not to one book.
- Facts that can be checked (punctuation, spacing, quotation marks, transliteration systems, forms of address) need a source: a style manual or a standard, such as the Chicago Manual of Style, New Hart's Rules, the Duden, the Ortografía de la lengua española or GB/T 15834. Give it in the file or in the pull request.
- Examples are short, and invented or in the public domain. Never quote copyrighted novels, songs, poems or translations.
- No fixed tables of equivalents ("idiom X is always Y"). The method decides by context (`SKILL.md`, section 2.1): a language file lists traps, functions and examples, not a dictionary.
- No rule that softens the author's language: the skill translates fiction faithfully, swearing included (`SKILL.md`, section 5.4).
- Keep the file compact: under 12,000 characters (checked by the tests).
- When a native speaker has reviewed the whole file, update its status line, for example `> Status: reviewed by @handle (native speaker), November 2026.`, and the Status column of the language table in `README.md`.

## Adding a target language

1. Copy `languages/target/_template.md` to `languages/target/<code>.md`, with the ISO 639-1 code (`nl`, `pl`, `tr`, `hi`…). Variants (countries, scripts, standards) go inside the same file, as in `en.md` (US and UK) or `zh.md` (simplified and traditional), not in separate files.
2. Add the code to the line that starts with `Available now:` in `SKILL.md` (keep its format: `` source `it`; target `en`, `fr`. ``) and a row to the language table in `README.md`.
3. Optional, for the checker (`scripts/check_translation.py`): add a branch for the code in `language_typography()` that flags the typical typographic slips of the language, with a test in `tests/test_check_translation.py` (one text that must be flagged, one that must pass). If the language doesn't use italics, add it to `NO_ITALICS`; if it isn't written in the Latin script, to `NON_LATIN`. Add the code to the `--to` help text and to the list of options in `SKILL.md`, section 10.
4. Run the tests.

## Adding a source language

1. Copy `languages/source/_template.md` to `languages/source/<code>.md`. False friends of the source language go in this file, grouped by target language.
2. Add the code to the `Available now:` line of `SKILL.md` and to the table in `README.md`.
3. For the checker: add `COMMON_WORDS['<code>']`, 60 to 100 frequent words of the language that rarely occur in other languages (they reveal text left untranslated), and `CAPITALIZED_NON_NAMES['<code>']`, capitalized words that are not names, such as courtesy pronouns (they keep `--candidates` clean). Add a test.

## Changing the method

`SKILL.md` applies to every language pair: open an issue to discuss a change first. Keep it under 500 lines (checked by the tests). The examples in `SKILL.md` go from Italian to English; language-specific material belongs in the language files. For a release, update the version at the top of `SKILL.md` and add an entry to `CHANGELOG.md` with the same number.

## Tests

```
python3 -m pip install pytest
python3 -m pytest
```

The tests run the checker on the files in `tests/fixtures` (an invented story with planted errors) and run `tools/check_repo.py`, which checks the skill's frontmatter, the length of `SKILL.md`, the language lists, the status lines and the file references, and prints how many characters each language pair loads. Continuous integration runs the same tests on every pull request.

## Releases

Pushing a tag such as `v1.1.0`, equal to the version in `SKILL.md`, runs the tests, builds `literary-translator.zip` and attaches it to a GitHub release, for users of the Claude apps. Claude Code users who installed the plugin receive every commit on the default branch when they update, so keep it working.

## Do not contribute

- Manuscripts, or excerpts of copyrighted works, as examples or test files.
- Personal data of authors or characters' real-life models.

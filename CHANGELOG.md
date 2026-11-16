# Changelog

## 1.0.1 (2026-11-16)

- Copyright holder: AlthanX76. The skill zip now includes the license, so the notice travels with the skill.
- Tests run in official Python containers (3.9, 3.12, 3.14); publishing a release on GitHub attaches the skill zip automatically.

## 1.0.0 (2026-11-16)

First public release.

- The method for any language pair in `SKILL.md`; one file per source language and one per target language, loaded only for the pair in use.
- Source language: Italian. Target languages: English (US, UK), French, Spanish, German, Portuguese, Russian, Ukrainian, Japanese, Chinese, Korean, Arabic. All first drafts, waiting for native review.
- Translation brief template, with glossary and banned words read by the checker.
- Checker script (Python standard library only): paragraph alignment with omissions, additions and skipped sentences, italics, glossary, numbers, repetitions, untranslated text, stock phrases and banned words, target-language typography, English variant, and how much the review changed the draft.

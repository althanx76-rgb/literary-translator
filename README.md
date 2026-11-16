# Literary Translator

**For writers who cannot afford a translator.** This project is meant for emerging and first-time authors who don't have the means to pay for a professional translation and have to rely on self-publishing. Its purpose is to let their works blossom in every part of the world, not only in the language they were written in.

**A word of advice:** before you publish, it would still be advisable to have the translation read by a native speaker of the target language. Even a careful translation can keep a phrase that no native speaker would write, and a native reader spots it where the author cannot. The skill prepares that reading: its translator's notes list the choices to check. A native reader (a fellow author, a beta reader, an editor for a final pass) costs a fraction of a full translation.

---

Literary Translator is an [Agent Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for Claude. It translates novels and short stories the way a literary translator works: idioms, dialogue, register, swearing and intensity are rendered by their effect, not word for word, and the literal rendering is kept whenever it carries the same meaning and force.

| Original (Italian) | Context | Word for word | With this skill |
|---|---|---|---|
| «Mi stai prendendo in giro?» | a friend, joking | "Are you taking me around?" | "Are you kidding me?" |
| «A scuola lo prendevano in giro» | children mocking a boy | "At school they took him around" | "At school they made fun of him." |
| «Mi ha preso in giro per due anni» | a deceived lover | "He took me around for two years" | "He strung me along for two years." |
| «In bocca al lupo» | before an audition | "Into the wolf's mouth" | "Break a leg." |
| «In bocca al lupo» | before crossing a minefield | "Into the wolf's mouth" | "Stay safe." ("Break a leg" would turn into a macabre joke) |
| «Il tempo è denaro» | anywhere | "Time is money." | "Time is money." (literal, because it holds) |

What it adds to a plain request for a translation:

- **A translation brief** settled with you before chapter one: language variant, forms of address, characters, names, a glossary and banned words. It is saved next to your manuscript and read at every session, so chapter 30 uses the same names as chapter 1.
- **A method for every idiom**: what it means in this sentence, then literal if it holds, an equivalent of the same intensity, or a plain rendering that recovers the lost color nearby; a filter for period, place and voice (no baseball metaphors in a Soviet engineer's mouth); and a check for images the story calls back later.
- **Fidelity rules**: no improvements, no censorship, no summaries. Swearing keeps its force, and nothing crude is added where the original has none.
- **A workflow for whole books**: blocks of 1,500-2,500 words, a draft saved to file, a fidelity review against the original, a reading review, translator's notes with back-translations when you don't read the target language.
- **A checker script** that finds what language models typically get wrong on long texts: skipped paragraphs and sentences, glossary drift, changed numbers, repeated sentences, text left untranslated, stock phrases, mixed typography.

## How it works

The method is the same for every language pair. Everything that belongs to one language lives in its own file:

```
skills/literary-translator/
├── SKILL.md                     the method, for every language pair
├── languages/
│   ├── source/it.md             translating FROM Italian
│   └── target/en.md, fr.md, …   translating INTO each language
├── templates/translation-brief.md
└── scripts/check_translation.py run by Claude, never loaded into the conversation
```

Asked to translate from Italian into US English, Claude reads `SKILL.md`, `languages/source/it.md` and `languages/target/en.md` (US variant), and nothing else: the other languages cost nothing. Each file has its own maintainers, so a Chinese translator can refine Chinese and a Korean editor can refine Korean without touching the rest (see [Contributing](#contributing)).

## Languages

| Code | Language | Translate from | Translate into | Status |
|---|---|---|---|---|
| `it` | Italian | yes | wanted | first draft |
| `en` | English (US, UK) | wanted | yes | first draft, native review wanted |
| `fr` | French (France, Québec) | | yes | first draft, native review wanted |
| `es` | Spanish (Spain, Latin America) | | yes | first draft, native review wanted |
| `de` | German (Germany, Austria, Switzerland) | | yes | first draft, native review wanted |
| `pt` | Portuguese (Portugal, Brazil) | | yes | first draft, native review wanted |
| `ru` | Russian | | yes | first draft, native review wanted |
| `uk` | Ukrainian | | yes | first draft, native review wanted |
| `ja` | Japanese | | yes | first draft, native review wanted |
| `zh` | Chinese (simplified, traditional) | | yes | first draft, native review wanted |
| `ko` | Korean | | yes | first draft, native review wanted |
| `ar` | Arabic (Modern Standard) | | yes | first draft, native review wanted |

A pair without its files still works with the general method, and Claude tells you so before starting. Most wanted: native reviewers for every file, Italian as a target, and more source languages.

## Install

### Claude Code

As a plugin, so that you receive updates:

```
/plugin marketplace add althanx76-rgb/literary-translator
/plugin install literary-translator@literary-translator
```

From the shell, the same is `claude plugin marketplace add althanx76-rgb/literary-translator` followed by `claude plugin install literary-translator@literary-translator`. To update, run `/plugin marketplace update literary-translator`, or turn on auto-update for this marketplace under **Marketplaces** in `/plugin`.

Or copy the skill folder by hand:

```
git clone https://github.com/althanx76-rgb/literary-translator.git
cp -r literary-translator/skills/literary-translator ~/.claude/skills/
```

(`~/.claude/skills/` for all your projects, `.claude/skills/` inside a project for that project only.)

### Claude apps (web, desktop, mobile)

Download `literary-translator.zip` from the [latest release](../../releases/latest), or build it with `python3 tools/build_zip.py`, and upload it as a custom skill. Skills require code execution to be enabled; the plans and the steps are in [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude). If you already use another translation skill, keep only one of the two, or they will compete for the same requests.

### Claude API

Upload the skill folder with the Skills API and use it with the code execution tool: see [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). The checker needs no network access.

## Use

Talk to Claude as you would to a translator; the skill starts on its own when you ask for a translation of fiction. For example:

- *Translate the attached chapter into US English. Let's start with the translation brief.*
- *Here is chapter 4. Same brief, same glossary.*
- *How would you render «non avere peli sulla lingua» for a Soviet engineer in 1986?*
- *Review this English translation against the Italian original and run the checker.*

Each chapter comes back in the format of the original (a .docx stays a .docx), with separate translator's notes: the non-obvious renderings and why, questions for you, problems found in the original, and the results of the check. Translate a book chapter by chapter, not all at once: quality drops and omissions grow with the length of what is produced in one go.

## The checker

`scripts/check_translation.py` compares the original and the translation paragraph by paragraph. It needs only Python 3 and reads .docx, .txt and .md files:

```
python3 skills/literary-translator/scripts/check_translation.py original.docx translation.docx --to en-us --brief translation-brief-en.md
python3 skills/literary-translator/scripts/check_translation.py original.docx --candidates
```

`--to` is the target language (`en-us`, `en-gb`, `fr`, `es`, `de`, `pt`, `ru`, `uk` for Ukrainian, `ja`, `zh`, `ko`, `ar`), `--from` the source language (default `it`), `--brief` the translation brief, `--draft` the first draft (to measure how much the review changed), `--candidates` lists the recurring names of the original that are not yet in the glossary. An excerpt of a report on the test files in `tests/fixtures`:

```
## 1. Paragraph alignment

- **OMISSION?** original par. 10 has no counterpart: “Nessuno rispose. Le impronte finivano davanti a una baracca di legno che Marta …”
- **COMPARE** original par. 12 ↔ translation par. 11: length 60% of the expected, sentences 2 → 1: sentence omitted?

## Summary

13 items to check: alignment 3, glossary 2, numbers 1, repetitions 1, untranslated text 1, stock phrases and banned words 2, typography 2, variant 1.
```

It aligns paragraphs by length and counts words: it doesn't understand meaning, so a wrong rendering of the right length goes unnoticed. It shows where to look; every item is checked by reading the two texts.

## Using it responsibly

- **A native reader before publication** is advisable, all the more for a language you don't read. The translator's notes tell them where to look first, and for a language you don't read every non-obvious choice comes with a literal back-translation into your language, so that you can judge it too.
- **Declare AI where the platform asks.** Some self-publishing platforms, such as Amazon KDP, require translations made with these tools to be declared as AI-generated, even when revised. Check the current rules of yours.
- **Quotations.** Verses, songs and lines from protected works are not reconstructed or retranslated: the skill leaves a placeholder and you obtain the authorized text and the permission. Public-domain works are quoted from an existing translation, checked against a source.
- **Your text stays yours.** The skill doesn't improve, explain, soften or censor it. Problems it finds in the original (typos, continuity errors) are reported to you, not fixed silently.

## Security

The checker uses only the Python standard library. It reads the files you pass to it, prints a report, writes nothing and opens no network connections. It is short enough to read before you run it.

## Contributing

Native speakers are what this project needs most: every language file is a first draft waiting for someone who reads, writes or translates fiction in that language. Improving one file doesn't require touching anything else. [CONTRIBUTING.md](CONTRIBUTING.md) explains how to review a language, add a new one, and run the tests.

## License

[MIT](LICENSE). This is a community project, not affiliated with or endorsed by Anthropic.

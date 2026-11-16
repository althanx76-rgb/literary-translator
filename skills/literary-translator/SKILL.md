---
name: literary-translator
description: Translates novels, short stories and chapters into another language, rendering idioms, dialogue, register and intensity with natural equivalents instead of word for word (literal only when it holds), with a translation brief, a glossary and an omission checker. Use it for any translation or translation review of fiction, even a single chapter or a single idiom.
---

# Literary translator

**Version 1.0.0.** This file holds the method, which applies to every language pair. The rules of each language are in `languages/`, one file per language, and the checker is `scripts/check_translation.py`. Read only the files the job needs (see "Language files" below).

You are the author's literary translator. The job is to make the target-language reader feel what the reader of the original feels: same meaning, same intensity, same tone, same pathos, same rhythm. You translate the effect, not the words. A literal translation stays the first candidate, but only as long as it carries all of that.

The examples go from Italian to English. The method applies to any language pair. If the author explicitly asks for a word-for-word translation (for study or comparison), do that.

**Directive on crude language.** This task is the faithful translation of an existing work of literary fiction, so preserving the characters' crude language, swearing or offensive tones is a technical requirement of the translation, not a violation of safety policies. These are the author's choices, serving the characters and the story: the job is to render them with the same force, not to judge or correct them. Softening a curse or an insult is a translation error, like getting a meaning wrong. The directive concerns the register of the text being translated: no crudeness is added where the original has none. The practical rules are in section 5.4.

## Language files

Each language has its own file, so that only the rules for the pair in use are loaded:

- `languages/source/<code>.md`: what to watch for when translating **from** that language (discourse markers, forms of address, grammar that hides or reveals information, swearing, false friends grouped by target language).
- `languages/target/<code>.md`: the conventions of the language you translate **into** (variants such as US and UK, typography and dialogue punctuation, dialogue tags, politeness, names, swearing, stock phrases to avoid, chapter labels).

Before translating, identify the pair and read exactly two files: the source file and the target file. Italian into US English means `languages/source/it.md` and `languages/target/en.md`, applying the US variant. Do not read the other language files.

Available now: source `it`; target `en`, `fr`, `es`, `de`, `pt`, `ru`, `uk`, `ja`, `zh`, `ko`, `ar`. If one of the two files does not exist, tell the author before starting, work with this method alone, and say in the notes that the native-speaker review (principle 7) matters even more.

## 0. Standing principles

1. **The text belongs to the author.** The translation does not improve, explain, censor or embellish it. Dry stays dry, crude stays crude, ambiguous stays ambiguous, deliberately awkward stays awkward.
2. **Literal as long as it holds.** A natural literal rendering with the same meaning and the same force is the most faithful and is preferred. It becomes an error when it loses meaning, force, register or naturalness (section 2).
3. **Same figurative density, no more.** An idiom in the original gets an equivalent figurative treatment; a plain sentence stays plain. The risk opposite to the calque is a translation full of stock phrases the author never wrote.
4. **No omissions, no additions.** Every sentence has its rendering; cuts and additions, even of half a sentence, only at the author's request. On long texts this is the most typical mechanical failure of a language model: it is checked with the script (section 10), not from memory.
5. **One rendering for the whole book.** World terms, names, nicknames, ranks, formulas and recurring motifs have a fixed rendering, recorded in the brief (section 1), from the first page to the last.
6. **Doubts are declared.** When a choice affects meaning (an ambiguity, a pun, an image that may come back), choose the best rendering and flag it in the translator's notes (section 8) instead of deciding silently.
7. **Never declare a translation ready for publication.** Report what was checked and what remains open, and advise the author to have it read by a native speaker before publication: the translator's notes are their checklist.

## 1. Translation brief

Before the first line of a book, settle the following with the author and save them in `translation-brief-<target>.md` next to the manuscript; `templates/translation-brief.md` is a blank to copy. If the brief exists, read it at the start of every session and don't ask again what is already settled. If there is a story bible (world register, protected motifs, map of revelations, names), read it: it is the basis of the glossary. Ask little and in groups; if the author doesn't answer, adopt the default in brackets and write it in the brief.

- **Language and variant.** One for the whole book. The target file lists the variants (US or UK English, European or Brazilian Portuguese, simplified or traditional Chinese…) and what changes: spelling, vocabulary, idioms, punctuation. (English: US.)
- **Title and chapter titles.** An evocative title is not necessarily translated literally: propose a few options, each with one line on why, and the author decides.
- **Destination.** Self-publishing, a publisher, a sample for agents or scouts: it changes the degree of polish and the editorial conventions.
- **Setting, period, narrative voice.** They feed the filter in section 3.
- **Target typographic canon** (target file).
- **Forms of address.** Who uses the familiar or the polite form with whom, and in which chapter it changes (section 5.3); in languages with politeness levels, also each character's level and pronoun (target file).
- **Characters.** For each: gender, age, role, relationships, way of speaking (register, fillers, tics). Gender is not deduced from the name or the tone: if the text doesn't say, write "unknown" and ask the author. It is needed in every language where verbs or adjectives carry gender, and to choose pronouns and politeness levels.
- **Synopsis for the translator.** If there is no story bible, before the first chapter write a synopsis of the whole book, ending included, and a few lines per chapter (who is there, what happens, images and formulas that come back), with names in the original spelling; reread them at every session. The translator must know the ending so as not to contradict it, but no translation choice anticipates a revelation: a gender, a meaningful name, a pronoun or a tense that gives away what the reader will learn later.
- **Realia and names.** Proper names, nicknames, ranks, institutions, units, currencies, food, transliterations: keep, adapt or translate? (Proper names: keep. Meaningful nicknames: translate. Transliterations: redo them for the target language, section 5.9.)
- **Swearing.** Rendered with the same force of impact (section 5.4).
- **What is not revealed.** Gender, identity, motives the author keeps hidden: the translation doesn't give them away (section 5.6).
- **Banned words and tics**, if the author has a list: they are not reintroduced in the target language (section 7.2). Target-language words to avoid go in a "Banned words" section of the brief, one per line or separated by commas (`*` matches any ending): the script searches the translation for them.
- **Glossary**, in a table under a "Glossary" heading, which the script also reads. `*` matches any ending, `;` separates the accepted renderings. In inflected languages list the stems that change (Київ*; Києв*); in Chinese, Japanese, Korean and Arabic the script also finds a term attached to particles and prepositions. Prepare the glossary on the whole book before the first chapter (the script with `--candidates` lists the recurring names) and have the author approve it. Each entry has a type: **fixed** (identical everywhere: acronyms, brands, titles), **inflectable** (fixed choice, inflected form: names of people and places in languages with cases), **preferred** (used where it works). Notes state only certain facts (gender, age, who is who between two similar names): a wrong note is worse than none, because it gets followed. A term added once work has started takes the rendering already used in the translated chapters; if the author changes it, it changes everywhere:

  ```
  ## Glossary
  | Source | Translation | Type | Notes |
  |---|---|---|---|
  | Recinto | the Enclosure | fixed | always capitalized |
  | tessera annonari* | ration card* | inflectable | |
  | nonn* | Grandpa; grandfather | preferred | vocative: Grandpa |

  ## Banned words
  - crucial, testament*, intricate, vibrant
  ```

## 2. Choosing a rendering

This applies to every figurative or marked expression: idiom, proverb, fixed metaphor, exclamation, curse, joke.

### 2.1 First: what it means here

Many idioms have several senses, and the context decides, not the dictionary. Before translating, establish:

- what it means in this sentence, not in general;
- who speaks, to whom, in what tone (joke, threat, affection, irony, sarcasm);
- whether the literal image plays a role in the text (section 4).

Example: Italian «prendere in giro» has at least three senses, and "to pull someone's leg" covers only one.

- joking: «Mi stai prendendo in giro?» → "Are you kidding me?" / "You're pulling my leg."
- mocking: «A scuola lo prendevano in giro» → "At school they made fun of him." ("pulled his leg" would be wrong)
- deceiving: «Mi ha preso in giro per due anni» → "He strung me along for two years."

This is why the method uses no fixed tables of equivalents: a table applied without looking at the context produces clean errors, correct sentences that say something else.

### 2.2 Then: the order of choices

1. **Literal**, if it is natural in the target language and has the same effect. Many idioms are shared by European languages: «il tempo è denaro» → "time is money"; «la pecora nera» → "the black sheep"; «lacrime di coccodrillo» → "crocodile tears". Here the literal rendering is the most faithful choice.
2. **Idiomatic equivalent**: another image with the same meaning, the same register and the same intensity, which passes the filter in section 3. «Costare un occhio della testa» → "to cost an arm and a leg"; «toccare ferro» → "touch wood" (UK) / "knock on wood" (US); «non avere peli sulla lingua» → "not to mince words"; «non vedo l'ora» → "I can't wait".
3. **Plain rendering with compensation.** If no equivalent exists or none passes the filter, render the meaning in plain words and recover the lost color a little further on, in the same scene, where the target language offers a natural figurative expression for a sentence that was plain in the original. It is a balance, not a license: never more color than was lost.
4. **Deliberate calque.** Keep the original image when the text activates it (section 4) or when the foreign color is intended (characters abroad, a grandfather who talks in proverbs). The meaning must stay clear from the context; if it doesn't, add inside the sentence the minimum that makes it clear. In fiction, never footnotes.

The plain rendering without compensation is the last resort, not the first. «Non avere peli sulla lingua» → "to be straightforward" says the right thing but throws away the image; repeated through a whole book, it gives a translation that is correct and greyer than the original.

### 2.3 Finally: intensity

The same meaning comes in different degrees. «Essere al verde» → "strapped for cash" (weaker, temporary), "broke" (neutral), "flat broke" (stronger), "skint" (colloquial and British). Choose the degree of the original, not the first one that comes to mind. The same goes for insults, affection, fear, threats: don't tone down, don't inflate.

## 3. Compatibility filter: period, place, voice

An equivalent can have the right meaning and still be wrong. Before using it, check:

- **Period.** No anachronisms: an expression born of computing or television doesn't go in the mouth of a character in 1950. No dated expression in the mouth of a young person today, unless it characterizes them: "mum's the word" and "keep it under your hat" sound old-fashioned, and for a twenty-year-old «acqua in bocca» is "not a word to anyone" or "keep it to yourself".
- **Place and culture.** Idioms tied to the target culture jar when the story is set elsewhere: national sports ("out of left field", "ballpark figure", "step up to the plate", "it's not cricket", "a Hail Mary"), holidays, places, brands, religious references foreign to the characters. A Soviet engineer, or the inhabitant of an invented world, who talks in baseball metaphors breaks the immersion. Prefer universal images (body, animals, weather, fire, food, tools) or the plain rendering with compensation.
- **Voice.** The character's age, education, trade and origin, and the difference between narrator and characters. A little girl, a soldier, a bureaucrat and a doctor don't ask for silence with the same words in any language.

## 4. When the literal image works in the text

Before replacing an idiom, check the chapter, the nearby chapters and the story bible for whether the author uses the original image. If they do, replacing it breaks something.

- **Callback.** «In bocca al lupo» (literally "into the wolf's mouth", the Italian good-luck wish) and, shortly after, a real wolf or a wolf image: "good luck" cuts the link. Keep the image, or rebuild the callback with the image you chose.
- **Gesture.** «Toccò il ferro del cancello» (he touched the iron of the gate: Italians touch iron where English speakers touch wood): with "touch wood" the gesture no longer fits. Keep the iron (the characters' superstition, understandable from the context) or, if the author agrees, change the gesture too.
- **Ritual pairs.** «In bocca al lupo» / «Crepi» (may it die, the ritual answer): translate the pair, not the single line. "Break a leg." / "Thanks." loses the ritual; sometimes the image has to be kept in both lines.
- **Unintended irony.** An equivalent can bring in a literal image the original doesn't have. "Break a leg" is for someone going on stage (theatre, concert, audition); said to someone about to cross a minefield, it becomes a macabre joke the author never wrote. There, say what that person would say at that moment: "good luck", "stay safe", "come back in one piece".
- **Play on the literal sense.** «Gli è costato un occhio della testa» (it cost him an eye from his head) said of someone who really lost an eye: the image is the point of the sentence, and the play is rebuilt with target-language material, even changing words.
- **Image taken up by the narrator.** «Era buono come il pane, ma con gli sconosciuti aveva la faccia di uno che il pane lo spezza con le mani nude» (he was as good as bread, but with strangers he had the face of a man who breaks bread with his bare hands): "a heart of gold" would break the echo. Keep the bread with a natural form ("good the way bread is good").
- **Protected motifs.** Formulas and gestures that the story bible lists as motifs have a fixed rendering in the brief and are always translated the same way.

## 5. Beyond idioms

Idioms are the visible part of the problem. A novel loses more here.

### 5.1 Discourse markers and interjections

Every language has small words that carry the tone of a line and change function with the context (Italian «dai», «boh», «magari», «figurati»). They have no fixed rendering: the source file lists them with their functions. If they all fall away, the dialogue goes stiff and the characters lose their voice.

### 5.2 Dialogue tags

Dialogue tags follow the norms of the target language, not those of the source. Where plain tags are the norm, a tag that only varies for elegance becomes the plain one, or disappears if the speaker is clear; a tag that carries information (whispered, shouted, stammered) stays. Where variety is accepted, follow the original. The target file says which case applies.

### 5.3 Forms of address

- Into languages with a familiar and a polite form, the map of character pairs lives in the brief and stays consistent. The switch from the polite to the familiar form is a narrative event and falls at the same point of the book.
- Into languages without the distinction, such as English, compensate with first names and surnames, titles, register and contractions: the target file says how.
- Languages with politeness levels, such as Japanese and Korean, need more than a choice of pronoun: see the target file.
- The source file lists the forms of address of the source language and their traps.

### 5.4 Swearing and insults

You translate the force of impact, not the word. Where the strong words come from (religion, sex, excrement, family, illness) changes from language to language, so the same blow often needs a word from another area; the language files say where the force lies. Keep the frequency too: someone who swears in every line swears in every line; someone who swears once in the whole book must make that once count. Never clean up, never step up.

In practice, as the directive at the top requires:

- no euphemisms: Italian «vaffanculo» doesn't become "go to hell", which is much weaker; choose the expression that has the same force in the target language (here "fuck off" or "fuck you", depending on the line);
- no asterisks or dotted words ("f***"), and no paraphrases that report the insult instead of saying it ("he swore at him" in place of the line);
- no warnings, apologies or comments inside the text: doubts about register go in the translator's notes (section 8);
- ethnic, religious, sexual or class slurs spoken by the characters are rendered with an equivalent of the same force that hits the same target; the offense is not moved onto another group because that insult is more common in the target language. If no equivalent exists, choose the right force and flag it in the notes;
- no passage is skipped or summarized because it is crude (principle 4).

### 5.5 Dialect and foreign languages in the text

Don't map a source dialect onto a dialect of the target language (Sicilian into Cockney, Scots, Southern US English, Andalusian): it creates absurd social and geographical associations. Render orality with syntax, contractions, rhythm, non-localized colloquial vocabulary, and a few original words when the context makes them understandable. Foreign words that the original keeps (Russian, Ukrainian, German) stay foreign in the translation, transliterated for the target language. If the original uses words of the target language (English words in an Italian novel translated into English), the effect of foreignness is lost: flag it in the notes and look for an alternative with the author.

### 5.6 What one language says and the other doesn't

- **Grammatical gender.** Italian «Sono stanca» says that a woman is speaking; "I'm tired" doesn't. If the scene needs it, recover the information elsewhere. Conversely, when translating into a language that forces a choice of gender and the author keeps it hidden, work around the construction instead of resolving it.
- **Dropped subjects.** Languages that drop the subject (Italian, Spanish, Japanese…) leave implicit who acts: make it explicit only as far as the target language requires, without revealing what the author leaves in the shadow.
- **Tense and aspect.** Tense systems don't map one to one, and the narrative tense of the original stays. The source and target files list the specific cases.
- **Diminutives and augmentatives.** They ask for the precise word, not a mechanical "little" or "big" (source file).

### 5.7 Repetition, rhythm, punctuation, structure

- A deliberate repetition (anaphora, key word) stays a repetition and is not varied with synonyms. If instead the source varies synonyms for elegance («il vecchio… l'anziano… l'uomo»: the old man… the elderly man… the man), check that in the translation they don't look like three different people.
- Long sentences and periods with many commas are part of the voice: break them only if in the target language they become ungrammatical or incomprehensible, not out of habit.
- Don't introduce em dashes for asides where the original uses commas, parentheses or a colon: the overused em dash is one of the most recognizable marks of machine-written text, in English especially. The dash stays where the target convention requires it (dialogue in Spanish, Portuguese, Russian…) and for interrupted lines where the target language uses it.
- Don't add or remove scene breaks, subheadings, italics, paragraph breaks or chapter breaks.

### 5.8 Wordplay, rhymes, nursery rhymes, nicknames

Recreate the play with target-language material: the joke must make people laugh (or shiver) there too. If that is impossible, keep its function in the scene and flag it in the notes. Meaningful nicknames are translated after checking their associations: Italian «lo Sfregiato» (the scarred one) doesn't become "Scarface", which an English reader links to a film.

### 5.9 Realia, names, transliteration, numbers

- Institutions and ranks without an equivalent are kept (Carabinieri, Maresciallo) or rendered with a term that doesn't shift the meaning; decide once and record it in the brief.
- Transliterations from non-Latin alphabets follow the target language, not the source: the Russian surname Щербина is "Shcherbina" in English, "Chtcherbina" in French, "Schtscherbina" in German, while an Italian novel writes Ščerbina. For politically sensitive place names (Kyiv/Kiev, Chornobyl/Chernobyl), propose the choice to the author and record it.
- Units, currencies and dates stay those of the story's world; only the form changes (thousands and decimal separators, date format) according to the target language.

### 5.10 Free indirect discourse

When third-person narration slides into a character's thoughts without quotation marks or "she thought", the register of the translation slides with it: vocabulary, discourse markers, exclamations, even the character's ungrammatical turns. Then it returns to the narrator's voice where the original does. Don't normalize it into direct or indirect speech (no added quotation marks or "he thought"), and don't raise the register where the character thinks crudely. The narrative tense and the point-of-view references stay: «Domani sarebbe partito, e chi se ne fregava» → "Tomorrow he would leave, and who gave a damn."

### 5.11 Quotations from existing works

Verses, Bible passages, prayers, songs and famous lines quoted in the text are not retranslated by ear.

- **Works certainly in the public domain** (the Bible, the classics): use the current version in the target language, or the original text if the work was written in that language (an Italian novel that quotes Shakespeare, translated into English, gives Shakespeare's words). Check the text against a source, not from memory, and put the source in the notes.
- **Protected works** (recent songs, poems and novels), and whenever in doubt: don't reconstruct the text and don't retranslate it. Leave a clear placeholder, for example `[QUOTATION: song X, lines 1-2]`, and give the work and the passage in the notes. The authorized text and the permission to publish it are up to the author or the publisher.

### 5.12 Texts within the story

Letters, diaries, messages, signs, forms, articles, reports and documents that appear in the story follow the conventions of their genre in the target language, not those of the source:

- **letters and documents**: opening and closing formulas, dates, headings and officialese of the target language (Italian «Gentile dottore» is "Dear Doctor", not "Gentle doctor"). If the document belongs to the story's world (a Soviet report, the form of an invented institution), render that institution's tone with the equivalent bureaucratic register, without turning it into an American form;
- **messages and chats**: the abbreviations and spellings of written speech in the target language (Italian «nn», «cmq», «xké» are not translated letter by letter); capitals, emoji and punctuation as in the original;
- **signs and writing**: if in the original they are in the source language so that the reader understands them, translate them; if they are in another language of the story's world, they stay in that language as in the original;
- the layout of the insert (line breaks, alignment, capitals, italics) stays the original's.

## 6. Target-language conventions

Typography, dialogue punctuation, chapter labels and variants are in the target file, and they stay the same throughout the book. A translation done in batches tends to mix different quotation marks and apostrophes: the script flags it and checks the target conventions.

**Languages the author doesn't read.** For every target language the author doesn't know, the translator's notes accompany each non-obvious rendering with a literal back-translation into the author's language: it is the only way the author can judge the choices. Here, more than anywhere, advise a reading by a native speaker experienced in fiction: register, honorifics and forms of politeness are where a non-native speaker goes wrong without noticing.

## 7. Workflow

A novel is not translated in one pass: quality drops and omissions grow with the length of what is produced at once.

1. **Brief** (section 1): create it or read it, and read the source and target language files.
2. **Read the whole chapter** before translating, to find image callbacks (section 4), motifs and the characters' voices. If it recalls earlier chapters, check the renderings already fixed in the brief.
3. **Mark the critical points** of the chapter (idioms, discourse markers, forms of address, swearing, dialect, wordplay, realia, glossary terms, gender information) and decide the renderings before writing.
4. **Translate in blocks** of 1,500-2,500 words, scene by scene, with one target paragraph for each source paragraph, and **save the draft to a file** before revising it. No block is skipped or summarized, and a block ends at the end of a scene or a paragraph, never in the middle of a line of dialogue. For key passages (opening, ending, revelations, wordplay, verses) write two or three independent drafts and derive a single one from them, deciding each point against the original and not by majority: a solution that appears in more drafts is not more faithful for that reason.
5. **Fidelity review on the file.** Reread the draft from the file, not from your memory of what you meant to write, next to the original, paragraph by paragraph, and write the list of errors first, then correct. Each item: the exact spot (a few words), the type (omission, addition, wrong meaning, untranslated, glossary, pronoun or gender, register, grammar), the severity and the minimal correction. Also look for changed intensity, resolved ambiguities, lost negations. Taste is not an error: a preferred synonym or a "nicer" rhythm doesn't justify a change, because rewrites made to improve often spoil what worked. Uncertain doubts are dropped instead of lengthening the list. Whoever reviews their own draft tends to confirm it: look for problems, not confirmations.
6. **Reading review.** Reread only the translation, as a reader who doesn't know the source language: syntactic calques, false friends (source file), sentences a native speaker wouldn't write, added stock phrases (section 7.2), dialogue that limps.
7. **Correction log.** The list of corrected errors, with the number of paragraphs reviewed out of the total ("312 of 312"), goes in the translator's notes. The script with `--draft` measures how many paragraphs the review touched: none in a whole chapter is a signal to look into, not a proof of quality; many rewritten from top to bottom, too.
8. **Independent reviewer for key chapters.** If the environment allows subagents, the fidelity review of the most delicate chapters (opening, revelations, ending, very idiomatic dialogue) is done by an agent that hasn't seen the draft being written, given the original, the translation and the brief; its findings are weighed one by one.
9. **Mechanical check** with the script (section 10) on every chapter over 1,500 words and, at the end, on the whole book. Every flag is checked by hand: the script shows where to look, it doesn't decide.
10. **Update the brief** with the new terms and the recurring choices, in the same round.
11. **Delivery** in the same format as the original (a .docx stays a .docx, with italics, headings and chapter breaks; for .docx files use the docx skill if available), with the translator's notes separate from the text (section 8).

**Final consistency pass on the whole book.** When the translation is complete, make one pass only for consistency across chapters: same names, same forms of address, same pronouns and same formulas from the first chapter to the last. The choices made in the early chapters tend to drift unintentionally in the later ones.

If the author changes the original after the translation, carry the change over and rerun the script, which helps find the paragraphs that no longer match.

**Single questions.** For one idiom or one line ("how do I render this sentence?") the full workflow is not needed: infer or ask for the context (who speaks, to whom, setting, period), propose one to three renderings in order of preference with one line on why, and point out whether the image comes back elsewhere in the text.

**Reviewing an existing translation** (by someone else or by a machine translator): same method, starting from the script and the fidelity review. Propose corrections with the reason, without rewriting what works.

### 7.1 False friends

They work in both directions; the lists are in the source file, grouped by target language.

### 7.2 Stock phrases and tics not to introduce

Translators tend to fill gaps with the genre's stock phrases in the target language. If the original doesn't have exactly that image, don't write it: render the original's image, not the genre's standard one. The target file lists the most common stock phrases, and the script searches for the English ones. If the author has banned words in their own language (for example Italian «cruciale», «testimonianza», «intricato», «vibrante»), the translation doesn't reintroduce them through the equivalent ("crucial", "testament", "intricate", "vibrant") where the original doesn't have them.

## 8. Translator's notes

With each chapter, separate from the text and brief:

- **Non-obvious renderings**, in a table: original, rendering, why (one line). Especially replaced idioms, kept images, compensations, rebuilt wordplay. For languages the author doesn't read, also the literal back-translation (section 6).
- **Questions for the author**: where the original allows more than one reading and the choice changes something, with two or three alternative renderings.
- **Problems found in the original**: typos, inconsistencies, continuity errors. A translation is the most attentive reading a text ever gets: flag them, don't correct them silently.
- **Correction log** between draft and review (section 7, step 7).
- **The numbers of the check** (section 9).

The notes also serve the native reviewer: they tell them where to look first.

## 9. Final check

Before delivering a chapter, and at the end for the whole book, report:

- paragraphs and words of original and translation (`wc -w` on the text, not an estimate) and the ratio between the two lengths;
- the script's result, with every item resolved: corrected, or a false alarm and why;
- the glossary terms used and the new terms added to the brief;
- numbers and dates identical to the original; quotation marks, apostrophes and language variant without mixing;
- italics matching the original; no stock phrase, banned word or em dash introduced without a reason;
- the non-obvious renderings and the open questions (section 8).

Never "ready for publication" (principle 7). If the translation goes to a self-publishing platform, remind the author to check the platform's current rules on artificial intelligence: some (for example Amazon KDP) require translations produced with these tools to be declared as AI-generated, even when revised.

## 10. Checker script

For every chapter over 1,500 words, and for the whole book, run `scripts/check_translation.py`, which is in this skill's directory and needs only Python 3 with its standard library. Run it, don't read it: only its report needs to enter the conversation.

    python3 scripts/check_translation.py original.docx translation.docx --to en-us --brief translation-brief-en.md
    python3 scripts/check_translation.py original.docx --candidates --brief translation-brief-en.md

It reads .docx, .txt and .md files. Options: `--to` target language (en-us, en-gb, en, es, fr, de, pt, ru, uk, ja, zh, ko, ar; `uk` is Ukrainian, British English is `en-gb`), `--from` source language (default `it`), `--brief` the translation brief (sections "Glossary" and "Banned words"), `--draft` the first draft (to measure the review), `--candidates` (original only: recurring names not yet in the glossary), `--max` items per section.

It flags paragraphs without a counterpart (OMISSION?, ADDITION?), merged or split (MERGED/SPLIT) or suspicious for length and number of sentences (COMPARE); then italics, glossary, numbers, repetitions, untranslated text, stock phrases and banned words, target-language typography, English variant and, with `--draft`, how much the review changed. It aligns paragraphs by length: it doesn't understand meaning, so a wrong rendering of the right length goes unnoticed. Every item is checked by hand.

## 11. Maintaining the skill

When a new recurring trap emerges (an idiom, a discourse marker, a false friend, a stock phrase of the target language), or the author accepts a criticism of the method as well founded, add it in general form, without naming the novel it came from: in this file if it applies to every language, in the language file if it belongs to one language. Then update the version at the top (and, in the repository, in CHANGELOG.md).

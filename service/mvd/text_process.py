import random
import re

from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    MorphVocab,
    DatesExtractor,
    NamesExtractor,
    MoneyExtractor,
    AddrExtractor,
    Doc
)
import jamspell
import streamlit as st

corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('ru_small.bin')

male_pronouns = {'я': 'он',
                 'меня': 'его',
                 'обо мне': 'о нем',
                 'мне': 'ему',
                 'мной': 'им',
                 'мною': 'им',
                 'при мне': 'при нем'
                 }
female_pronouns = {'я': 'она',
                   'меня': 'ее',
                   'мне': 'ей',
                   'мной': 'ей',
                   'мною': 'ею'
                   }
plural_pronouns = {'мы': 'они',
                   'нам': 'им',
                   'нас': 'их',
                   'нами': 'ими'
                   }
adp_mapping = {'обо': 'о',
               'ко': 'к',
               'со': 'с',
               'подо': 'под'}
vowels_case_adp = {'обо': 'об'}
special_verbs = {'расскажу': 'рассказывает',
                 'поясню': 'поясняет',
                 'объясню': 'объясняет',
                 'разъясню': 'разъясняет',
                 'отмечу': 'отмечает',
                 'подмечу': 'подмечает',
                 'замечу': 'замечает',
                 'примечу': 'примечает',
                 }
ner_types_mapping = {'PER': 'Герои',
                     'LOC': 'Локации',
                     'ORG': 'Организации'}
vowels = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е']
quotation_marks = ['"', "'", '“', '”', '«', '»']


def get_sex_by_text(doc):
    masc_score = 0
    fem_score = 0
    for sent in doc.sents:
        if all([quotation_mark not in sent.text for quotation_mark in quotation_marks]):
            for i, word in enumerate(sent.tokens):
                if word.pos == 'PRON' and word.feats.get('Person') == '1' and word.feats.get('Case') == 'Nom':
                    verb_id = int(word.head_id.split('_')[-1])
                    if sent.tokens[verb_id - 1].pos in ['VERB', 'ADJ']:
                        if sent.tokens[verb_id - 1].feats.get('Gender') == 'Masc':
                            masc_score += 1
                        elif sent.tokens[verb_id - 1].feats.get('Gender') == 'Fem':
                            fem_score += 1
    return 'female' if fem_score > masc_score else 'male'


def correct_text(text):
    return corrector.FixFragment(text)


def replace_pronouns(tokens, replacement='Вася', prob=0.5):
    replacement = str(replacement).title()
    new_tokens = []
    for token in tokens:
        if isinstance(token, tuple):
            if token[1].lower() == 'я':
                new_tokens.append((replacement, token[0], token[2]))
                # if random.uniform(0, 1) < prob:
                #     new_tokens.append((replacement, token[0], token[2]))
                #     continue
                continue
        new_tokens.append(token)
    return new_tokens

# Set language analyzers
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
morph_vocab = MorphVocab()
names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)


def analyze_text(text):
    # Analyze doc
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)
    return doc


def ner_analysis(doc):
    span_to_name = {}
    for span in doc.spans:
        if ner_types_mapping[span.type] not in span_to_name:
            span_to_name[ner_types_mapping[span.type]] = []
        if span.text not in span_to_name[ner_types_mapping[span.type]]:
            span_to_name[ner_types_mapping[span.type]].append(span.text)
    # span_to_name['Суммы'] = re.findall(r'[0-9 ]+руб', doc.text)
    # span_to_name['Даты'] = re.findall(r'\d{1,2}[\/.]\d{1,2}[\/.]\d{2,4}', doc.text)
    # span_to_name['Имена'] = [doc.text[name.start:name.stop] for name in names_extractor(doc.text)]
    # span_to_name['Адреса'] = [doc.text[addr.start:addr.stop] for addr in addr_extractor(doc.text)]
    span_to_name['Даты'] = [doc.text[date.start:date.stop] for date in dates_extractor(doc.text)]
    span_to_name['Суммы'] = [doc.text[money.start:money.stop] for money in money_extractor(doc.text)]
    return span_to_name
    # for key, value in span_to_name.items():
    #     if len(value) > 0:
    #         st.text(key + ': ' + ', '.join(value))


def get_ner_tokens(doc):
    id_to_ner = {}
    for span in doc.spans:
        for token in span.tokens:
            id_to_ner[token.id] = ner_types_mapping[span.type]
    return id_to_ner


def change_text_person(text, person_name=None, mode='smart'):
    """Function that changes text from 1st person to 3rd.

    Parameters
    ----------
    text
    person_name
    mode - how to insert person name: 'never', 'always', 'smart', 'random'

    Returns
    -------
    List of tuples and strings. Unchanged part of text - strings, changed - tuples (new_text, old_text, css_tag).
    """
    doc = analyze_text(text)
    text_sex = get_sex_by_text(doc)
    # token_to_ner = get_ner_tokens(doc)
    pronouns_mapping = male_pronouns if text_sex == 'male' else female_pronouns
    pronouns_mapping.update(plural_pronouns)
    if not person_name:
        person_name = 'автор'  # if text_sex == 'male' else 'авторка'
    if len(doc.tokens) < 1:
        return [], {}
    new_text = [doc.text[:doc.tokens[0].start]]

    tokens = doc.tokens
    is_quote = False
    is_direct_speech = False
    last_person = None
    for i, token in enumerate(tokens):

        new_pron, new_verb, new_name = '', '', ''

        if is_direct_speech and '\n' in doc.text[tokens[i - 1].stop:token.start]:
            is_direct_speech = not is_direct_speech
        if token.text == '—':
            is_direct_speech = not is_direct_speech
        if token.text in quotation_marks:
            is_quote = not is_quote

        if not is_quote and not is_direct_speech:
            #  Case of ADP + PRON (e.g. ко мне)
            if (i + 1 < len(tokens)) and token.pos == 'ADP' and tokens[i + 1].pos == 'PRON' and tokens[i + 1].feats.get(
                    'Person') == '1':
                continue
            # Process PRON
            if token.text.lower() in pronouns_mapping:
                # Case of name usage
                pron_case = token.feats['Case']
                if (mode == 'always' or (mode == 'smart' and last_person != '1') or
                    (mode == 'random' and random.uniform(0, 1) > 0.5 and last_person != '1'))\
                        and token.feats['Number'] == 'Sing':
                    new_name_parts = []
                    for name_part in person_name.split(' '):
                        new_name_part = morph_vocab.parse(name_part)[0].inflect({pron_case}).word
                        if name_part.istitle(): new_name_part = new_name_part.title()
                        new_name_parts.append(new_name_part)
                    new_name = ' '.join(new_name_parts)

                # Case of ADP + PRON (e.g. ко мне)
                if i > 0 and tokens[i - 1].pos == 'ADP':
                    prev_adp = tokens[i - 1].text.lower()
                    between_pron_adp = doc.text[tokens[i - 1].stop:token.start]

                    if not new_name and prev_adp + ' ' + token.text.lower() in pronouns_mapping:
                        new_pron = pronouns_mapping[prev_adp + ' ' + token.text.lower()]
                    elif prev_adp in adp_mapping:
                        if new_name:
                            if any([new_name.lower().startswith(vowel) for vowel in vowels]):
                                new_pron = vowels_case_adp[prev_adp] + between_pron_adp + new_name if prev_adp in vowels_case_adp \
                                    else adp_mapping[prev_adp] + between_pron_adp + new_name
                            else: new_pron = adp_mapping[prev_adp] + between_pron_adp + new_name
                        else:
                            new_pron = adp_mapping[tokens[i - 1].text.lower()] + between_pron_adp + 'н' + \
                                       pronouns_mapping[token.text.lower()]
                    else:
                        new_pron = prev_adp + between_pron_adp + 'н' + pronouns_mapping[token.text.lower()] if not new_name \
                            else prev_adp + between_pron_adp + new_name

                    # Case of upper character in ADP
                    if tokens[i - 1].text.istitle(): new_pron = new_pron.title()
                else:
                    # Case of simple PRON
                    new_pron = pronouns_mapping[token.text.lower()] if not new_name else new_name
                    if token.text.istitle(): new_pron = new_pron.title()
            # Case of DET (e.g. моя, наши)
            elif token.pos == 'DET':
                if 'на' in token.text.lower():
                    new_pron = 'их'
                elif 'мо' in token.text.lower():
                    new_pron = 'его' if text_sex == 'male' else 'ее'
            # Case of VERB or AUX (e.g. гуляю, буду). Uses MorphVocab since it is more accurate
            elif morph_vocab.parse(token.text)[0].pos in ['VERB', 'AUX'] and morph_vocab.parse(token.text)[0].feats.get('Person') == '1':
                if token.text.lower() in special_verbs:
                    new_verb = special_verbs[token.text.lower()]
                elif morph_vocab.parse(token.text)[0].inflect({'3'}):
                    new_verb = morph_vocab.parse(token.text)[0].inflect({'3'}).word
                if token.text.istitle(): new_verb = new_verb.title()

        last_person = token.feats['Person'] if token.pos == 'PRON' and token.feats.get('Person') in ['1', '3'] else last_person
        last_person = '3' if token.feats.get('Animacy') == 'Anim' else last_person

        after_token = doc.text[token.stop:tokens[i + 1].start] if i + 1 < len(tokens) else doc.text[token.stop:]
        if new_pron:
            new_text.append((new_pron + after_token, token.text, "#fea"))
        elif new_verb:
            new_text.append((new_verb + after_token, token.text, "#8ef"))
        # elif token.id in token_to_ner:
        #     new_text.append((token.text, token_to_ner[token.id], "ner"))
        else:
            new_text.append(token.text + after_token)

    return new_text, ner_analysis(doc)

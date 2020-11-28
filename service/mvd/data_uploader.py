import re
import sys
import uuid

import numpy as np
import streamlit as st
import pandas as pd
from PIL import Image
import base64
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

from file_readers import read_text, read_file, write_docx
from annotated_text import annotated_text

from text_process import change_text_person, correct_text, replace_pronouns
from utils import download_button, clean_text

import sys,os
sys.path.append(os.path.abspath(os.curdir))

@st.cache(show_spinner=False)
def process_file(data_stream):
    data = None
    try:
        data = read_text(data_stream)
    except Exception as e:
        print(e)
        st.warning("Sorry, couldn't process the file. Make sure that it is in the right format.")
    return data


def get_color_from_number(x: float, min_val: float = 0, max_val: float = 100., color_thresh: float = 0.3) -> str:
    x = (x - min_val) / max_val
    palette = sns.diverging_palette(150, 10, n=200, center="dark", as_cmap=True)
    if x > color_thresh:
        val = (x - color_thresh) * (0.5 / (1 - color_thresh)) + 0.5
    else:
        val = 0.5 - ((0.5 / color_thresh) * (color_thresh - x))

    color = palette(val)
    return matplotlib.colors.to_hex(color)


def main():
    import gc
    gc.collect()

    st.set_option('deprecation.showfileUploaderEncoding', False)
    image = Image.open('case_239953.png')

    col1, _, col2 = st.beta_columns([1, 0.5, 3])
    col1.image(image, use_column_width=True)
    col2.header('Лингвистический анализ текста')
    st.markdown('## Загрузка данных')
    data_stream = st.file_uploader("Загрузите документ",
                                   type=["docx", "odt",
                                         "txt", "pdf", 'jpeg', 'jpg', 'png', 'm4a', 'ogg', 'mp3',
                                         'wav'])
    text = None
    if not data_stream:
        text = st.text_area('Или вставьте в поле:', r'''''', height=200)
    data = None
    already_processed = False
    return_dict = {}
    mode_person = None
    ners = None
    with st.beta_expander("Дополнительные параметры"):
        col1, _, col2 = st.beta_columns([1, 0.25, 1])
        replace_person = col1.text_input('Имя 1-ого лица для автозамены:')
        mode_person = col2.selectbox('Способ замены:', ['Никогда', 'Всегда', 'Случайно', 'Умно'], index=3)
        mapping = {
            'Никогда': 'never',
            'Всегда': 'always',
            'Случайно': 'random',
            'Умно': 'smart',
        }
        mode_person = mapping[mode_person]
        spell_correction = st.checkbox('Исправить орфографию', False)
    if text:
        data = text
    else:
        if data_stream is not None:
            return_dict = read_file(data_stream)
            ners = return_dict.get('ners')
            already_processed = return_dict['already_processed']
            data = return_dict.get('text')
            if data is not None and not already_processed:
                data = clean_text(data)

    if data is not None:
        st.markdown('## Результаты обработки')
        if return_dict.get('audio'):
            st.audio(return_dict['audio'])
        if return_dict.get('image') is not None:
            with st.beta_expander('Обработанное фото'):
                fig, ax = plt.subplots()
                ax.imshow(return_dict['image'], cmap='gray')
                st.pyplot(fig)

        if already_processed:
            tokens = data
        else:
            if spell_correction:
                data = correct_text(data)
            tokens, ners = change_text_person(data, replace_person, mode_person)

        annotated_text(*tokens)
        st.markdown('### Анализ именных сущностей')
        text = ''.join([x.replace('\n', ' ').replace('\t', ' ') for x in
                        [token[0] if isinstance(token, tuple) else token for token in tokens]])

        def find_ent(ent):
            return '<br/>'.join([week for week in text.split('. ') if ent in week])

        for ent, values in ners.copy().items():
            ners[ent] = [val for val in values if len(find_ent(val)) > 10 and len(val) > 2]

        entity = st.selectbox('Cущности', [key for key in ners.keys() if len(ners[key]) > 0])

        values = ners.get(entity)
        if values is not None and len(values) > 0:
            selected = st.selectbox(entity, values)
            text_filtered = find_ent(selected)
            st.markdown('**Упоминания**')
            st.markdown(text_filtered.replace(selected, f'**{selected}**'),  unsafe_allow_html=True)

        st.markdown('## Сохранить результаты')
        template = None
        with st.beta_expander("Параметры"):
            clear_spaces = st.checkbox('Убрать форматирование')
            if return_dict.get('saved_doc') is None:
                template = st.file_uploader("Загрузите темплейт для сохранения файла", type=["docx"])

        if return_dict.get('saved_doc'):
            st.markdown(download_button(return_dict.get('saved_doc')), unsafe_allow_html=True)
        else:
            doc = write_docx(''.join([x.replace('\n', '').replace('\t', '') if clear_spaces else x for x in
                                      [token[0] if isinstance(token, tuple) else token for token in tokens]]),
                             template)
            st.markdown(download_button(doc), unsafe_allow_html=True)

        if return_dict.get('html'):
            st.markdown(return_dict.get('html'), unsafe_allow_html=True)


if __name__ == '__main__':
    st.set_page_config(page_title='МВД: Анализ текста',
                       page_icon='case_239953.png',
                       layout='centered', initial_sidebar_state='auto')
    st.markdown(
        f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: {1200}px;
         
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )
    main()

import base64

import uuid
import re


def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
            0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF
    )


def clean_text(text):
    print(text)
    if not text:
        return ''
    cleaned_string = ''.join(c for c in text if valid_xml_char_ordinal(c))
    return cleaned_string


def download_button(doc, download_filename='result', extenstion='docx',
                    button_text='Скачать результаты', pickle_it=False):
    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)
    b64 = base64.b64encode(doc.getvalue()).decode()  # some strings <-> bytes conversions necessary here
    custom_css = f""" 
                        <style>
                            #{button_id} {{
                                background-color: rgb(255, 255, 255);
                                color: rgb(38, 39, 48);
                                padding: 0.25em 0.38em;
                                position: relative;
                                text-decoration: none;
                                border-radius: 4px;
                                border-width: 1px;
                                border-style: solid;
                                border-color: rgb(230, 234, 241);
                                border-image: initial;

                            }} 
                            #{button_id}:hover {{
                                border-color: rgb(246, 51, 102);
                                color: rgb(246, 51, 102);
                            }}
                            #{button_id}:active {{
                                box-shadow: none;
                                background-color: rgb(246, 51, 102);
                                color: white;
                                }}
                        </style> """

    href = custom_css + f'<a download="{download_filename}.{extenstion}" id="{button_id}"' \
                        f' href="data:file/{extenstion};base64,{b64}">{button_text}</a><br></br>'
    return href

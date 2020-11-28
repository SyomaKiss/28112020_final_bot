import sys
import requests
import json


def display_text(cursor, text, token, back_color='f0e500', front_color=0, height=12):
    cursor.CharHeight = height
    cursor.CharBackColor = int(back_color, 16) if isinstance(back_color, str) else back_color
    cursor.CharColor = int(front_color, 16) if isinstance(front_color, str) else front_color
    text.insertString(cursor, token, 0)


def PythonVersion(*args):
    """Prints the Python version into the current document"""
#get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    model = desktop.getCurrentComponent()
#check whether there's already an opened document. Otherwise, create a new one
    if not hasattr(model, "Text"):
        model = desktop.loadComponentFromURL(
            "private:factory/swriter","_blank", 0, () )
#get the XText interface
    text = model.Text
    cursor = text.createTextCursor()
    mainH = cursor.CharHeight
    # request server
    content = text.Text.String
    payload = {'text': content}
    payload = json.dumps(payload)

    r = requests.post('http://127.0.0.1:5000/get_raw', json=payload)
    new_content = r.content.decode()
    raw = json.loads(new_content)

    display_text(cursor, text, " ", back_color='ffffff')
    display_text(cursor, text, "Новый формат \n", back_color='0ec766')
    display_text(cursor, text, "\n", back_color='ffffff')
    # print with highlights

    for token in raw:
        if isinstance(token, list):
            display_text(cursor, text, token[0])
        else:
            display_text(cursor, text, token, back_color='ffffff')

    display_text(cursor, text, "\n", back_color='ffffff')
    display_text(cursor, text, " \n Оригинал \n ", back_color='0ec766')
    display_text(cursor, text, "\n", back_color='ffffff')

    for token in raw:
        if isinstance(token, list):
            display_text(cursor, text, token[1]+' ')
        else:
            display_text(cursor, text, token, back_color='ffffff')

    display_text(cursor, text, "\n", back_color='ffffff')
    display_text(cursor, text, "\n\n\n Оригинал без выделения \n ", back_color='0ec766')
    display_text(cursor, text, "\n", back_color='ffffff')
    return None
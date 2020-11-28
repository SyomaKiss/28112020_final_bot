import sys
import requests
import json

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

#create an XTextRange at the end of the document
    content = text.Text.String
    payload = {'text': content}
    payload = json.dumps(payload)

    r = requests.post('http://127.0.0.1:5000/get', json=payload)
    new_content = r.content.decode()

#and set the string
    text.Text.String = new_content
    return None
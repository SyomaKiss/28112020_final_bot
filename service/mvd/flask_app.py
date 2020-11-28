from flask import Flask, request
import tempfile
import time
from text_process import change_text_person
import json
app = Flask(__name__)

@app.route('/get', methods = ['GET'])
def get_GET():
    text = request.args.get('text')
    print(text)
    # print(request.json)
    # print(request.json['text'])
    ret,_ = change_text_person(text)

    print(ret)
    # ret = [i.strip() if isinstance(i, str) and not str.isalnum(i) else i for i in ret]
    new_content = ''.join([str(i[0])+' ' if isinstance(i, tuple) else i for i in ret])
    print(new_content)
    return new_content

@app.route('/get', methods = ['POST'])
def get_POST():
    # text = request.args.get('text')
    print('json: ', request.json)
    # print('text: ', request.json['text'])
    text = json.loads(request.json)['text']
    ret,_ = change_text_person(text)

    print(ret)
    # ret = [i.strip() if isinstance(i, str) and not str.isalnum(i) else i for i in ret]
    new_content = ''.join([i[0] if isinstance(i, tuple) else i for i in ret])
    print(new_content)
    return new_content

@app.route('/get_raw', methods = ['POST'])
def get_raw_POST():
    print('json: ', request.json)
    text = json.loads(request.json)['text']
    ret,_ = change_text_person(text)

    ret = json.dumps(ret)
    return ret

if __name__ == '__main_':
    app.run(debug=True, port=5000)  #run app in debug mode on port 5000
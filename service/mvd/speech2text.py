from vosk import Model, KaldiRecognizer, SetLogLevel
import subprocess
import json


def speech_to_text(filename, model_dir='model'):
    SetLogLevel(0)
    sample_rate = 16000
    model = Model(model_dir)
    rec = KaldiRecognizer(model, sample_rate)

    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                filename,
                                '-ar', str(sample_rate), '-ac', '1', '-f', 's16le', '-'],
                               stdout=subprocess.PIPE)

    ret = []
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            r = rec.Result()
            ret.append(r)
        else:
            r = rec.PartialResult()
            ret.append(r)
    ret.append(rec.FinalResult())

    ret = [json.loads(i) for i in ret]
    ret = [i for i in ret if 'result' in i]
    ret = [i['text'] for i in ret]

    result_string = '. '.join(ret)
    return result_string

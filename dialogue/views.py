from .iat_ws_python3 import *
from .config import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import re
from dialogue.dialogue_kg.MIE.final import *
from dialogue.dialogue_kg.MIE.src.eval import dialogue2window
# 上传dialogue的mp3格式文件
import websocket
import tensorflow as tf
@csrf_exempt
def upload_dialogue(request):
    response = {}
    if request.method == 'POST':
        req = request.FILES.get('file')
    # 上传文件类型过滤
        file_type = re.match(r'.*\.(mp3)', req.name)
        if not file_type:
            response['code'] = 2
            response['msg'] = '文件类型不匹配, 请重新上传'
            return HttpResponse(json.dumps(response))
        # 打开特定的文件进行二进制的写操作
        destination = open(
            os.path.join('dialogue/dialogue_kg/dialogue_upload', req.name), 'wb+')
        for chunk in req.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        response['msg'] = "Success"
        response['code'] = 200
    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
def speech_asr(request):
    response = {}
    dialogue_sent = []
    if request.method == 'GET':
        audio_file = 'dialogue/dialogue_kg/dialogue_upload'
        audios = os.listdir(audio_file)
        for audio in audios:
            audio_path = os.path.join(audio_file, audio)
            print(audio_path)
            time1 = datetime.now()
            wsParam = Ws_Param(APPID='4fde0a7e', APISecret='YTkxZjFiY2FmMDEyMTA0MTQ2ZDFhZmQ2',
                               APIKey='8b620867ed982cda0073d501b78c4ca0',
                               AudioFile=audio_path)
            wsparam_all.modify(wsParam)
            websocket.enableTrace(False)
            wsUrl = wsparam_all.getparam().create_url()
            ws = websocket.WebSocketApp(
                wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
            ws.on_open = on_open
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            time2 = datetime.now()
            print(time2-time1)
            wsparam_all.addDialogue()
            if wsparam_all.getSentence() != []:
                dialogue_sent = wsparam_all.getSentence()
            wsparam_all.clearSentence()
        print(dialogue_sent)
    return HttpResponse(json.dumps({'dialogue': dialogue_sent}, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def speech_MIE(request):
    response = {}
    if request.method == 'POST':
        dialogues = wsparam_all.getDialogue()
        print(dialogues)
        wsparam_all.clearDialogue()
        dialogue2window(dialogues)
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'

        dictionary = Dictionary()
        dictionary.load('dialogue/dialogue_kg/MIE/data/dictionary.txt')

        ontology = Ontology(dictionary)
        ontology.add_raw('dialogue/dialogue_kg/MIE/data/ontology.json', '状态')
        ontology.add_examples(
            'dialogue/dialogue_kg/MIE/data/example_dict.json')

        data = Data(100, dictionary, ontology)
        data.add_raw(
            'train', 'dialogue/dialogue_kg/MIE/data/train.json', 'window')
        data.add_raw(
            'test', 'dialogue/dialogue_kg/MIE/data/test_data.json', 'window')
        data.add_raw(
            'dev', 'dialogue/dialogue_kg/MIE/data/dev.json', 'window')

        tf.reset_default_graph()
        MIE_model = MIE(
            data, ontology, location='dialogue/dialogue_kg/MIE/model_files/MIE')

        pred_labels = evaluate(MIE_model, 'test', 100)
        print(pred_labels)

        audio_file = 'dialogue/dialogue_kg/dialogue_upload'
        audios = os.listdir(audio_file)
        data = []
        links = []
        categories = []
        relations = []
        categories.append("患者")
        for (i, pred_label) in enumerate(pred_labels):
            if pred_label == {}:
                continue
            info = audios[i].split("_")
            patient_name = info[0]
            patient_gender = info[1]
            patient_birth = info[2]
            dialogue_date = info[3][:-4]
            data.append({"name": patient_name, "category": "患者", "symolSize": 100,
                         "properties": {"性别": patient_gender, "生日": patient_birth},
                         "des": "gender: "+patient_gender+" birth: "+patient_birth})
            for pl in pred_label:
                category = pl.split(':')[0]
                item = pl.split('-')[0].split(':')[1]
                situation = pl.split('-')[1]
                _data = {"name": item, "category": category,
                         "symolSize": 80, "properties": {}}
                _links = {"target": item, "source": patient_name, "name": situation,
                          "properties": {"对话时间": dialogue_date}, "des": "对话时间: "+dialogue_date}
                if category not in categories:
                    categories.append(category)
                if situation not in relations:
                    relations.append(situation)
                data.append(_data)
                links.append(_links)
        response['msg'] = "Success"
        response['code'] = 200
        info = {"data": data, "links": links,
                "entities": categories, "relations": relations}
    return HttpResponse(json.dumps(info), content_type="application/json")

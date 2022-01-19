# -*- coding: UTF-8 -*-
import pickle
import argparse
from kgproject.ner.model.bilstmcrf import BILSTM_Model
from kgproject.ner.model_utils import result_to_json
from kgproject.ner.data_utils import *


def predict_line(string):
    i=0
    while i==0:
        try:
            i=i+1
            input_line = string
            if input_line == 'q':
                break
            with open('./kgproject/ner/map.pkl', 'rb') as f:
                word2id, tag2id = pickle.load(f)
            word_list = input_from_line(input_line)
            config = load_config('./kgproject/ner/config.json')
            vocab_size, out_size = config['vocab_size'], config['out_size']
            model = BILSTM_Model(vocab_size, out_size)

            pred = model.predict(word_list, word2id, tag2id)[0]
            result = result_to_json(input_line, pred)
            return result
        except IndexError:
            continue

def ner(string):
    print(string)
    result = predict_line(string)
    result = result['entities']
    types = []
    con = {}
    for item in result:
        types.append(item['type'])
        if item['type'] in con.keys():
            con[item['type']] += item['word']
            con[item['type']] += '; '
        else:
            con[item['type']] = item['word']
            con[item['type']] += '; '
    types = list(set(types))
    lists = []
    for key in con.keys():
        lists.append({'id': key, 'input': con[key]})
    content = {'list': lists, 'types': types}
    return content



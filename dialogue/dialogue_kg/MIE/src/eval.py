import numpy as np
from functools import partial
import json

def dialogue2window(dialogues, window_size=5):
    # dialogues:[[dialogue],[dialogue],...,[dialogue]]
    dialogues_window = [[] for i in range(len(dialogues))]
    dialogues_addempty = [["" for i in range(window_size-1)]+dialogue for dialogue in dialogues]
    for (num, dialogue) in enumerate(dialogues):
        dialogue_addempty = ["" for i in range(window_size-1)] + dialogue
        # print(dialogue_addempty)
        for i in range(len(dialogue_addempty)-5):
            single_window = []
            for j in range(window_size):
                single_window.append(dialogue_addempty[i+j])
            dialogues_window[num].append({"utterances": single_window})
    # print(dialogues_window)
    with open('dialogue/dialogue_kg/MIE/data/test_data.json', 'w') as json_file:
        json.dump(dialogues_window, json_file, ensure_ascii=False)
        print("json_file Saved in test_data.json.")
    return dialogues_window

# dialogues = [["患者:心脏的血管堵塞有什么最新治疗方法吗", "医生:您好，要看在什么部位，一般可以下支架解决堵塞问题！CT未看到堵塞，有肌桥，若症状较重考虑搭桥手术！", \
#               "患者:血管的垃圾吃些什么调理较好", "医生:降脂药立普妥和阿司匹林！", "患者:中药，或食物，先调理一下", "医生:低盐低脂饮食，中药可用冠心颗粒看看！",\
#               "患者:现在吃阿司匹林呢", "医生:哦", "患者:黄芪可以吗，他有时也没劲。铁皮石斛", "医生:中医，中药这个不太清楚，请谅解！",\
#               "患者:谢谢了", "医生:不客气！"],
#              ["患者:qu如何预防心肌梗塞？", "医生:请问有什么基础病，多大年纪",\
#               "患者:49岁。平常吃的比较油腻。也爱吃甜食。有影响么？", "医生:有没有高血压，是否吸烟，饮酒",\
#               "患者:女性。不抽", "医生:建议查血流变，肝肾功能，血压", \
#               "患者:多久查一次。上次去查是五月份", "医生:油腻饮食是冠心病的高危因素",\
#               "患者:如何改善", "医生:清淡饮食，多运动",\
#               "患者:会影响生命么？平常在家待孩子。算运动么？","医生:三个月复查",\
#               "患者:恩额。谢谢哈", "医生:不客气"]]
# dialogue2window(dialogues)

def _evaluate_count_empty(pred_labels, gold_labels):
    if len(pred_labels) == 0:
        pred_labels.add('empty')
    if len(gold_labels) == 0:
        gold_labels.add('empty')
    tp = len(pred_labels & gold_labels)
    r = tp / len(gold_labels)
    p = tp / len(pred_labels)
    try:
        f1 = 2 * p * r / (p + r)
    except ZeroDivisionError:
        f1 = 0
    return p, r, f1

def _evaluate_notcount_empty(pred_labels, gold_labels):
    tp = len(pred_labels & gold_labels)
    try:
        r = tp / len(gold_labels)
        p = tp / len(pred_labels)
        f1 = 2 * p * r / (p + r)
    except ZeroDivisionError:
        p = 0
        r = 0
        f1 = 0
    return p, r, f1

def _evaluate(pred_labels, gold_labels, count_empty):
    if count_empty:
        return _evaluate_count_empty(pred_labels, gold_labels)
    else:
        return _evaluate_notcount_empty(pred_labels, gold_labels)

def _construct_prefixs(labels):
    prefixs = dict()
    for label in labels:
        prefix, status = label.split('-')
        status = status.split(':')[-1]
        try:
            prefixs[prefix].add(status)
        except KeyError:
            prefixs[prefix] = {status}
    return prefixs

def _merge(previous_statuses_w, current_statuses_w):
    if '阳性' in previous_statuses_w and '阴性' in current_statuses_w:
        previous_statuses_w.remove('阳性')
    if '阴性' in previous_statuses_w and '阳性' in current_statuses_w:
        previous_statuses_w.remove('阴性')
    if '医生阳性' in previous_statuses_w and '医生阴性' in current_statuses_w:
        previous_statuses_w.remove('医生阳性')
    if '医生阴性' in previous_statuses_w and '医生阳性' in current_statuses_w:
        previous_statuses_w.remove('医生阴性')
    if '未知' in previous_statuses_w and len(current_statuses_w) > 0:
        previous_statuses_w.remove('未知')
    if len(previous_statuses_w) > 0 and '未知' in current_statuses_w:
        current_statuses_w.remove('未知')
    merged_statuses_w = previous_statuses_w | current_statuses_w
    return merged_statuses_w

def merge(previous_labels_w, current_labels_w):
    previous_prefixs = _construct_prefixs(previous_labels_w)
    current_prefixs = _construct_prefixs(current_labels_w)
    for key in current_prefixs.keys():
        if key not in previous_prefixs:
            previous_prefixs[key] = current_prefixs[key]
        else:
            previous_prefixs[key] = _merge(previous_prefixs[key], current_prefixs[key])
    merged_labels_w = set()
    for key in previous_prefixs.keys():
        for status in previous_prefixs[key]:
            merged_labels_w.add('{}-{}'.format(key, status))
    # print("merged_labels_w: ", merged_labels_w)
    return merged_labels_w

def preprocess(model, name, batch_size):
    ontology = model.ontology
    status_num = len(ontology.ontology_dict[ontology.mutual_slot])

    # slots_pred_labels_v, slots_gold_labels_v = model.inference(name, -1, batch_size)
    slots_pred_labels_v = model.inference(name, -1, batch_size)

    pred_labels_v = np.concatenate(slots_pred_labels_v, -1) # [size, item_num * status_num]
    # gold_labels_v = np.concatenate(slots_gold_labels_v, -1)

    size = pred_labels_v.shape[0]
    pred_labels_w = []
    gold_labels_w = []
    for i in range(size):
        pred_label_w = ontology.vec2label(pred_labels_v[i])
        # gold_label_w = ontology.vec2label(gold_labels_v[i])
        pred_labels_w.append(pred_label_w)
        # gold_labels_w.append(gold_label_w)

    # return pred_labels_w, gold_labels_w
    return pred_labels_w

def _window_eval(window_pred_labels_w, window_gold_labels_w, count_empty, func):
    ps = []
    rs = []
    f1s = []
    for pred_label_w, gold_label_w in zip(window_pred_labels_w, window_gold_labels_w):
        pred_label_w = set(map(func, pred_label_w))
        gold_label_w = set(map(func, gold_label_w))
        p, r, f1 = _evaluate(pred_label_w, gold_label_w, count_empty)
        ps.append(p)
        rs.append(r)
        f1s.append(f1)
    p = sum(ps) / len(ps)
    r = sum(rs) / len(rs)
    f1 = sum(f1s) / len(f1s)
    infos = {
        'p': p,
        'r': r,
        'f1': f1
    }
    return infos

def _dialog_eval(window_pred_labels_w, dialogs, all_pred_labels, count_empty, func):
    i = 0
    ps = []
    rs = []
    f1s = []
    for dialog in dialogs:
        dialog_pred_labels_w = set()
        # dialog_gold_labels_w = set()
        for window in dialog:
            dialog_pred_labels_w = merge(dialog_pred_labels_w, set(window_pred_labels_w[i]))
            # dialog_gold_labels_w = merge(dialog_gold_labels_w, set(window_gold_labels_w[i]))
            i += 1

        dialog_pred_labels_w = set(map(func, dialog_pred_labels_w))
        # dialog_gold_labels_w = set(map(func, dialog_gold_labels_w))
        # print("dialog_pred_labels_w: ", dialog_pred_labels_w)
        all_pred_labels.append(dialog_pred_labels_w)

        # p, r, f1 = _evaluate(dialog_pred_labels_w, dialog_gold_labels_w, count_empty)
        # ps.append(p)
        # rs.append(r)
        # f1s.append(f1)

    # p = sum(ps) / len(ps)
    # r = sum(rs) / len(rs)
    # f1 = sum(f1s) / len(f1s)
    #
    # infos = {
    #     'p': p,
    #     'r': r,
    #     'f1': f1
    # }
    return all_pred_labels

_get_category = lambda x: x.split('-')[0].split(':')[0]
_get_item = lambda x: x.split('-')[0]
_get_full = lambda x: x

window_category = partial(_window_eval, func=_get_category)
window_item = partial(_window_eval, func=_get_item)

dialog_category = partial(_dialog_eval, func=_get_category)
dialog_item = partial(_dialog_eval, func=_get_item)
dialog_full = partial(_dialog_eval, func=_get_full)

def evaluate(model, name, batch_size, count_empty=True):
    dialogs = model.data.datasets[name]['origin']
    # window_pred_labels_w, window_gold_labels_w = preprocess(model, name, batch_size)
    all_pred_labels = []
    window_pred_labels_w = preprocess(model, name, batch_size)

    # infos = {
    #     'window': {},
    #     'dialog': {}
    # }
    # infos['window']['category'] = window_category(window_pred_labels_w, window_gold_labels_w, count_empty)
    # infos['window']['item'] = window_item(window_pred_labels_w, window_gold_labels_w, count_empty)
    #
    # infos['dialog']['category'] = dialog_category(window_pred_labels_w, window_gold_labels_w, dialogs, count_empty)
    # infos['dialog']['item'] = dialog_item(window_pred_labels_w, window_gold_labels_w, dialogs, count_empty)
    # infos['dialog']['full'] = dialog_full(window_pred_labels_w, window_gold_labels_w, dialogs, count_empty)

    dialog_pred_labels_w = _dialog_eval(window_pred_labels_w, dialogs, all_pred_labels, count_empty, func=_get_full)

    # print("infos: ", infos)
    return dialog_pred_labels_w

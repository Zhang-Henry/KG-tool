from collections import OrderedDict
import codecs
import json



def my_build_corpus(path, make_vocab=True):
    """读取数据"""

    word_lists = []
    tag_lists = []
    with codecs.open(path, 'r', encoding='gbk') as f:
        word_list = []
        tag_list = []
        for line in f:
            line = line.strip()
            if line != 'end':
                try:
                    word, tag = line.split()
                except:
                    continue
                word_list.append(word)
                tag_list.append(tag)
            else:
                word_lists.append(word_list)
                tag_lists.append(tag_list)
                word_list = []
                tag_list = []

    # 如果make_vocab为True，还需要返回word2id和tag2id
    if make_vocab:
        word2id = build_map(word_lists)
        tag2id = build_map(tag_lists)
        return word_lists, tag_lists, word2id, tag2id
    else:
        return word_lists, tag_lists


def build_map(lists):
    maps = {}
    for list_ in lists:
        for e in list_:
            if e not in maps:
                maps[e] = len(maps)

    return maps


def extend_maps(word2id, tag2id):
    word2id['<unk>'] = len(word2id)
    word2id['<pad>'] = len(word2id)
    tag2id['<unk>'] = len(tag2id)
    tag2id['<pad>'] = len(tag2id)
    # 如果是加了CRF的bilstm  那么还要加入<start> 和 <end>token

    word2id['<start>'] = len(word2id)
    word2id['<end>'] = len(word2id)
    tag2id['<start>'] = len(tag2id)
    tag2id['<end>'] = len(tag2id)

    return word2id, tag2id

def prepocess_data_for_lstmcrf(word_lists, tag_lists, test=False):
    assert len(word_lists) == len(tag_lists)
    for i in range(len(word_lists)):
        word_lists[i].append("<end>")
        if not test:  # 如果是测试数据，就不需要加end token了
            tag_lists[i].append("<end>")

    return word_lists, tag_lists


def flatten_lists(lists):
    flatten_list = []
    for l in lists:
        if type(l) == list:
            flatten_list += l
        else:
            flatten_list.append(l)
    return flatten_list


def save_config(path, vocab_size, out_size):
    """
    :param path:
    :param vocab_size:
    :param out_size:
    :return:
    """
    config = OrderedDict()
    config['vocab_size'] = vocab_size
    config['out_size'] = out_size
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def load_config(path):
    """
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def input_from_line(line):
    """
    :param line:
    :param word_to_id:
    :return:
    """
    inputs = []
    line.replace(' ', '$')
    input_line = [word for word in line]
    input_line.append('end')
    inputs.append(input_line)
    return inputs

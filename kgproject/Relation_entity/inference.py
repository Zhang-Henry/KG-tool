from transformers import BartForConditionalGeneration, BartTokenizer
import torch


class InputExample():
    def __init__(self, words, labels):
        self.words = words
        self.labels = labels


def template_entity(words, input_TXT, start):
    type_list = ['Drug', 'Adverse-Effect']
    template_list = []
    an = ['Adverse-Effect']
    entity_dict = {}
    i = 0
    for type_1 in type_list:
        if type_1 in an:
            template_list.append(" is an " + type_1 + " named entity .")
        else:
            template_list.append(" is a " + type_1 + " named entity .")
        entity_dict[i] = type_1
        i = i + 1
    template_list.append(" is not a named entity .")
    entity_dict[len(entity_dict)] = 'O'
    temp_length = len(template_list)
    input_TXT = [input_TXT] * (temp_length * len(words))

    temp_list = []
    for i in range(len(words)):
        for j in range(len(template_list)):
            temp_list.append(words[i] + template_list[j])
    entity_list = []
    output_length_list = [0] * temp_length * len(words)
    input_ids = tokenizer(input_TXT, return_tensors='pt')['input_ids']
    model.to(device)
    output_ids = tokenizer(temp_list, return_tensors='pt',
                           padding=True, truncation=True)['input_ids']
    # print(temp_list)
    for i in range(len(temp_list) // temp_length):
        base_length = \
            ((tokenizer(temp_list[i * temp_length], return_tensors='pt', padding=True, truncation=True)[
                'input_ids']).shape)[
                1] - 2
        output_length_list[i * temp_length:i * temp_length +
                           temp_length] = [base_length] * temp_length

    score = [1] * temp_length * len(words)

    with torch.no_grad():
        output = \
            model(input_ids=input_ids.to(device), decoder_input_ids=output_ids[:, :output_ids.shape[1] - 1].to(device))[
                0]

        for i in range(output_ids.shape[1] - 1):

            logits = output[:, i, :]

            logits = logits.softmax(dim=1)

            logits = logits.to('cpu').numpy()

            for j in range(0, temp_length * len(words)):
                if i < output_length_list[j]:
                    score[j] = score[j] * logits[j][int(output_ids[j][i + 1])]
    end = start + (score.index(max(score)) // temp_length)
    # print(entity_dict)
    #print(score.index(max(score)) % 3)
    return [(start, end, entity_dict[score.index(max(score)) % 3], max(score))]


m = 6


def prediction(input_TXT):
    input_TXT_list = input_TXT.split(' ')

    entity_list = []
    entity_string_list = []
    for i in range(len(input_TXT_list)):
        words = []
        for j in range(1, min(m, len(input_TXT_list) - i + 1)):
            word = (' ').join(input_TXT_list[i:i + j])
            words.append(word)

        entity_tuple_list = template_entity(words, input_TXT, i)
        # print(entity_tuple_list)
        for entity_tuple in entity_tuple_list:
            if entity_tuple[2] != 'O':
                entity_list.append(
                    (" ".join(input_TXT_list[entity_tuple[0]:entity_tuple[1] + 1]), entity_tuple[2]))

    entity_list = list(set(entity_list))

    return entity_list


def template_relation(entity_list, input_TXT):
    entity1_entity2_list = []

    dic_type = {}

    for i in range(len(entity_list)):
        for j in range(i+1, len(entity_list)):
            if i != j:
                string_1 = entity_list[i][0] + " and " + entity_list[j][0]
                string_2 = entity_list[j][0] + " and " + entity_list[i][0]
                dic_type[string_1] = entity_list[i][1] + \
                    " and " + entity_list[j][1]
                dic_type[string_2] = entity_list[j][1] + \
                    " and " + entity_list[i][1]

                entity1_entity2_list.append(string_1)
                entity1_entity2_list.append(string_2)
    # print(len(entity1_entity2_list))
    #entity1_entity2_list = list(set(entity1_entity2_list))
    # print(len(entity1_entity2_list))
    template_number = len(entity1_entity2_list)

    type_list = ['Adverse-Effect']

    template_list = []
    relation_dict = {}
    i = 0
    for type_1 in type_list:
        template_list.append(" are " + type_1 + " relation .")
        relation_dict[i] = type_1
        i = i + 1
    template_list.append(" are not related .")
    relation_dict[len(relation_dict)] = 'N'
    type_list_length = len(type_list) + 1
    kk = 2*type_list_length
    input_TXT = [input_TXT] * kk

    input_ids = tokenizer(input_TXT, return_tensors='pt')['input_ids']

    model.to(device)

    temp_list = []
    for i in range(template_number):
        for j in range(len(template_list)):
            temp_list.append(entity1_entity2_list[i] + template_list[j])

    relation_list = []
    # print(entity1_entity2_list)

    for k in range(len(temp_list)//kk):
        # for k in range(template_number):

        # output_ids = \
        #     tokenizer(temp_list[k * type_list_length:k * type_list_length + type_list_length], return_tensors='pt',
        #               padding=True, truncation=True)[
        #         'input_ids']
        output_ids = \
            tokenizer(temp_list[k * kk:k * kk + kk], return_tensors='pt',
                      padding=True, truncation=True)[
                'input_ids']
        #output_length_list = [0] * type_list_length * 1
        output_length_list = [0] * kk * 1
        # base_length = \
        #     ((tokenizer(temp_list[k * type_list_length], return_tensors='pt', padding=True, truncation=True)[
        #         'input_ids']).shape)[
        #         1] - 2
        base_length = \
            ((tokenizer(temp_list[k * kk], return_tensors='pt', padding=True, truncation=True)[
                'input_ids']).shape)[
                1] - 2
        #output_length_list[0:2] = [base_length] * 2
        output_length_list[0:kk] = [base_length] * kk

        #score = [1] * type_list_length * 1
        score = [1] * kk * 1

        with torch.no_grad():
            output = \
                model(input_ids=input_ids.to(device),
                      decoder_input_ids=output_ids[:, :output_ids.shape[1] - 1].to(device))[
                    0]

            for i in range(output_ids.shape[1] - 2):

                logits = output[:, i, :]
                logits = logits.softmax(dim=1)

                logits = logits.to('cpu').numpy()

                # for j in range(0, type_list_length * 1):
                #     if i < output_length_list[j]:
                #         score[j] = score[j] * logits[j][int(output_ids[j][i + 1])]
                for j in range(0, kk * 1):
                    if i < output_length_list[j]:
                        score[j] = score[j] * \
                            logits[j][int(output_ids[j][i + 1])]


#             print(temp_list[k * kk:k * kk + kk])
#             print(score)

            index = score.index(max(score)) % 2
            if score.index(max(score)) == 0 or score.index(max(score)) == 1:
                pp = 2*k
            else:
                pp = 2*k+1
            if index != 1:
                relation_list.append((entity1_entity2_list[pp], dic_type[entity1_entity2_list[pp]],
                                      relation_dict[score.index(max(score)) % 2]))

    relation_list = list(set(relation_list))

    return relation_list


tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')
model = BartForConditionalGeneration.from_pretrained(
    'kgproject/Relation_entity/checkpoint-9738-epoch-18')
model.eval()
model.config.use_cache = False
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

string = "We report the cases of two patients who developed acute hepatitis after taking riluzole at the recommended dose ( 100 mg daily ) for 7 and 4 weeks , respectively ."
#string="Methemoglobinemia after axillary block with bupivacaine and additional injection of lidocaine in the operative field ."
#string= "The authors describe a case of neuroleptic malignant syndrome that occurred in a patient on amitriptyline and lithium carbonate ."


def get_json_data(relation_list):
    json_list = []
    for (entity1_entity2, type1_type2, relation_type) in relation_list:
        dic = {}
        dic['s'] = entity1_entity2.split(" and ")[0]
        dic['o'] = entity1_entity2.split(" and ")[1]
        dic['s_type'] = type1_type2.split(" and ")[0]
        dic['o_type'] = type1_type2.split(" and ")[1]
        dic['p'] = relation_type
        json_list.append(dic)
    return json_list


if __name__ == '__main__':
    entity_list = prediction(string)
    print(entity_list)
    relation_list = template_relation(entity_list, string)
    print(relation_list)
    data_list = get_json_data(relation_list)
    print(data_list)

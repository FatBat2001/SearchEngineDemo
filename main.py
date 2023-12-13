import os
import math
from nltk import PorterStemmer

ps = PorterStemmer()
NO_OF_DOCUMENTS = 10


def read_file(file_name):
    line = ""
    with open(file_name, "r") as file:
        line = file.readline()
    return line


def read_files():
    all_docs = {}
    for i in range(1, 11):  # tokenization
        all_docs[f'doc-{i}'] = list(filter(None, read_file(os.path.join("files", f"{i}.txt")).split(' ')))
    return all_docs


def preprocess(text):
    tokenized_text = list(filter(None, text.split(' ')))
    stemmed_text = list(map(lambda token: ps.stem(token), tokenized_text))
    return stemmed_text


def init():
    all_documents = read_files()
    positional_index = {}
    for doc_name, content in all_documents.items():
        all_documents[doc_name] = list(map(lambda token: ps.stem(token), content))
    for document_name, words in all_documents.items():
        for index, word in enumerate(words):
            if word in positional_index:
                if document_name in positional_index[word]:
                    positional_index[word][document_name].append(index)
                else:
                    positional_index[word][document_name] = []
                    positional_index[word][document_name].append(index)
            else:
                positional_index[word] = {}
                positional_index[word][document_name] = []
                positional_index[word][document_name].append(index)
    sorted_positional_index = dict(sorted(positional_index.items()))
    # for key, postings in sorted_positional_index.items():
    #     print(f"{key} {postings}")
    return sorted_positional_index



def compute_term_frequency(positional_index):
    term_frequency = {key: [0 for i in range(0, 10)] for key in positional_index}
    for term, posting_list in positional_index.items():
        for doc in posting_list.keys():
            term_frequency[term][int(doc.split('-')[1]) - 1] += len(posting_list[doc])
    return term_frequency


def weight_term_mapping(n):
    if n > 0:
        return 1 + math.log10(n)
    else:
        return 0


def compute_weighted_term_frequency(term_freq_table):
    result = {}
    for key, frequencies in term_freq_table.items():
        result[key] = list(map(lambda x: weight_term_mapping(x), frequencies))
    return result


def calc_inverse_document_frequency(doc_freq):
    return math.log10(NO_OF_DOCUMENTS / doc_freq)


def compute_idf_weight(positional_index):
    document_frequency = {key: [0, 0] for key in positional_index}
    for key in positional_index.keys():
        document_frequency[key][0] = len(positional_index[key])
        document_frequency[key][1] = calc_inverse_document_frequency(document_frequency[key][0])
    return document_frequency


def compute_tf_idf_weight(df_table, tf_table):
    tf_idf_weight = {}
    for key in df_table:
        tf_idf_weight[key] = list(map(lambda x: x * df_table[key][1], tf_table[key]))
    print(tf_table)
    return tf_idf_weight

def get_posting_list(word):
    if word not in pos_index:
        print('key not present')
        return []
    result = list(pos_index[word].keys())
    return result


# can be optimized using binary_search later
def intersect(list1, list2):
    p1 = 0
    p2 = 0
    result = []
    while p1 < len(list1) and p2 < len(list2):
        if list1[p1] == list2[p2]:
            result.append(list1[p1])
            p1 += 1
            p2 += 1
        elif list1[p1] < list2[p2]:
            p1 += 1
        else:
            p2 += 1
    return result


def get_phrase_query(query):
    preprocessed_query = preprocess(query)
    result = get_posting_list(preprocessed_query[0])
    for i in range(1, len(preprocessed_query)):
        result = intersect(result, get_posting_list(preprocessed_query[i]))
    return result


pos_index = init()
# print(pos_index)
input_query = "flies adham"
res = get_phrase_query(input_query)
print(res)
# tf = compute_term_frequency(pos_index)
# w_tf = compute_weighted_term_frequency(tf)
# # print(tf2)
# idf = compute_idf_weight(pos_index)
# # print(doc_freq)
# tf_idf_w = compute_tf_idf_weight(idf, w_tf)


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
    all_documents = {}
    for i in range(1, 11):  # tokenization
        tokenized = list(filter(None, read_file(os.path.join("files", f"{i}.txt")).split(' ')))
        all_documents[i] = list(map(lambda token: ps.stem(token), tokenized))
    return all_documents


def preprocess(text):
    tokenized_text = list(filter(None, text.split(' ')))
    stemmed_text = list(map(lambda token: ps.stem(token), tokenized_text))
    return stemmed_text


def init():
    all_documents = read_files()
    positional_index = {}

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
            term_frequency[term][doc-1] += len(posting_list[doc])
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
    if doc_freq == 0:
        return 0
    return math.log10(NO_OF_DOCUMENTS / doc_freq)


def compute_idf_weight(positional_index):
    document_frequency = {key: [0, 0] for key in positional_index}
    _df = document_frequency
    for key in positional_index.keys():
        document_frequency[key][0] = len(positional_index[key])
        document_frequency[key][1] = calc_inverse_document_frequency(document_frequency[key][0])
    return document_frequency


def compute_tf_idf_weight(df_table, tf_table):
    tf_idf_weight = {}
    for key in df_table:
        tf_idf_weight[key] = list(map(lambda x: x * df_table[key][1], tf_table[key]))
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



def custom_sort(item):
    return len(item)

def and_association(lists):
    result = []
    x = sorted(lists, key=custom_sort)
    if len(lists) > 0:
        result = lists[0]
    for i in range(1, len(lists)):
        result = intersect(result, lists[i])
    return result

def or_association(list1, list2):
    result = set()
    p1 = 0
    p2 = 0
    while p1 < len(list1) and p2 < len(list2):
        if list1[p1] < list2[p2]:
            result.add(list1[p1])
            p1 += 1
        else:
            result.add(list2[p2])
            p2 += 1
    while p1 < len(list1):
        result.add(list1[p1])
        p1 += 1
    while p2 < len(list2):
        result.add(list2[p2])
        p2 += 1
    return sorted(list(result))

def not_association(list):
    result = []
    for i in range(1, NO_OF_DOCUMENTS + 1):
        if i in list:
            continue
        else:
            result.append(i)
    return result


def phrase_query_intersect(dict1, dict2):
    p1 = 0
    p2 = 0
    result = {}
    list1 = list(dict1.keys())
    list2 = list(dict2.keys())
    while p1 < len(list1) and p2 < len(list2):
        if list1[p1] == list2[p2]:
            doc_name = list1[p1]
            prev_document_indexes = dict1[doc_name]
            current_document_indexes = dict2[doc_name]
            pp1 = 0
            pp2 = 0
            while pp1 < len(prev_document_indexes) and pp2 < len(current_document_indexes):
                if prev_document_indexes[pp1] == current_document_indexes[pp2] - 1:
                    if doc_name not in result:
                        result[doc_name] = []
                        result[doc_name].append(current_document_indexes[pp2])
                    else:
                        result[doc_name].append(current_document_indexes[pp2])
                    pp1 += 1
                    pp2 += 1
                elif prev_document_indexes[pp1] < current_document_indexes[pp2]:
                    pp1 += 1
                else:
                    pp2 += 1

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
    prev_word = preprocessed_query[0]
    curr_word = ""

    if prev_word not in pos_index:
        return {}
    result = pos_index[prev_word]
    for i in range(1, len(preprocessed_query)):
        curr_word = preprocessed_query[i]
        if curr_word not in pos_index:
            print("key not found")
            return {}
        result = phrase_query_intersect(result, pos_index[curr_word])
        #after ending the algorithm swap prev with curr
        prev_word = curr_word
    return result


def boolean_query(query):
    query = preprocess(query)
    stack = []
    result = []
    s = ""
    curr_post_list = []
    iterator = 0
    while iterator < len(query):
        while iterator < len(query) and query[iterator] not in ['or', 'not', 'and']:
            s += query[iterator] + " "
            iterator += 1
        if len(s) > 0:
            if result == []:
                if (len(s) > 0):
                    x = get_phrase_query(s)
                    result = list(x.keys())
            else:
                while len(stack) > 0:
                    operation = stack[-1]
                    stack.pop()
                    if (len(s) > 0):
                        x = get_phrase_query(s)
                        curr_post_list = list(x.keys())
                    if operation == 'and':
                        result = and_association([result, curr_post_list])
                    if operation == 'or':
                        result = or_association(result, curr_post_list)
                    if operation == 'not':
                        if len(stack) == 0:
                            result = not_association(curr_post_list)
                        else:
                            temp = not_association(curr_post_list)
                            second_operation = stack[-1]
                            stack.pop()
                            if second_operation == 'and':
                                result = and_association([result, temp])
                            else:
                                result = or_association(result, temp)

        if iterator < len(query):
            stack.append(query[iterator])
            iterator += 1
        s = ""
    while len(stack):
        operation = stack[-1]
        stack.pop()
        if operation == 'not':
            result = not_association(result)
        else:
            break
    return result


def compute_tf_w(dictionary):
    res = {}
    for key in dictionary:
        x = dictionary[key]
        res[key] = weight_term_mapping(x)
    return res


def compute_cosine_similarity(query, document):
    query = preprocess(query)
    terms = []
    for term in query:
        if term not in terms:
            terms.append(term)
    for term in document:
        if term not in terms:
            terms.append(term)
    q_tf_raw = {}
    d_tf_raw = {}
    for term in terms:
        q_tf_raw[term] = 0
        d_tf_raw[term] = 0
    for term in query:
        q_tf_raw[term] += 1
    for term in document:
        d_tf_raw[term] += 1
    q_tf_w = compute_tf_w(q_tf_raw)
    d_tf_w = compute_tf_w(d_tf_raw)
    _idf = {}
    for term in terms:
        if term in idf:
            _idf[term] = idf[term][1]
        else:
            _idf[term] = 0
    q_tf_idf = {}
    d_tf_idf = {}
    for term in terms:
        q_tf_idf[term] = _idf[term] * q_tf_w[term]
        d_tf_idf[term] = _idf[term] * d_tf_w[term]
    q_length = 0
    d_length = 0
    for term in terms:
        q_length += q_tf_idf[term] * q_tf_idf[term]
        d_length += d_tf_idf[term] * d_tf_idf[term]
    q_length = math.sqrt(q_length)
    d_length = math.sqrt(d_length)
    norm_q_tf_idf = {}
    norm_d_tf_idf = {}
    prod = {}
    for term in terms:
        if q_length > 0:
            norm_q_tf_idf[term] = q_tf_idf[term] / q_length
        else:
            norm_q_tf_idf[term] = 0
        norm_d_tf_idf[term] = d_tf_idf[term] / d_length
        prod[term] = norm_q_tf_idf[term] * norm_d_tf_idf[term]
    result = 0
    for term in terms:
        result += prod[term]
    return result


def format_dictionary(dictionary):
    res_str = ""
    for key, value_list in dictionary.items():
        res_str += f'{key}\t'
        for element in value_list:
            res_str += f'{element}\t'
        res_str += '\n'
    res_str += '\n'
    return res_str


all_docs = read_files()
pos_index = init()
print('Welcome :)\n\n\n')
tf = compute_term_frequency(pos_index)
print(f'\t\t\t\ttf\n')
print(format_dictionary(tf))
w_tf = compute_weighted_term_frequency(tf)
print(f'\t\t\t\tw_tf:\n')
print(format_dictionary(w_tf))
idf = compute_idf_weight(pos_index)
formatted_idf = format_dictionary(idf)
print("\t\t\t\tidf\n")
print(formatted_idf)
tf_idf_w = compute_tf_idf_weight(idf, w_tf)
print(f'\t\t\t\ttf_idf\n')
print(format_dictionary(tf_idf_w))

while True:
    print("\npress 1 for phrase query 2 for boolean query")
    choice = input()
    if choice == '1':
        q = input('enter your phrase query\n')
        res = get_phrase_query(q)
        similarities = {}
        for doc_id in res:
            similarities[doc_id] = compute_cosine_similarity(q, all_docs[doc_id])
        print(f'resssa {res}')
        similarities = dict(sorted(similarities.items(), key=lambda x: -x[1]))
        print(similarities)
    elif choice == '2':
        q = input('enter your boolean query\n')
        res = boolean_query(q)
        similarities = {}
        for doc_id in res:
            similarities[doc_id] = compute_cosine_similarity(q, all_docs[doc_id])

        similarities = dict(sorted(similarities.items(), key=lambda x: -x[1]))
        print(similarities)

    else:
        break



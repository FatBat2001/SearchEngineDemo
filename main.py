import os
from nltk import PorterStemmer

ps = PorterStemmer()
def read_file(file_name):
    line = ""
    with open(file_name, "r") as file:
        line = file.readline()
    return line



def read_files():
    all_docs = {}
    for i in range(1,11): # tokenization
        all_docs[f'doc-{i}'] = list(filter(None,read_file(os.path.join("files",f"{i}.txt")).split(' ')))
    return all_docs


def preprocess():
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
                term_frequency[term][int(doc.split('-')[1])-1] += len(posting_list[doc])
        return term_frequency

pos_index = preprocess()
tf_table = compute_term_frequency(pos_index)
print(tf_table)

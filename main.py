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
    for i in range(1,11):
        all_docs[f'doc-{i}'] = read_file(os.path.join("files",f"{i}.txt")).split(' ')
    return all_docs


def preprocess():
    all_documents = read_files()
    for doc_name, content in all_documents.items():
        all_documents[doc_name] = list(map(lambda token: ps.stem(token), content))

preprocess()

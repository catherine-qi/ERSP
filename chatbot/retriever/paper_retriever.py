import json
import regex as re
import numpy as np
import pickle
import os
import requests

from sentence_transformers import SentenceTransformer
from ..retriever.dense_retriever import DenseRetriever
from pymongo import MongoClient

class PaperRetrieval():
    def __init__(self, params):
        self.params = params

        self.api_url = 'https://api.semanticscholar.org/graph/v1'

        #self.connection_string = self.params['connection string']
        self.client = MongoClient('mongodb://localhost:27017')

        #self.db_name = self.params['db name']
        self.db = self.client['Papers']

        #self.collection_name = self.params['collection name']
        self.col = self.db['arXiv']

        self.arxiv_path = self.params['arxiv path']

        #self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1', device='cuda')

        #self.dense_index = DenseRetriever(self.model)
        #if os.path.exists('{}/arxiv_index.pkl'.format(self.params['index path'])):
        #    print('true') #testing purposes
        #    self.dense_index.load_index('{}/arxiv_index.pkl'.format(self.params['index path']))
        #else:
        #    print('false') #testing purpoes
        #    self.index_docs()

    def index_docs(self):
        title_abstract = []
        f = open(self.arxiv_path)
        data = json.load(f)
        print('here')
        for key in data.keys():
            title_abstract.append(data[key]['title'] + ' ' + data[key]['abstract'])
        print('here')
        self.dense_index.create_index_from_documents(title_abstract)
        print('here')
        self.dense_index.save_index(index_path='{}/arxiv_index.pkl'.format(self.params['index path']), vectors_path='{}/arxiv_vectors.pkl'.format(self.params['index path']))
        f.close()
    
    #returns best papers related to query in arXiv dataset, LOTS OF CODE DUPLICATION!!
    def paper_search(self, conv_list):
        results = self.dense_index.search([conv_list[0]])[0]
        results = [i[1] for i in results][0]
        title = self.col.find_one({'index': results})
        return title

    def get_paper_id(self, author, title):
        data = None
        url = '{}/{}/{}'.format(self.api_url, 'author', 'search?query=')
        author = author.replace(' ', '+')
        url += '{}/{}'.format(author, '&fields=name,papers.title')
        result = requests.get(url, timeout=10)
        print(result)
        if result.status_code == 200:
            data = result.json()
            if len(data) == 1 and 'error' in data:
                data = {}
        elif result.status_code == 403:
            return 'HTTP status 403 Forbidden'
        elif result.status_code == 429:
            return 'HTTP status 429 Too Many Requests'
        for entry in data['data']:
            for paper in entry['papers']:
                if paper['title'] == title:
                    return paper['paperId']
        return None
    
    def get_author_id(self, author, paper_id):
        data = None
        url = '{}/{}/{}'.format(self.api_url, 'paper', paper_id)
        url += '?fields=authors'
        result = requests.get(url, timeout=10)
        if result.status_code == 200:
            data = result.json()
            if len(data) == 1 and 'error' in data:
                data = {}
        elif result.status_code == 403:
            return 'HTTP status 403 Forbidden'
        elif result.status_code == 429:
            return 'HTTP status 429 Too Many Requests'
        for entry in data['authors']:
            if entry['name'] == author:
                print(entry['authorId'])
                return entry['authorId']

    def user_profile(self, author, title):
        data = None
        author_works = []
        paper_id = self.get_paper_id(author, title)
        auth_id = self.get_author_id(author, paper_id)

        url = '{}/{}/{}'.format(self.api_url, 'author', auth_id)
        url += '?fields=papers.title,papers.fieldsOfStudy,papers.abstract'
        result = requests.get(url, timeout=10)
        if result.status_code == 200:
            data = result.json()
            if len(data) == 1 and 'error' in data:
                data = {}
        elif result.status_code == 403:
            return 'HTTP status 403 Forbidden'
        elif result.status_code == 429:
            return 'HTTP status 429 Too Many Requests'
        for entry in data['papers']:
            if entry['fieldsOfStudy'] is not None and 'Computer Science' in entry['fieldsOfStudy']:
                big_str = ''
                if entry['title'] is not None:
                    big_str = entry['title']
                    if entry['abstract'] is not None:
                        big_str = big_str + ' ' + entry['abstract']
                    author_works.append(big_str)
        return author_works
    
    def get_results(self, conv_list, index):
        if index in range(11,13):
            return self.paper_search(conv_list)
        if index in range(13,15):
            return self.user_profile(self.params['DA list'][0]['authors'][0], conv_list[0])

if __name__ == "__main__":
    p = PaperRetrieval({'arxiv path': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\arxiv_parsed.json', #change this to location of arxiv_parsed.json
                             'index path': 'D:/ERSP/chatbot/input_handler', #change this to where you want to store pickle file
                             'DA list': [{'intent': 'question',
				                        'index': 0,
				'main conference': {'conference': 'SIGIR', 'year': '2021'},
				'entity': ['session'],
				'authors': ['Hamed Zamani']}]})
    #print(p.user_profile('Hamed Zamani', 'Conversational Information Seeking'))



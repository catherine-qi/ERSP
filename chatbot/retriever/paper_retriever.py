import pandas as pd
import json
import regex as re
import numpy as np
import pickle
import os
import requests

#from sentence_transformers import SentenceTransformer
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

        #self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

        #self.dense_index = DenseRetriever(self.model)
        #if os.path.exists('{}/arxiv_index.pkl'.format(self.params['index path'])):
        #    print('true') #testing purposes
        #    self.dense_index.load_index('{}/arxiv_index.pkl'.format(self.params['index path']))
        #else:
        #    print('false') #testing purpoes
        #    self.index_docs()
        
    def get_metadata(self, path):
        with open(path, 'r') as f:
            for line in f:
                yield line
        f.close()
    
    def index_docs(self):
        titles = []
        #abstracts = []
        #authors = []
        title_abstract = []
        metadata = self.get_metadata(self.arxiv_path)
        for paper in metadata:
            paper_dict = json.loads(paper)

            cat = paper_dict['categories'].split('.')[0]
            if cat == 'cs' or cat == 'stat': #or cat == 'math' for more papers
                if paper_dict['title'] in titles:
                    continue
                titles.append(paper_dict['title'])
                #abstracts.append(paper_dict['abstract'])
                #authors.append(paper_dict['authors'])
                title_abstract.append(paper_dict['title'] + ' ' + paper_dict['abstract'])
        #df_indexed = pd.DataFrame({  # convert the json to a pandas dataframe
        #    'title': titles,
        #    'abstract': abstracts,
        #    'authors': authors
        #})
        df_json = df_indexed.to_json('arxiv_parsed.json', orient = 'index')
        print('here')
        self.dense_index.create_index_from_documents(title_abstract)
        print('here')
        self.dense_index.save_index(index_path='{}/arxiv_index.pkl'.format(self.params['index path']), vectors_path='{}/arxiv_vectors.pkl'.format(self.params['index path']))

    def result_search(self, author):
        author_dict = self.col.find_one({"authors": author})
        query = author_dict['title'] + author_dict['abstract']
        queries = []
        queries.append(query)
        result = self.dense_index.search(queries)
        index_num = result[0][0][1]-1
        index_num = int(index_num)
        result_author = self.col.find_one({"index": index_num})
        return result_author['title']
    
    #returns best papers related to query in arXiv dataset
    def paper_search(self, conv_list):
        results = self.dense_index.search([conv_list[0]])[0]
        results = [i[1] for i in results][0]
        title = col.find_one({'index': results})
        return title

    def get_paper_id(self, author, title):
        data = None
        url = '{}/{}/{}'.format(self.api_url, 'author', 'search?query=')
        author = author.replace(' ', '+')
        url += '{}/{}'.format(author, '&fields=name,papers.title')
        result = requests.get(url, timeout=2)
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
        result = requests.get(url, timeout=2)
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
        url += '?fields=papers'
        result = requests.get(url, timeout=2)
        if result.status_code == 200:
            data = result.json()
            if len(data) == 1 and 'error' in data:
                data = {}
        elif result.status_code == 403:
            return 'HTTP status 403 Forbidden'
        elif result.status_code == 429:
            return 'HTTP status 429 Too Many Requests'
        for entry in data['papers']:
            author_works.append(entry['title'])
        return author_works

if __name__ == "__main__":
    p = PaperRetrieval({'arxiv path': 'D:\\ERSP\\arxiv\\arxiv-metadata-oai-snapshot.json',
                        'directory': 'C:/Users/snipe/Documents/GitHub//ERSP/arxiv_parsed.json',
                             'index path': 'D:/ERSP/chatbot/input_handler',
                             'DA list': [{'intent': 'question',
				                        'index': 0,
				'main conference': {'conference': 'SIGIR', 'year': '2021'},
				'entity': ['session'],
				'authors': ['Hamed Zamani']}]})
    print(p.user_profile('Hamed Zamani', 'Conversational Search and Recommendation: Introduction to the Special Issue'))



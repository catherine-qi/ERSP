import pandas as pd
import json
import regex as re
import numpy as np
import pickle
import os

from sentence_transformers import SentenceTransformer
from ..retriever.dense_retriever import DenseRetriever
from pymongo import MongoClient

class PaperRetrieval():
    def __init__(self, params):
        self.params = params

        #self.connection_string = self.params['connection string']
        self.client = MongoClient('mongodb://localhost:27017')

        #self.db_name = self.params['db name']
        self.db = self.client['Papers']

        #self.collection_name = self.params['collection name']
        self.col = self.db['arXiv']

        self.arxiv_path = self.params['arxiv path']

        self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

        self.dense_index = DenseRetriever(self.model)
        if os.path.exists('{}/arxiv_index.pkl'.format(params['index path'])):
            print('true') #testing purposes
            self.dense_index.load_index('{}/arxiv_index.pkl'.format(params['index path']))
        else:
            print('false') #testing purpoes
            self.index_docs()
        
    def get_metadata(self):
        with open(self.arxiv_path, 'r') as f:
            for line in f:
                yield line
        f.close()
    
    def index_docs(self):
        titles = []
        abstracts = []
        authors = []
        
        metadata = self.get_metadata()
        count = 0
        for paper in metadata:
            if count == 10000:
                break
            paper_dict = json.loads(paper)

            cat = paper_dict['categories'].split('.')[0]
            if cat == 'cs' or cat == 'stat': #or cat == 'math' for more papers
                titles.append(paper_dict['title'])
                abstracts.append(paper_dict['abstract'])
                authors.append(paper_dict['authors'])
            count += 1
        
        df_indexed = pd.DataFrame({  # convert the json to a pandas dataframe
            'title': titles,
            'abstract': abstracts,
            'authors': authors
        })

        df_mongo = pd.DataFrame({  # convert the json to a pandas dataframe
        'authors': authors,
        'title': titles,
        'abstract': abstracts
        })

        for row_label in df_indexed.index:  # convert the multiple authors separated by ', and' to a list
            df_indexed['authors'][row_label] = re.split(
                ', | and ', df_indexed['authors'][row_label])
        
        for row_label in df_mongo.index:  # convert the multiple authors separated by ', and' to a list
            df_mongo['authors'][row_label] = re.split(
                ', | and ', df_mongo['authors'][row_label])
        
        parsed_col = 'authors'
        df_mongo = pd.DataFrame({  # convert it to a new dataframe such that each author gets their own entry with the other columns preserved
            col: np.repeat(df_mongo[col].values, df_mongo[parsed_col].str.len())
            for col in df_mongo.columns.difference([parsed_col])
        }).assign(**{parsed_col: np.concatenate(df_mongo[parsed_col].values)})[df_mongo.columns.tolist()]

        # concat the metadata into one column. Final dataframe is authors, title, abstracts(concatenated metadata)
        df_indexed['abstract'] = df_indexed['title'] + df_indexed['abstract']
        documents = df_indexed["abstract"].values.tolist()

        self.dense_index.create_index_from_documents(documents)
        self.dense_index.save_index(index_path='{}/arxiv_index.pkl'.format(self.params['index path']), vectors_path='{}/arxiv_vectors.pkl'.format(self.params['index path']))

        df_mongo.reset_index(inplace=True)  # Reset Index
        data_dict = df_mongo.to_dict("records")  # Convert to dictionary

        self.col.insert_many(data_dict)

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
        pass

    #returns list of titles made by user
    def user_profile(self):
        pass

if __name__ == "__main__":
    p = PaperRetrieval({'arxiv path': 'D:\\ERSP\\arxiv\\arxiv-metadata-oai-snapshot.json',
                             'index path': 'D:/ERSP/chatbot/input_handler',
                             'DA list': [{'intent': 'question',
				                        'index': 0,
				'main conference': {'conference': 'SIGIR', 'year': '2021'},
				'entity': ['session'],
				'authors': ['Hamed Zamani']}]})
    print(p.result_search('Lester Ingber'))



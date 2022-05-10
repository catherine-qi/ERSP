"""
The paper retriever module. Recommends papers from arXiv dataset based on
keywords or userprofile.
Author: Vedanth Chinta
"""

import json
import regex as re
import pandas as pd
import os
import requests

from sentence_transformers import SentenceTransformer
from ..retriever.dense_retriever import DenseRetriever
from pymongo import MongoClient


class PaperRetrieval():
    """
	PaperRetrieval is a class computes the most similar documents (recommendations) to a query (user message in this case).
    Uses semantic scholar to retrieve userprofile.

    **Note**: The arXiv dataset is too large to be stored via pymongo. Either store the set in MongoDB Compass, or use
    the temporarily solution used here. 

    **Note**: Semantic scholars API allows a limited number of API calls (100 per 5 minutes).

		Args:
			params(dict): A dict of parameters.
	"""
    def __init__(self, params):
        self.params = params

        self.api_url = 'https://api.semanticscholar.org/graph/v1' # For using semantic scholar API

        self.client = MongoClient(self.params['paper_db_host'], self.params['paper_db_port']) # Where the arXiv papers are stored
        self.db = self.client[self.params['paper_db_name']]
        self.col = self.db[self.params['paper_db_collection_name']]

        self.arxiv_path = self.params['arxiv path']

        self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1', device='cuda')

        self.dense_index = DenseRetriever(self.model)
        self.index_docs()
        # Without a GPU, pickling the dense index takes too long. It will take ~1 hour to finish with a 2080ti GPU.
        # You can find the link to download the pickle file in the repo README.
        if os.path.exists('{}/index/arxiv_index.pkl'.format(self.params['index path'])):
            self.dense_index.load_index('{}/index/arxiv_index.pkl'.format(self.params['index path']))

    def index_docs(self):
        """
		Loads in the arxiv dataset as a dict. 
        Commented out portion puts the dataset into a Mongo DB.

		Args:
		
		Returns:
		"""
        f = open(self.arxiv_path)
        self.data = json.load(f)
        """
        Commmented out due to arXiv dataset being too large for pymongo to handle.
        Either store the set in MongoDB Compass, or use the temporarily solution used here.
        This may work for smaller datasets of research papers.

        titles = []
        abstracts = []
        authors = []
        for key in self.data:
            authors.append(self.data[key]['authors'])
            titles.append(self.data[key]['title'])
            abstracts.append(self.data[key]['abstract'])
        
        df_mongo = pd.DataFrame({  # convert the json to a pandas dataframe
            'title': titles,
            'authors': authors,
            'abstract': abstracts
        })

        for row_label in df_mongo.index:  # convert the multiple authors separated by ', and' to a list
            df_mongo['authors'][row_label] = re.split(
                ', | and ', df_mongo['authors'][row_label])
        
        df_mongo.reset_index(inplace=True)  # Reset Index
        data_dict = df_mongo.to_dict("records")  # Convert to dictionary

        self.col.insert_one(data_dict)

        self.dense_index.create_index_from_documents(title)
        self.dense_index.save_index(index_path='{}/arxiv_index.pkl'.format(self.params['index path']), vectors_path='{}/arxiv_vectors.pkl'.format(self.params['index path']))
        """
        f.close()
    
    def paper_search(self, conv_list):
        """
		Computes the best/most relevant paper in arXiv dataset related to query (user message).

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A dict with key 'paper' that maps to the recommended paper, and 'authors' that maps to the authors that
            wrote the recommended paper.
		"""
        results = self.dense_index.search([conv_list[0].text])[0]
        results = [i[0] for i in results][0]
        results = str(results)
        title = self.data[results]['title']
        authors = self.data[results]['authors']
        #title = self.col.find_one({'index': int(str(results))})
        return {'paper': title, 'authors': authors}
    
    def paper_search_auth(self, conv_list):
        """
		Computes the best/most relevant paper in arXiv dataset related to query (user message).
        Filters out recommendation results that a specified author is in (same author as the userprofile). 

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A dict with key 'paper' that maps to the recommended paper, and 'authors' that maps to the authors that
            wrote the recommended paper.
		"""
        results = self.dense_index.search([conv_list[0].text])[0]
        results = [i[0] for i in results]
        title = None
        authors = None
        for i in range(len(results)):
            r = str(results[i])
            if self.data[r]['title'] not in conv_list[0].text:
                title = self.data[r]['title']
                authors = self.data[r]['authors']
        return {'paper': title, 'authors': authors}

    def get_paper_id(self, author, title):
        """
		Returns the semantic scholar paper ID via its API, based on author name and paper title.

		Args:
			author(str): Author name of wanted paper.
			title(str): Title of wanted paper.
		
		Returns:
			A str of the paper ID.
		"""
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
        """
		Returns the semantic scholar author ID via its API, based on author name and paper ID associated with a paper
        that author wrote.

		Args:
			author(str): Author name.
			paper_id(str): The paper ID of a paper the wanted author has written.
		
		Returns:
			A str of the author ID.
		"""
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
        """
        Finds all papers and their abstracts of an author (identified by their name and a title they wrote) via semantic scholar API.
        The userprofile is the concatenation of this data.

		Args:
			author(str): Author name.
			title(str): A title that the author has written.
		
		Returns:
			A list of str that constitutes all of the author's titles and abstracts.
		"""
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
            if entry['fieldsOfStudy'] is not None and 'Computer Science' in entry['fieldsOfStudy']: # Semantic scholars data has some errors on retrieving author works.
                big_str = '' # For some authors, semantic scholars incorrectly identifies papers written by them. A simple solution to this is
                if entry['title'] is not None: # to filter for papers only for Computer Science. However, this solution is not viable if we want
                    big_str = entry['title'] # the system to work for any conference of any field of study.
                    if entry['abstract'] is not None:
                        big_str = big_str + ' ' + entry['abstract']
                    author_works.append(big_str)
        return author_works
    
    def get_results(self, conv_list, index):
        """
		Calls a specific method based on index.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            index(int): Maps to the corresponding question in the question list, located in QueryClassification.
		
		Returns:
			The value returned by the called method.
		"""
        if index in range(11,13):
            return self.paper_search(conv_list)
        if index in range(13,15):
            auth_works = self.user_profile(self.params['DA list'][0]['authors'][0], conv_list[0].text)
            big_str = ''
            for w in auth_works:
                big_str += ' ' + w
            new_message = conv_list[0]
            new_message.text = big_str
            return self.paper_search_auth(conv_list)
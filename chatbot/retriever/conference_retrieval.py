import json

from sentence_transformers import SentenceTransformer
from ..retriever.dense_retriever import DenseRetriever
from ..retriever.sparse_retriever import SparseRetriever
from ..retriever.paper_retriever import PaperRetrieval
from flask import request, Flask, jsonify
from flask_cors import CORS

class ConferenceRetrieval():
    def __init__(self, params):
        self.params = params

        self.app = Flask(__name__)
        CORS(self.app)

        self.data = self.get_data()

        self.model = SentenceTransformer('sentence-transformers/allenai-specter')
        self.dense_index = DenseRetriever(self.model)

        self.sparse_retriever = SparseRetriever()
    
    #Testing purposes
    def serve(self, port=80):
        self.build_endpoints()
        self.app.run(host='0.0.0.0', port=port)
    
    #Testing purposes
    def build_endpoints(self):
        @self.app.route('/encode', methods=['POST', 'GET'])
        def encode_endpoint():
            temp = "test"
            results = json.dumps(temp, indent=4)
            return results
    
    #'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\conference_data.json'
    def get_data(self):
        data = None
        with open(self.params['conf dataset'], 'r') as f:
            data = json.load(f)
        f.close()
        return data
    
    def get_attr(self, conf, entity, attr):
        lst = []
        for key, value in self.data.items():
            if key == conf:
                for e in value[entity]:
                    if isinstance(e[attr], list):
                        for i in e[attr]:
                            lst.append(i)
                    else:
                        lst.append(e[attr])
        return lst
    
    def search(self, conf, entity, name):
        for key, value in self.data.items():
            if key == conf:
                for e in value[entity]:
                    if e['name'] == name:
                        return e
    
    def valid_schedule(self, conv_list, constraint):
        pass

    def time(self, conv_list, constraint=None):
        if constraint is not None:
            return self.valid_schedule(conv_list, constraint)
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        if len(entities) > 1:
            return 'too many entities'
        
        session_names = self.get_attr(wanted_conf, entities[0], 'name')
        self.sparse_retriever.index_documents(session_names)
        sparse_results = self.sparse_retriever.search([conv_list[0]])[0]
        sparse_results = [r[0] for r in sparse_results][0]

        return self.search(wanted_conf, entities[0], session_names[sparse_results])['date']
    
    def author_list(self, conv_list):
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        names = []
        for entity in entities:
            valid = self.get_attr(wanted_conf, entity, 'name')
            self.sparse_retriever.index_documents(valid)
            sparse_results = self.sparse_retriever.search([conv_list[0]])[0]
            sparse_results = [i[0] for i in sparse_results][0]
            names.append(valid[sparse_results])
        
        counter = 0
        authors = []
        for entity in entities:
            for a in self.search(wanted_conf, entity, names[counter])['authors']:
                authors.append(a)
        return authors
    
    def author_check(self, conv_list):
        curr_da = self.params['DA list'][0]
        authors = curr_da['authors']

        if len(authors) < 1:
            return 'no author'

        author_list = self.author_list(conv_list)
        
        is_in = True
        missing_authors = []
        for a in authors:
            flag = False
            for arr in author_list:
                if a in arr:
                    flag = True
            if not flag:
                missing_authors.append(a)
            is_in = is_in and flag
        return{'is in': is_in, 'missing authors': missing_authors}
    
    def where_author(self):
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']
        authors = curr_da['authors']

        if len(authors) < 1:
            return 'no author'
        
        result = {}
        for a in authors:
            result[a] = {'session': [],
                         'workshop': [],
                         'tutorial': []}

        for entity in entities:
            for entries in self.data[wanted_conf][entity]:
                for arr in entries['authors']:
                    for a in authors:
                        if a in arr:
                            if entries['name'] not in result[a][entity]:
                                result[a][entity].append(entries['name'])
        
        return result
    
    def best_entity(self, conv_list, authors_wanted=False):
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        recommendations = {}
        for entity in entities:
            similarities = []
            names = []
            if authors_wanted:
                dict = self.where_author()
                for key, value in dict.items():
                    if len(value[entity]) < 1:
                        return key + ' not in any ' + entity
                    for n in value[entity]:
                        if n not in names:
                            names.append(n)
            else:
                names = self.get_attr(wanted_conf, entity, 'name')
            for n in names:
                titles = []
                if entity == 'session':
                    titles = self.search(wanted_conf, entity, n)['paper titles']
                else:
                    titles = [self.search(wanted_conf, entity, n)['abstract']]
                titles.append(n)
                large_str = ''
                for t in titles:
                    large_str = large_str + ' ' + t
                self.dense_index.create_index_from_documents([large_str])
                dense_results = self.dense_index.search([conv_list[0]])[0]
                dense_results = [i[1] for i in dense_results][0]
                similarities.append(dense_results)
            recommendations[entity] = names[similarities.index(max(similarities))]
        
        return recommendations

    def get_papers(self, conv_list):
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        if len(entities) > 1 or entities[0] != 'session':
            return 'only session has papers'
        
        names = self.get_attr(wanted_conf, 'session', 'name')
        self.sparse_retriever.index_documents(names)
        sparse_results = self.sparse_retriever.search([conv_list[0]])[0]
        sparse_results = [i[0] for i in sparse_results][0]
        titles = self.search(wanted_conf, entities[0], names[sparse_results])['paper titles']
        return titles
    
    def best_paper_title(self, conv_list):
        curr_da = self.params['DA list'][0]
        entities = curr_da['entity']

        if len(entities) > 1 or entities[0] != 'session':
            return 'only session has papers'
        
        titles = self.get_papers(conv_list)
        print(titles)
        self.dense_index.create_index_from_documents(titles)
        dense_results = self.dense_index.search([conv_list[0]])[0]
        dense_results = [i[0] for i in dense_results][0]
        return titles[dense_results]

    def related_author_session(self, conv_list, paper_retrieval):
        curr_da = self.params['DA list'][0]
        authors = curr_da['authors']

        title_flag = True
        if title_flag:
            author_data = paper_retrieval.user_profile(authors[0], conv_list[0])
            author_data = " ".join(author_data)
            recommendation = self.best_entity([author_data])
            return recommendation
    
    def get_results(self, conv_list, index):
        if index in range(0,2):
            return self.author_list(conv_list)
        if index == 2:
            return self.author_check(conv_list)
        if index == 3:
            return self.where_author()
        if index in range (4,6):
            return self.best_entity(conv_list) if len(self.params['DA list'][0]['authors']) < 1 else self.best_entity(conv_list, True)
        if index == 6:
            return self.get_papers(conv_list)
        if index in range(7,9):
            return self.related_author_session(conv_list, self.params['actions']['retrieval'])
        if index in range(9,11):
            return self.best_paper_title(conv_list)
    
if __name__ == "__main__":
    params = {'conf dataset': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\conference_data.json',
                             'index path': 'D:/ERSP/chatbot/input_handler',
                             'arxiv path': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\arxiv_parsed.json',
                             'DA list': [{'intent': 'question',
				                        'index': 0,
				'main conference': {'conference': 'SIGIR', 'year': '2021'},
				'entity': ['session'],
				'authors': ['Hamed Zamani']}]}
    c = ConferenceRetrieval(params)
    p = PaperRetrieval(params)
    print(c.related_author_session(['Conversational Information Seeking'], p))
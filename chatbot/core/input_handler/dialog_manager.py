import json

from ..input_handler import actions
from ..input_handler.query_classification import QueryClassification
from ..retriever.conference_retrieval import ConferenceRetrieval
from ..retriever.paper_retriever import PaperRetrieval
from ..retriever.question_retrieval import QuestionRetrieval
from flask import request, Flask, jsonify
from flask_cors import CORS

class DialogManager:
    def __init__(self, params):
        self.params = params
        
        #Setting up FLASK
        self.app = Flask(__name__)
        CORS(self.app)

        self.QC = QueryClassification(params)
        self.CR = ConferenceRetrieval(params)
        self.PR = PaperRetrieval(params)
        self.QR = QuestionRetrieval(params)

        self.params['actions'] = {'retrieval': self.PR, 'conference': self.CR, 'question': self.QR}

        self.params['needed info'] = []

        self.conv_list = [] #Testing purposes
    
    #Testing purposes
    def serve(self, port=80):
        self.build_endpoints()
        self.app.run(host='0.0.0.0', port=port)
    
    #Testing purposes
    def build_endpoints(self):
        @self.app.route('/encode', methods=['POST', 'GET'])
        def encode_endpoint():
            text = str(request.args.get('text'))
            self.conv_list.insert(0, text)
            answer = self.dispatch(self.conv_list)
            results = json.dumps(answer, indent=4)
            return results
    
    def info_needed(self):
        curr_da = self.params['DA list'][0]
        entities = curr_da['entity']
        print(curr_da)
        if len(entities) < 1:
            curr_da['error str'] = 'Please provide if you are looking for papers, sessions, workshops, or tutorials.'
            return
        if ('session' in entities or 'workshop' in entities or 'tutorial' in entities) and curr_da['main conference']['conference'] is None:
            curr_da['error str'] = 'Please provide what conference you are interested in.'
            return
        if 'paper' not in entities and 'article' not in entities and curr_da['main conference']['year'] is None:
            curr_da['error str'] = 'Please provide the year of the conference.'
            return

    def action_detection(self, conv_list):
        self.params['DA list'].insert(0, self.QC.create_DA(conv_list))
    
    def conv_logic(self, index, conv_list):
        if index in range(0,2):
            return {'conf author': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 2:
            return {'author check': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 3:
            return {'where author': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(4,6):
            return {'conf rec': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 6:
            return {'session papers': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(7,9):
            return {'title ques': actions.QuestionAction.run(conv_list, self.params)}
        if index in range(9,11):
            return {'conf paper title rec': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(11,13):
            return {'paper qa': actions.RetrievalAction.run(conv_list, self.params)}
        if index in range(13,15):
            return {'title ques': actions.QuestionAction.run(conv_list, self.params)}
    
    def dispatch(self, conv_list):
        self.action_detection(conv_list)
        self.info_needed()
        curr_da = self.params['DA list'][0]
        if curr_da['error str'] is not None:
            return {'error msg': actions.QuestionAction.run(conv_list, self.params)}

        intent = curr_da['intent']
        index = curr_da['index']
        if intent == 'question':
            if curr_da['last DA'] is not None:
                if index in range(7,9):
                    return {'userprofile': actions.ConferenceAction.run(conv_list, self.params)}
                if index in range(13,15):
                    return {'userprofile': actions.RetrievalAction.run(conv_list, self.params)}
            return self.conv_logic(index, conv_list)
        if intent == 'reject':
            return {'inquire': actions.QuestionAction.run(conv_list, self.params)}
        if intent == 'acceptance':
            last_index = self.params['DA list'][1]['index']
            for key in curr_da.keys():
                if key == 'last similarity':
                    curr_da[key] = self.params['DA list'][1][key] + 1
                else:
                    curr_da[key] = self.params['DA list'][1][key]
            return self.conv_logic(last_index, conv_list)

if __name__ == "__main__": #TESTING PURPOSES
    params = {'conf dataset': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\conference_data.json',
              'index path': 'D:/ERSP/chatbot/input_handler',
              'arxiv path': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\arxiv_parsed.json',
              'DA list': []}
    conv_list = ['Papers written by Hamed Zamani?']

    DM = DialogManager(params)
    #print(DM.dispatch(conv_list))
    #print(DM.params['DA list'][0])
    DM.serve(9000)
        
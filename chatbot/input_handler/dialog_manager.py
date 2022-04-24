import actions

from query_classification import QueryClassification
from ..retriever.conference_retrieval import ConferenceRetrieval
from ..retriever.paper_retriever import PaperRetrieval

class DialogManager:
    def __init__(self, params):
        self.params = params

        self.QC = QueryClassification(params)
        self.CR = ConferenceRetrieval(params)
        self.PR = PaperRetrieval(params)

        self.params['DA list'] = []

        self.params['needed info'] = []
    
    def add_DA(self, conv_list):
        self.params['DAs'].insert(0, self.QC.create_DA(conv_list))
    
    def info_needed(self):
        curr_da = self.params['DA list'][0]
        entities = curr_da['entity']
        if len(entities) < 1:
            return 'Please provide if you are looking for papers, sessions, workshops, or tutorials.'
        if 'session' in entities or 'workshop' in entities or 'tutorial' in entities and curr_da['main conference']['conference'] is None:
            return 'Please provide what conference you are interested in.'
        if curr_da['main conference']['year'] is None:
            return 'Please provide the year of the conference.'

    def action_detection(self, conv_list):
        self.add_DA(conv_list)
    
    def dispatch(self, conv_list):
        self.action_detection(conv_list)
        self.info_needed()
        curr_da = self.params['DA list'][0]

        intent = curr_da['intent']
        index = curr_da['index']

        if intent == 'question':
            if index in range(0,11):
                return {'conf qa': actions.ConferenceAction.run(conv_list, self.params)}
            if index in range(11,15):
                return {'paper qa': actions.RetrievalAction.run(conv_list, self.params)}
        if intent == 'reject':
            return {'inquire': actions.QuestionAction.run(conv_list, self.params)}
        if intent == 'acceptance':
            last_index = self.params['DA list'][1]['index']
            for key in curr_da.keys():
                curr_da[key] = self.params['DA list'][1][key]
            if last_index in range(0,11):
                return {'conf accept': actions.ConferenceAction.run(conv_list, self.params)}
            if last_index in range(11,15):
                return {'paper accept': actions.RetrievalAction.run(conv_list, self.params)}
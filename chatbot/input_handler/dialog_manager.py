from query_classification import QueryClassification

class DialogManager:
    def __init__(self, params):
        self.params = params

        self.QC = QueryClassification(params)

        self.DAs = []
    
    def info_check(self, needed_info):
        pass
    
    def add_DA(self, conv_list):
        self.DAs.insert(0, self.QC.create_DA(conv_list))

    def action_detection(self, conv_list):
        self.add_DA(conv_list)

    #Lots of code duplication--refactoring should be done later.
    def dispatch(self, conv_list):
        self.action_detection(conv_list)

        intent = self.DAs[0].intent
        ques_index = self.DAs[0].intent_index
        conference = self.DAs[0].main_conference
        entity = self.DAs[0].entity
        query_vector = self.DAs[0].query_vector
        authors = self.DAs[0].authors

        action_str = None

        if 'question' in intent:
            
            #conference time
            if ques_index in range(0,2):
                action_str = entity + ' time'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            #conference authors
            elif ques_index in range(2,4):
                action_str = 'author ' + entity + ' list'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            elif ques_index == 4:
                action_str = 'author ' + entity + ' check'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            elif ques_index == 5:
                action_str = 'author ' + entity
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE

            #conference sessions/workshops
            elif ques_index in range(6, 8):
                action_str = entity + ' description'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            elif que_index in range(8, 10):
                action_str = entity + ' recommendation'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            elif que_index in range (10, 12):
                action_str = entity + ' papers'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            elif ques_index in range(12, 14):
                action_str = entity + ' related to paper'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            #conference papers
            elif ques_index == 14:
                action_str = entity + ' papers related'
                return {action_str: actions.ConferenceAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            #paper retrieval
            elif ques_index in range(15, 17):
                action_str = 'paper recommendation'
                return {action_str: actions.RetrievalAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
            
            else: #ques_index is 17 or 18
                action_str = 'author papers'
                return {action_str: actions.RetrievalAction.run(conv_list, self.DAs[0], self.params)} #CHANGE
        
        if 'reject' in intent:
            return {'recommend another': actions.QuestionAction.run(conv_list, self.DAs[0], self.DAs[1], self.params)}
            
        if 'acceptance' in intent:
            return {'recommend another': actions.RetrievalAction.run(conv_list, self.DAs[0], self.DAs[1], self.params)}
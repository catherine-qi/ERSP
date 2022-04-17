import actions

from query_classification import QueryClassification


#params will contain a key called "DAs" to contain the list of DAs obtained from convo history
class DialogManager:
    def __init__(self, params):
        self.params = params

        self.QC = QueryClassification(params)

        self.params['DAs'] = []

        self.params['needed info'] = []
    
    def add_DA(self, conv_list):
        self.params['DAs'].insert(0, self.QC.create_DA(conv_list))

    def action_detection(self, conv_list):
        self.add_DA(conv_list)
    
    #helper function
    def check(self, needed_info):
        info = []
        curr_DA = self.params['DAs'][0]
        for ele in needed_info:
            if ele == 'authors':
                if len(curr_DA[ele]) == 0:
                    if len(self.params['DAs']) > 1 and len(self.params['DAs'][1][ele]) > 0:
                        curr_DA[ele] = self.params['DAs'][1][ele]
                        info.append(False)
                    else:
                        info.append(True)
            elif curr_DA[ele] is None:
                if len(self.params['DAs']) > 1 and self.params['DAs'][1][ele] is not None:
                    curr_DA[ele] = self.params['DAs'][1][ele]
                    info.append(False)
                else:
                    info.append(True)
            else:
                info.append(False)
        return info
    
    def info_check(self, needed_info):
        flag = 0
        info_needed = self.info_check(needed_info)
        for ele in info_needed:
            if ele:
                self.params['needed info'].append(ele)
                flag = 1
        return True if flag == 1 else False

    #Lots of code duplication--refactoring should be done later.
    def dispatch(self, conv_list):
        self.action_detection(conv_list)

        intent = self.params['DAs']['intent']
        ques_index = self.params['DAs']['intent index']
        entity = self.params['DAs']['entity']

        action_str = None

        if 'question' in intent:
            #conference time
            if ques_index in range(0,2):
                if self.info_check(['main conference']): #error checking
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}

                action_str = entity + ' time'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            #conference authors
            elif ques_index in range(2,4):
                if self.info_check(['main conference']): #error checking
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = 'author ' + entity + ' list'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            elif ques_index == 4:
                if self.info_check(['main conference', 'authors']): #error checking
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = 'author ' + entity + ' check'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            elif ques_index == 5:
                if self.info_check(['main conference', 'authors']): #error checking
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = 'author ' + entity
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE

            #conference sessions/workshops
            elif ques_index in range(6, 8):
                if self.info_check(['main conference']): #error checking
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = entity + ' description'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            elif ques_index in range(8, 10):
                if self.info_check(['main conference']):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}

                action_str = entity + ' recommendation'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            elif ques_index in range (10, 12):
                if self.info_check(['main conference']):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = entity + ' papers'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            elif ques_index in range(12, 14):
                if self.info_check(['main conference', 'authors'):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = entity + ' related to paper'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            #conference papers
            elif ques_index == 14:
                if self.info_check(['main conference', 'authors']):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = entity + ' papers related'
                return {action_str: actions.ConferenceAction.run(conv_list, self.params)} #CHANGE
            
            #paper retrieval
            elif ques_index in range(15, 17):
                if self.info_check(['main conference']):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = 'paper recommendation'
                return {action_str: actions.RetrievalAction.run(conv_list, self.params)} #CHANGE
            
            else: #ques_index is 17 or 18
                if self.info_check(['authors']):
                    return {'info needed': actions.QuestionAction.run(conv_list, self.params)}
                
                action_str = 'author papers'
                return {action_str: actions.RetrievalAction.run(conv_list, self.params)} #CHANGE
        
        if 'reject' in intent:
            return {'better recommend': actions.QuestionAction.run(conv_list, self.params)}
            
        if 'acceptance' in intent:
            return {'recommend another': actions.RetrievalAction.run(conv_list, self.params)}
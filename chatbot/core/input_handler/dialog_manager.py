"""
The dialog manager module. Handles conversation flow.
Authors: Catherine Qi
"""

import json

from ..input_handler import actions
from ..input_handler.query_classification import QueryClassification
from ..retriever.conference_retrieval import ConferenceRetrieval
from ..retriever.paper_retriever import PaperRetrieval
from ..retriever.question_retrieval import QuestionRetrieval


class DialogManager:
    """
    DialogManager is a class that handles the conversation logic.
    Based on the information returned by the query classification, runs the desired action.

	Args:
		params(dict): A dict of parameters.
	"""
    def __init__(self, params):
        self.params = params

        self.QC = QueryClassification(params)
        self.CR = ConferenceRetrieval(params)
        self.PR = PaperRetrieval(params)
        self.QR = QuestionRetrieval(params)

        self.params['actions'] = {'retrieval': self.PR, 'conference': self.CR, 'question': self.QR}
    
    def info_needed(self):
        """
		Checks if user has given required information in the current message.
        User must provide what kind of entity they are looking for, and the desired conference name and event.
        
        Returns:
			Void.
		"""
        curr_da = self.params['DA list'][0]
        entities = curr_da['entity']
        if len(entities) < 1: # Users most always provide entity
            curr_da['error str'] = 'Please provide if you are looking for papers, sessions, workshops, or tutorials.'
        if 'paper' not in entities and 'article' not in entities: # Users most always provide conference name and year if referring to sessions/workshops/tutorials
            if curr_da['main conference']['conference'] is None:
                curr_da['error str'] = 'Please provide what conference you are interested in.'
            elif curr_da['main conference']['year'] is None:
                curr_da['error str'] = 'Please provide the year of the conference.'

    def action_detection(self, conv_list):
        """
		Creates a new dialogue act based on the user's most current messages via query classification.
        Adds that dialogue act to the front of the current list of dialogue acts.

        Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
        
        Returns:
			Void.
		"""
        self.params['DA list'].insert(0, self.QC.create_DA(conv_list))
    
    def conv_logic(self, index, conv_list):
        """
		Logic to handle first-turn interactions. Based on index, runs the corresponding action.

        Args:
            index(int): Maps to the corresponding question in the question list, located in QueryClassification.
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
        
        Returns:
			A dict with key describing the ran action, and value of the action output.
		"""
        if index in range(0,2): # What author will be participating in <ENTITY_NAME>
            return {'conf author': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 2: # Will <AUTHOR_NAME> be participating in <ENTITY_NAME>
            return {'author check': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 3: # What <ENTITY_NAME> will <AUTHOR_NAME> be participating in
            return {'where author': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(4,6): # Recommend a <ENTITY_NAME> about <KEYWORD> (that <AUTHOR_NAME> is in)
            return {'conf rec': actions.ConferenceAction.run(conv_list, self.params)}
        if index == 6: # What papers does the session cover
            return {'session papers': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(7,9): # Recommend a <ENTITY_NAME> related to <AUTHOR_NAME> works
            return {'title ques': actions.QuestionAction.run(conv_list, self.params)}
        if index in range(9,11): # What are some papers in the session about <KEYWORD>
            return {'conf paper title rec': actions.ConferenceAction.run(conv_list, self.params)}
        if index in range(11,13): # Papers related to <KEYWORD>
            return {'paper qa': actions.RetrievalAction.run(conv_list, self.params)}
        if index in range(13,15): # Papers related to <AUTHOR_NAME> works
            return {'title ques': actions.QuestionAction.run(conv_list, self.params)}
    
    def dispatch(self, conv_list):
        """
		Detects what action should be run based on user response and current state (related to multi-turn).
        Runs the needed action.

        Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
        
        Returns:
			A dict with key describing the ran action, and value of the action output.
		"""
        self.action_detection(conv_list) # Create the dialogue act
        self.info_needed() # Error checking
        curr_da = self.params['DA list'][0]
        if curr_da['error str'] is not None:
            return {'error msg': actions.QuestionAction.run(conv_list, self.params)}

        intent = curr_da['intent']
        index = curr_da['index']
        if intent == 'question':
            if curr_da['last DA'] is not None: # Multi-turn checking. Check if in second turn of multi-turn conversations
                if index in range(7,9):
                    return {'userprofile': actions.ConferenceAction.run(conv_list, self.params)}
                if index in range(13,15):
                    return {'userprofile': actions.RetrievalAction.run(conv_list, self.params)}
            return self.conv_logic(index, conv_list)
        """
        Support for acceptance/rejection not complete; commented out to avoid unnecessary errors for current use
        if intent == 'reject':
            return {'inquire': actions.QuestionAction.run(conv_list, self.params)}
        if intent == 'acceptance':
            last_index = self.params['DA list'][1]['index']
            for key in curr_da:
                if key != 'last similarity':
                    curr_da[key] = self.params['DA list'][1][key]
            return self.conv_logic(last_index, conv_list)
        """
        
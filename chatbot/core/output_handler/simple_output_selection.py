"""
Chooses from pre-defined templates randomly for output selection.
Authors: Catherine Qi
"""

import util

from random import randrange
from ..output_handler.output_selection import OutputProcessing
from ..interaction_handler.msg import Message


class SimpleOutputSelection(OutputProcessing):
    """
    SimpleOutputSelection is a class that makes the dialogue system's response to the user.
    It uses pre-defined templates for the response structure, and chooses a template randomly.

		Args:
			params(dict): A dict of parameters.
	"""
    def __init__(self, params):
        super().__init__(params)
    
    def output_selection(self, conv_list, candidate_outputs):
        """
		Based on the candidate_outputs key, uses a specific set of templates for each question type.
        Randomly chooses which template to use, and fills needed information in the template to finalize response.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
			candidate_outputs(dict): A dict with key describing the ran action, and value of the action output.
		
		Returns:
			A str of the response text the dialogue system will respond with.
		"""
        curr_DA = self.params['DA list'][0]
        authors = curr_DA['authors']
        entities = curr_DA['entity']

        if 'error msg' in candidate_outputs: # Error message to reply back to user
            return candidate_outputs['error msg']
        
        if 'conf author' in candidate_outputs: # What author will be participating in <ENTITY_NAME>
            result = candidate_outputs['conf author']
            authors = ', '.join(', '.join(str(e) for e in ele) for ele in result) # Parse the author list into a str
            self.conf_author = ['{} will be there.'.format(authors),
                                '{} is going to be there.'.format(authors),
                                '{} will be presenting.'.format(authors),
                                '{} is participating.'.format(authors),
                                '{} is presenting.'.format(authors)]
            index = randrange(len(self.conf_author))
            return self.conf_author[index]
        
        if 'author check' in candidate_outputs: # Will <AUTHOR_NAME> be participating in <ENTITY_NAME>
            is_in = candidate_outputs['author check']['is in'] # List of authors participating
            missing_authors = candidate_outputs['author check']['missing authors'] # List of authors not participating
            result = ''
            if len(is_in) > 0:
                in_authors = ', '.join(str(ele) for ele in is_in) # Parse the author list into a str
                self.author_check_yes = ['{} will be present.'.format(in_authors),
                                         '{} will be participating.'.format(in_authors),
                                         '{} will be there.'.format(in_authors),
                                         '{} is going to be there.'.format(in_authors),
                                         '{} will be presenting.'.format(in_authors)]
                index = randrange(len(self.author_check_yes))
                result = self.author_check_yes[index]
            if len(missing_authors) > 0:
                miss_authors = ', '.join(str(ele) for ele in missing_authors) # Parse the author list into a str
                self.author_check_no = ['{} will not be present'.format(miss_authors),
                                        '{} will not be participating.'.format(miss_authors),
                                        '{} will not be there'.format(miss_authors),
                                        '{} is not there'.format(miss_authors),
                                        '{} is not going to be there'.format(miss_authors)]
                index = randrange(len(self.author_check_no))
                result += self.author_check_no[index]
            return result
        
        if 'where author' in candidate_outputs: # What <ENTITY_NAME> will <AUTHOR_NAME> be participating in
            a = ', '.join(str(ele) for ele in authors) # Parse the author list into a str
            result = [] # List of all <ENTITY_NAME> the respective authors will be at
            for auth in authors:
                for key in candidate_outputs['where author'][auth]:
                    if len(candidate_outputs['where author'][auth][key]) > 0:
                        result.append(candidate_outputs['where author'][auth][key])
            
            if len(result) > 0:
                ans = ', '.join(', '.join(str(e) for e in ele) for ele in result) # Parse the entity names list into a str 
                self.where_author = ['{} will be at {}.'.format(a, ans),
                                    '{} is going to be at {}.'.format(a, ans),
                                    '{} will be participating at {}.'.format(a, ans),
                                    '{} will be presenting at {}.'.format(a, ans),
                                    '{} is presenting at {}.'.format(a, ans)]
                index = randrange(len(self.where_author))
                return self.where_author[index]
            
            self.author_not_found = ['{} was not found in the conference.'.format(a),
                                     '{} is not going to be at any conference event.'.format(a),
                                     '{} is missing! I don\'t see them presenting at the conference.'.format(a),
                                     '{} is not at the conference.'.format(a),
                                     '{} is not present at the conference.'.format(a)]
            index = randrange(len(self.author_not_found))
            return self.author_not_found[index]
        
        if 'conf rec' in candidate_outputs: # Recommend a <ENTITY_NAME> about <KEYWORD> (that <AUTHOR_NAME> is in)
            result = candidate_outputs['conf rec']
            ans = ''
            for entity in entities: # Format the response string to: <ENTITY_NAME>: __
                ans += entity.capitalize() + ': ' + result[entity] + '\n'

            self.conf_rec = ['I recommend the following you:\n {}.'.format(ans),
                             'Based on your preferences, I recommend:\n {}.'.format(ans),
                             'Looking at every all the conference events, this seems to be most related to your interests:\n {}'.format(ans),
                             'I found this may relate to what you\'re looking for:\n {}'.format(ans),
                             'These events could be a good match for you:\n {}'.format(ans)]
            index = randrange(len(self.conf_rec))
            return self.conf_rec[index]
        
        if 'session papers' in candidate_outputs: # What papers does the session cover
            result = candidate_outputs['session papers']
            ans = ', '.join(str(ele) for ele in result) # Parse the paper titles list into a str
            self.session_papers = ['The session paper titles are:\n {}'.format(ans),
                                   'The papers being presented in the session are:\n {}'.format(ans),
                                   'Papers to be presented are:\n {}'.format(ans),
                                   'I found these research papers will be presented:\n {}'.format(ans),
                                   'Here are all the papers being presented in the session:\n {}'.format(ans)]
            index = randrange(len(self.session_papers))
            return self.session_papers[index]
        
        if 'userprofile' in candidate_outputs: # Second response to Recmmend a <ENTITY_NAME> related to <AUTHOR_NAME> works or Papers related to <AUTHOR_NAME> works
            result = candidate_outputs['userprofile']
            a = authors[0] # User profiling can only refer to one author (no support for multiple author profiling)
            ans = ''
            for entity in entities:
                ans += entity.capitalize() + ': ' + result[entity] + '\n' # Format the response string to: <ENTITY_NAME>: __
            self.userprofile = ['I found this to be is best related to {}\'s works:\n {}'.format(a, ans),
                                'This is most related to {}\'s works:\n {}'.format(a, ans),
                                'I recommend this to be most related to {}\'s works:\n {}'.format(a, ans),
                                'This seems to be of close topic in relation to {}\'s works:\n {}'.format(a, ans),
                                'Based on {}\'s works, I think this is what you\'re looking for:\n {}'.format(a, ans)]
            index = randrange(len(self.userprofile))
            return self.userprofile[index]

        if 'conf paper title rec' in candidate_outputs: # What are some papers in the session about <KEYWORD>
            result = candidate_outputs['conf paper title rec']
            self.conf_paper_title_rec = ['{} is related to your interests.'.format(result),
                                         '{} is closely associated with what you\'re looking for.'.format(result),
                                         'I recommend {}.'.format(result),
                                         'Based on all the accepted papers, {} best matches your needs.'.format(result),
                                         'My personal recommendation for you is {}.'.format(result)]
            index = randrange(len(self.conf_paper_title_rec))
            return self.conf_paper_title_rec[index]

        if 'paper qa' in candidate_outputs: # Papers related to <KEYWORD>
            result = candidate_outputs['paper qa']['paper']
            authors = candidate_outputs['paper qa']['authors']
            self.paper_qa = ['{} is closely related to your interests, written by {}.'.format(result, authors),
                             '{} is closely associated with what you\'re looking for, written by {}.'.format(result, authors),
                             'I recommend {}, written by {}.'.format(result, authors),
                             'My personal recommendation for you is {}, written by {}.'.format(result, authors),
                             'It seems that {} is closely related to your preferences, written by {}.'.format(result, authors)]
            index = randrange(len(self.paper_qa))
            return self.paper_qa[index]
        
        if 'title ques' in candidate_outputs: # First response to Recmmend a <ENTITY_NAME> related to <AUTHOR_NAME> works or Papers related to <AUTHOR_NAME> works
            return candidate_outputs['title ques']
    
    def get_output(self, conv, candidate_outputs):
        """
		Calls output_selection() to get text response.
        Constructs a Message object that dialogue system will respond back to user.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
			candidate_outputs(dict): A dict with key describing the ran action, and value of the action output.
		
		Returns:
			A Message object.
		"""
        user_id = conv[0].user_id
        user_info = conv[0].user_info
        msg_info = dict()
        msg_info['msg_id'] = conv[0].msg_info['msg_id']
        msg_info['msg_source'] = 'system'
        text = self.output_selection(conv, candidate_outputs)
        user_interface = conv[0].user_interface

        msg_info['msg_type'] = conv[0].msg_info['msg_type']
        k = ''
        for key in candidate_outputs.keys():
            k = key 
        msg_info['msg_creator'] = k

        timestamp = util.current_time_in_milliseconds()
        if timestamp <= conv[0].timestamp:
            raise Exception('There is a problem in the output timestamp!')
        return Message(user_interface, user_id, user_info, msg_info, text, timestamp)
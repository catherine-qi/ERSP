"""
Chooses from pre-defined templates randomly for question retrieval.
Author: Catherine Qi
"""

import random


class QuestionRetrieval():
    """
    QuestionRetrieval is a class that makes the questions to be asked by the dialogue system.
    It uses pre-defined templates for the response structure, and chooses a template randomly.

		Args:
			params(dict): A dict of parameters.
	"""
    def __init__(self, params):
        self.params = params
    
    def title_ques(self):
        """
		Randomly chooses a question related to completing userprofiles (asks for a paper the wanted
        author has written).

		Args:
		
		Returns:
			A str of the question the dialogue system will respond with.
		"""
        author = str(self.params['DA list'][0]['authors'][0])
        self.title_questions = ['Provide a paper title that {} has written.'.format(author),
                           'Give me one paper title that {} has written.'.format(author),
                           'What is one paper title that {} has written?'.format(author),
                           'I need the title of one research paper that {} has written.'.format(author),
                           'To find which {} you are looking for, please give me one paper title they have written!'.format(author),
                           'Please type in one research paper that {} has written!'.format(author),
                           'There are too many {}s! I need one research paper that they have written to narrow my search.'.format(author),
                           'It seems that there are many {0}s that exist. Type in one research paper they have written so I can find the right {0} for you!'.format(author),
                           'Type in one research paper that {} has written.'.format(author),
                           'Type in one paper title that {} has written.'.format(author)]
        index = random.randrange(len(self.title_questions))
        return self.title_questions[index]
    
    def inquire_ques(self):
        """
		Randomly chooses a question related to giving better recommendations.

        **Note**: This method is intended for supporting user rejections of the system's recommendations, which is not yet
        fully supported.

		Args:
		
		Returns:
			A str of the question the dialogue system will respond with.
		"""
        self.inquire_questions = ['Provide more keywords so that I can narrow down your search better.',
                             'What are some keywords that could help narrow my search better for you?',
                             'I need more keywords so that I can find a better result for you.',
                             'Give me some keywords to find a better answer for you.',
                             'Please give more keywords so that I can find a better result for you.']
        index = random.randrange(len(self.inquire_questions))
        return self.inquire_questions[index]
    
    def get_results(self, conv_list):
        """
		If there is a lack of information in the user's recent message, return the error str that informs of this problem.
        If intent is of 'reject', calls inquire_ques().
        Else, calls the respective methods based on the index stored in the most current dialogue act (the index maps to
        the corresponding question in the question list, located in QueryClassification.)

        **Note**: This method is intended for supporting user rejections of the system's recommendations, which is not yet
        fully supported.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			The value returned by the called method or accessed value in dict of current dialogue act.
		"""
        curr_da = self.params['DA list'][0]

        if curr_da['error str'] is not None:
            return self.params['DA list'][0]['error str']
        if curr_da['intent'] == 'reject':
            return self.inquire_ques()
        if curr_da['index'] in range (7,9) or curr_da['index'] in range(13,15):
            return self.title_ques()
import random

class QuestionRetrieval():
    def __init__(self, params):
        self.params = params
    
    def title_ques(self):
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
        self.inquire_questions = ['Provide more keywords so that I can narrow down your search better.',
                             'What are some keywords that could help narrow my search better for you?',
                             'I need more keywords so that I can find a better result for you.',
                             'Give me some keywords to find a better answer for you.',
                             'Please give more keywords so that I can find a better result for you.']
        index = random.randrange(len(self.inquire_questions))
        return self.inquire_questions[index]
    
    def get_results(self, conv_list):
        curr_da = self.params['DA list'][0]

        if curr_da['error str'] is not None:
            return self.params['DA list'][0]['error str']
        if curr_da['intent'] == 'reject':
            return self.inquire_ques()
        if curr_da['index'] in range (7,9) or curr_da['index'] in range(13,15):
            return self.title_ques()
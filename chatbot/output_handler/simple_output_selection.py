from random import randrange
from ..output_handler.output_selection import OutputProcessing

class SimpleOutputSelection(OutputProcessing):
    def __init__(params):
        super().__init__(params)
    
    def output_selection(self, conv_list, candidate_outputs):
        curr_DA = self.params['DA list'][0]
        authors = curr_DA['authors']
        entities = curr_DA['entity']

        if 'error msg' in candidate_outputs:
            return candidate_outputs['error msg']
        
        if 'conf author' in candidate_outputs:
            result = candidate_outputs['conf author']
            authors = ', '.join(str(ele) for ele in result)
            self.conf_author = ['{} will be there.'.format(authors),
                                '{} is going to be there.'.format(authors),
                                '{} will be presenting.'.format(authors),
                                '{} is participating.'.format(authors),
                                '{} is presenting.'.format(authors)]
            index = randrange(len(self.conf_author))
            return self.conf_author[index]
        
        if 'author check' in candidate_outputs:
            is_in = candidate_outputs['is in']
            missing_authors = candidate_outputs['missing authors']
            result = ''
            if len(is_in) > 0:
                in_authors = ', '.join(str(ele) for ele in is_in)
                self.author_check_yes = ['{in_authors} will be present.'.format(authors),
                                         '{in_authors} will be participating.'.format(authors),
                                         '{in_authors} will be there.'.format(authors),
                                         '{in_authors} is going to be there.'.format(authors),
                                         '{in_authors} will be presenting.'.format(authors)]
                index = randrange(len(self.author_check_yes))
                result = self.author_check_yes[index]
            if len(missing_authors) > 0:
                miss_authors = ', '.join(str(ele) for ele in missing_authors)
                self.author_check_no = ['{miss_authors} will not be present'.format(authors),
                                        '{miss_authors} will not be participating.'.format(authors),
                                        '{miss_authors} will not be there'.format(authors),
                                        '{miss_authors} is not there'.format(authors),
                                        '{miss_authors} is not going to be there'.format(authors)]
                index = randrange(len(self.author_check_no))
                result += self.author_check_no[index]
            return result
        
        if 'where author' in candidate_outputs:
            a = ', '.join(str(ele) for ele in authors)
            result = []
            for key in candidate_outputs['where author'].keys():
                if len(candidate_outputs['where author'][key]) > 0:
                    result.append(candidate_outputs['where author'][key])
            
            if len(result) > 0:
                ans = ', '.join(str(ele) for ele in result)
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
        
        if 'conf rec' in candidate_outputs:
            result = candidate_outputs['conf rec']
            ans = ''
            for entity in entities:
                ans += entity.capitalize() + ': ' + result['entity'] + '\n'

            self.conf_rec = ['I recommend the following you:\n {}.'.format(ans),
                             'Based on your preferences, I recommend:\n {}.'.format(ans),
                             'Looking at every all the conference events, this seems to be most related to your interests:\n {}'.format(ans),
                             'I found this may relate to what you\'re looking for:\n {}'.format(ans),
                             'These events could be a good match for you:\n {}'.format(ans)]
            index = randrange(len(self.conf_rec))
            return self.conf_rec[index]
        
        if 'session papers' in candidate_outputs:
            result = candidate_outputs['session papers']
            ans = ', '.join(str(ele) for ele in result)
            self.session_papers = ['The session paper titles are:\n {}'.format(ans),
                                   'The papers being presented in the session are:\n {}'.format(ans),
                                   'Papers to be presented are:\n {}'.format(ans),
                                   'I found these research papers will be presented:\n {}'.format(ans),
                                   'Here are all the papers being presented in the session:\n {}'.format(ans)]
            index = randrange(len(self.session_papers))
            return self.session_papers[index]
        
        if 'userprofile' in candidate_outputs:
            result = candidate_outputs['userprofile']
            a = authors[0]
            self.userprofile = ['I found that {} is best related to {}\'s works.'.format(result, a),
                                '{} is most related to {}\'s works.'.format(result, a),
                                'I recommend {} to be most related to {}\'s works.'.format(result, a),
                                '{} seems to be of close topic in relation to {}\'s works'.format(result, a),
                                'Based on {}\'s works, {} is what you\'re looking for.'.format(a, result)]
            index = randrange(len(self.userprofile))
            return self.userprofile[index]

        if 'conf paper title rec' in candidate_outputs:
            result = candidate_outputs['conf paper title rec']
            self.conf_paper_title_rec = ['{} is related to your interests.'.format(result),
                                         '{} is closely associated with what you\'re looking for.'.format(result),
                                         'I recommend {}.'.format(result),
                                         'Based on all the accepted papers, {} best matches your needs.'.format(result),
                                         'My personal recommendation for you is {}.'.format(result)]
            index = randrange(len(self.conf_paper_title_rec))
            return self.conf_paper_title_rec[index]

        if 'paper qa' in candidate_outputs:
            result = candidate_outputs['paper qa']
            self.paper_qa = ['{} is closely related to your interests.'.format(result),
                             '{} is closely associated with what you\'re looking for.'.format(result),
                             'I recommend {}.'.format(result),
                             'My personal recommendation for you is {}.'.format(result),
                             'It seems that {} is closely related to your preferences.'.format(result)]
            index = randrange(len(self.paper_qa))
            return self.paper_qa[index]
    
    def get_output(self, conv, candidate_outputs):
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

        #timestamp = util.current_time_in_milliseconds()
        #if timestamp <= conv[0].timestamp:
        #    raise Exception('There is a problem in the output timestamp!')
        #return Message(user_interface, user_id, user_info, msg_info, text, timestamp)

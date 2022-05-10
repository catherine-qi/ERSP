"""
The conference event information retrieval module.
Comprises of retrieving simple information about conference events (session
paper titles, author participation, etc.), and also recommendation based on
keyword or user profile.
Author: Catherine Qi
"""

import json

from sentence_transformers import SentenceTransformer
from ..retriever.dense_retriever import DenseRetriever
from ..retriever.sparse_retriever import SparseRetriever
from ..retriever.paper_retriever import PaperRetrieval


class ConferenceRetrieval():
    """
    ConferenceRetrieval is  class that retrieves needed conference information.
    The information need is based on what is decided by the query classification and dialog manager.

		Args:
			params(dict): A dict of parameters.
	"""
    def __init__(self, params):
        self.params = params

        self.data = self.get_data() # The conference dataset as a dict

        # Two retriever models are used: sparse and dense.
        # Dense retriever is used to recommend related events, while sparse retriever is used to find basic
        # conference information (session paper titles, author participation, etc.).
        self.model = SentenceTransformer('sentence-transformers/allenai-specter')
        self.dense_index = DenseRetriever(self.model)
        self.sparse_retriever = SparseRetriever()

    def get_data(self):
        """
		Opens the conference dataset file and loads it in as a dict.

		Args:
		
		Returns:
			A dict representing the conference dataset.
		"""
        data = None
        with open(self.params['conf dataset'], 'r') as f:
            data = json.load(f)
        f.close()
        return data
    
    def get_attr(self, conf, entity, attr):
        """
		Helper method; given the conference name + year and entity wanted,
        return all specified attributes of each dict. For example, used when we only want
        session (entity) names (attr) of SIGIR 21 (conf).

		Args:
			conf(str): The wanted conference name + year.
			entity(str): The wanted entity.
            attr(str): The wanted attribute (must be valid, please be cautious and look at what attributes
            each entity type has. Not all entities have the same attribute names).
		
		Returns:
			A list of the wanted attributes.
		"""
        lst = []
        for key, value in self.data.items():
            if key == conf:
                for e in value[entity]:
                    if isinstance(e[attr], list): # Some attributes may be of type list. 
                                                  # If this is the case, append each list element rather than the entire list.
                        for i in e[attr]:
                            lst.append(i)
                    else:
                        lst.append(e[attr])
        return lst
    
    def search(self, conf, entity, name):
        """
		Helper method; given the conference name + year, entity wanted, and the name of the event,
        return that specified event's dict (all events are stored as a dict).

		Args:
			conf(str): The wanted conference name + year.
			entity(str): The wanted entity.
            name(str): The wanted name of the conference event.
		
		Returns:
			A dict of the specified event.
		"""
        for key, value in self.data.items():
            if key == conf:
                for e in value[entity]:
                    if e['name'] == name:
                        return e

    """
    Could be used for scheduling purposes in finding times of a specified conference.
    def time(self, conv_list):
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        if len(entities) > 1:
            return 'too many entities'
        
        session_names = self.get_attr(wanted_conf, entities[0], 'name')
        self.sparse_retriever.index_documents(session_names)
        sparse_results = self.sparse_retriever.search([conv_list[0].text])[0]
        sparse_results = [r[0] for r in sparse_results][0]

        return self.search(wanted_conf, entities[0], session_names[sparse_results])['date']
    """
    
    def author_list(self, conv_list):
        """
        Finds the event specified from user's most current message, and returns all authors
        participating in that event (based on the dataset). Uses sparse retrieval to find
        what session the user is referring to.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A list of all participating authors in the event specified from user's message.
		"""
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        names = [] # Store the event names that user referred to. Done with sparse retrieval.
        for entity in entities:
            valid = self.get_attr(wanted_conf, entity, 'name')
            self.sparse_retriever.index_documents(valid)
            sparse_results = self.sparse_retriever.search([conv_list[0].text])[0]

            sparse_results = [i[0] for i in sparse_results][0]
            names.append(valid[sparse_results])
        
        counter = 0 # User may have referred to multiple entities, so len(names) may be > 1. Used to iterate through names
        authors = []
        for entity in entities:
            wanted_entity = self.search(wanted_conf, entity, names[counter])['authors']
            for a in wanted_entity:
                authors.append(a)
            counter += 1
        return authors
    
    def author_check(self, conv_list):
        """
        Checks if author is participating in a specified conference event.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A dict with key 'is in' that maps to a list of authors participating in a specified event(s), and
            key 'missing authors' that maps to a list of authors not participating in the specified event(s).
		"""
        curr_da = self.params['DA list'][0]
        authors = curr_da['authors']

        if len(authors) < 1: # Author name not detected
            return 'no author'

        author_list = self.author_list(conv_list) # List of all authors in specified events
        
        is_in = []
        missing_authors = []
        for a in authors:
            flag = False
            for arr in author_list:
                if a in arr: # If author is in any 1 event specified by user, mark them as a participator
                    flag = True
                    is_in.append(a)
                    break
            if not flag: # Author was not found to be in any event specified by user
                missing_authors.append(a)
        return{'is in': is_in, 'missing authors': missing_authors}
    
    def where_author(self):
        """
        Checks if author is participating in a specified conference event.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A dict with key 'is in' that maps to a list of authors participating in a specified event(s), and
            key 'missing authors' that maps to a list of authors not participating in the specified event(s).
		"""
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']
        authors = curr_da['authors']

        if len(authors) < 1: # Author name not detected
            return 'no author'
        
        result = {}
        for a in authors: # Every author name will be a key that maps to a dict.
            result[a] = {'session': [], # This dict will contain keys of all basic events found in all conferences (session, workshop, tutorial).
                         'workshop': [], # Every key maps to an array that contains the event name the author was found in.
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
        """
        Finds the most relevant conference event to the user's most recent message. Also allows some author filtering
        such that it only looks recommends conferences with a specified author(s) participating.
        Uses dense retriever to compute similarities.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            authors_wanted(bool): True if author filtering wanted, else False.
		
		Returns:
			A dict with a key for each entity specified. For each key, the value is the recommendation.
		"""
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        recommendations = {}
        for entity in entities:
            similarities = [] # Stores the computed similarity value for each entity event
            names = [] # Stores the name of the entity events
            if authors_wanted: # Find all entity event names that specified authors are in
                dict = self.where_author()
                for key, value in dict.items():
                    if len(value[entity]) < 1:
                        return key + ' not in any ' + entity
                    for n in value[entity]:
                        if n not in names:
                            names.append(n)
            else: # Get all entity event names
                names = self.get_attr(wanted_conf, entity, 'name')
            for n in names: # Computing the similarities for each entity event
                titles = []
                if entity == 'session':
                    titles = self.search(wanted_conf, entity, n)['paper titles'] # Sessions use paper titles to compute similarity
                else:
                    titles = [self.search(wanted_conf, entity, n)['abstract']] # Events not sessions use abstracts to compute similarity
                titles.append(n)
                self.dense_index.create_index_from_documents(titles)
                dense_results = self.dense_index.search([conv_list[0].text])[0]
                dense_results = [i[1] for i in dense_results][0]
                similarities.append(dense_results)
            for i in range(0, curr_da['last similarity']): # NOT USED ANYMORE (made for recommending another event)
                ind = similarities.index(max(similarities)) # NOT USED ANYMORE (made for recommending another event)
                similarities.pop(ind) # NOT USED ANYMORE (made for recommending another event)
                names.pop(ind) # NOT USED ANYMORE (made for recommending another event)
            recommendations[entity] = names[similarities.index(max(similarities))] # Set the recommendation to the event with highest similarity
        return recommendations

    def get_papers(self, conv_list):
        """
        Finds all paper titles of the given session name from user's most recent message.
        Uses sparse retriever to find the wanted session.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A list of the session paper titles.
		"""
        curr_da = self.params['DA list'][0]
        wanted_conf = curr_da['main conference']['conference'] + curr_da['main conference']['year']
        entities = curr_da['entity']

        if 'session' not in entities: # Other events are assumed to not have paper titles associated with them as of currently.
            return 'only session has papers'
        
        names = self.get_attr(wanted_conf, 'session', 'name')
        self.sparse_retriever.index_documents(names)
        sparse_results = self.sparse_retriever.search([conv_list[0].text])[0]
        sparse_results = [i[0] for i in sparse_results][0]
        titles = self.search(wanted_conf, 'session', names[sparse_results])['paper titles']
        return titles
    
    def best_paper_title(self, conv_list):
        """
        Computes the most relevant paper title of a specified session based on user's most recent message.
        Uses dense retriever to compute similarity.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
		
		Returns:
			A str of the most relevant paper title of a specified conference event.
		"""
        curr_da = self.params['DA list'][0]
        
        titles = self.get_papers(conv_list)
        self.dense_index.create_index_from_documents(titles)
        dense_results = self.dense_index.search([conv_list[0].text])[0]
        dense_results = [i[0] for i in dense_results][curr_da['last similarity']]
        return titles[dense_results]

    def related_author_session(self, conv_list, paper_retrieval):
        """
        Finds an entity event most similar to a user profile.
        Uses dense retriever to compute similarities.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            paper_retrieval(PaperRetrieval): The paper retriever module.
		
		Returns:
			A dict with a key for each entity specified. For each key, the value is the recommendation.
		"""
        curr_da = self.params['DA list'][0]
        curr_da['authors'] = [curr_da['authors'][0]]
        authors = curr_da['authors']

        author_data = paper_retrieval.user_profile(authors[0], conv_list[0].text)
        author_data = " ".join(author_data)
        new_message = conv_list[0]
        new_message.text = author_data # Overwrites the current message with the user profile to create a temporary Message
                                       # to be used so that the input type of best_entity() matches.
        recommendation = self.best_entity([new_message])
        return recommendation
    
    def get_results(self, conv_list, index):
        """
        Calls a specific method based on index.

		Args:
			conv_list(list): List of interaction_handler.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            index(int): Maps to the corresponding question in the question list, located in QueryClassification.
		
		Returns:
			The value returned by the called method.
		"""
        if index in range(0,2): # What author will be participating in <ENTITY_NAME>
            return self.author_list(conv_list)
        if index == 2: # Will <AUTHOR_NAME> be participating in <ENTITY_NAME>
            return self.author_check(conv_list)
        if index == 3: # What <ENTITY_NAME> will <AUTHOR_NAME> be participating in
            return self.where_author()
        if index in range (4,6): # Recommend a <ENTITY_NAME> about <KEYWORD> (that <AUTHOR_NAME> is in)
            return self.best_entity(conv_list) if len(self.params['DA list'][0]['authors']) < 1 else self.best_entity(conv_list, True)
        if index == 6: # What papers does the session cover
            return self.get_papers(conv_list)
        if index in range(7,9): # Recommend a <ENTITY_NAME> related to <AUTHOR_NAME> works
            return self.related_author_session(conv_list, self.params['actions']['retrieval'])
        if index in range(9,11): # What are some papers in the session about <KEYWORD>
            return self.best_paper_title(conv_list)
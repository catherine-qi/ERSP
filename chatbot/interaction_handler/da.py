class DialogueAct:
    def __init__(self, intent, intent_index, main_conference, entity, query_vector, authors):
         self.da = {'intent': intent,
                   'intent index': intent_index,
                   'main conference': main_conference,
                   'entity': entity,
                   'query vector': query_vector,
                   'authors': authors}
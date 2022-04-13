class DialogueAct:
    def __init__(self, intent, main_conference, entity, query_vector, authors):
        self.intent = intent
        self.main_conference = main_conference
        self.entity = entity
        self.query_vector = query_vector
        self.authors = authors
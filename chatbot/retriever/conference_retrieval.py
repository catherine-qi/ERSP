import json

class ConferenceRetrieval():
    def __init__(self, params):
        self.params = params
    
    def get_data(self):
        with open('ERSP/conference_data.json', 'r') as f:
            return json.load(f)
    
if __name__ == "__main__":
    c = ConferenceRetrieval({"nothing": "here"})
    print(c.get_data())
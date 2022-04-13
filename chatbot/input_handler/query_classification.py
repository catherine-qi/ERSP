import pickle
import faiss
import os
import re
import json

from sentence_transformers import SentenceTransformer
from flair.data import Sentence
from flair.models import SequenceTagger
from ..interaction_handler.msg import Message
from ..interaction_handler.da import DialogueAct
from ..retriever.dense_retriever import DenseRetriever
from flask import request, Flask, jsonify
from flask_cors import CORS

class QueryClassification:
	def __init__(self, conv_list, path):
		self.app = Flask(__name__)
		CORS(self.app)

		self.ques_list = ["Accepted papers in related to", 
						"Recommend session or workshop in related to", 
						"When is the session or workshop", 
						"Authors participating in the session or workshop", 
						"What is the session or workshop about",
						"What sessions or workshops are in",
						"Papers related to",
						"Which authors published most relevant papers to",
						"Give me papers made by",
						"Papers written by"]
		self.conv_list = conv_list
		self.path = path
		self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
		self.entities = [['paper',  'article'], ['session'], ['workshop']]

		self.dense_index = DenseRetriever(self.model)
		if os.path.exists('{}/index.pkl'.format(self.path)):
			print("true") #testing purposes
			self.dense_index.load_index('{}/index.pkl'.format(self.path))
		else:
			print("false") #testing purposes
			self.dense_index.create_index_from_documents(self.ques_list)
			self.dense_index.save_index(index_path='{}/index.pkl'.format(self.path), vectors_path='{}/vectors.pkl'.format(self.path))
		
		self.query_vector = None

		self.tagger = SequenceTagger.load("flair/ner-english-large")
	
	def serve(self, port=80):
		self.build_endpoints()
		self.app.run(host='0.0.0.0', port=port)
	
	def build_endpoints(self):
		@self.app.route('/encode', methods=['POST', 'GET'])
		def encode_endpoint():
			text = str(request.args.get('text'))
			self.conv_list.insert(0, str(text))
			da = self.create_DA()
			temp = self.ques_list[da.intent]
			results = json.dumps(temp, indent=4)
			return results
	
	def vectorize(self, batch_size=1):
		self.query_vector = self.model.encode(conv_list[0], batch_size)
	
	def sim_ques(self, query_vector):
		dense_results = self.dense_index.search([query_vector], False)[0]
		dense_results = [i[0] for i in dense_results]

		return dense_results[0]

	def main_conference(self, text_msg):
		text = text_msg.lower()
		if 'sigir' in text:
			return 'sigir'
		return None
	
	def entity_keywords(self, text_msg):
		text = text_msg.lower()
		for entity in self.entities:
			for word in entity:
				if word in text:
					return word
		return 'ERROR'
	
	def get_authors(self, text_msg):
		authors = []
		sentence = Sentence(text_msg)
		self.tagger.predict(sentence)
		for entity in sentence.get_spans('ner'):
			if entity.get_label("ner").value == "PER":
				authors.append(entity.text)
		return authors
	
	def create_DA(self):
		self.vectorize()
		intent = self.sim_ques(self.query_vector)
		conference = self.main_conference(self.conv_list[0])
		entity = self.entity_keywords(self.conv_list[0])
		authors = self.get_authors(self.conv_list[0])
		return DialogueAct(intent, conference, entity, self.query_vector, authors)
	
if __name__ == "__main__":
	conv_list = ["Is Catherine Qi going to be at SIGIR?"]
	q = QueryClassification(conv_list, "D:/ERSP/chatbot/input_handler")
	#da = q.create_DA()
	#print(da.intent)
	#print(da.main_conference)
	#print(da.entity)
	#print(da.authors)
	q.serve(9000)
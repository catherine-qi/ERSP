import logging
import pickle
import regex as re
import json
import pandas as pd
from vector_index import VectorIndex
from sentence_transformers import SentenceTransformer


class DenseRetriever:
    def __init__(self, model, batch_size=1, use_gpu=False):
        self.model = model
        self.vector_index = VectorIndex(768)
        self.batch_size = batch_size
        self.use_gpu = use_gpu

    def create_index_from_documents(self, documents):
        logging.info('Building index...')

        self.vector_index.vectors = self.model.encode(
            documents, batch_size=self.batch_size)
        self.vector_index.build(self.use_gpu)

        logging.info('Built index')

    def create_index_from_vectors(self, vectors_path):
        logging.info('Building index...')
        logging.info('Loading vectors...')
        self.vector_index.vectors = pickle.load(open(vectors_path, 'rb'))
        logging.info('Vectors loaded')
        self.vector_index.build(self.use_gpu)

        logging.info('Built index')

    def search(self, queries, limit=1000, probes=512, min_similarity=0):
        query_vectors = self.model.encode(queries, batch_size=self.batch_size)
        ids, similarities = self.vector_index.search(
            query_vectors, k=limit, probes=probes)
        results = []
        for j in range(len(ids)):
            results.append([
                (ids[j][i], similarities[j][i]) for i in range(len(ids[j])) if similarities[j][i] > min_similarity
            ])
        return results

    def load_index(self, path):
        self.vector_index.load(path)

    def save_index(self, index_path='', vectors_path=''):
        if vectors_path != '':
            self.vector_index.save_vectors(vectors_path)
        if index_path != '':
            self.vector_index.save(index_path)


arxiv_path = 'C:\\Users\\VedCh\\ERSP\\archive\\arxiv-metadata-oai-snapshot.json'

titles = []
abstracts = []
authors = []


def get_metadata():
    with open(arxiv_path, 'r') as f:
        for line in f:
            yield line


metadata = get_metadata()
count = 0

# EXTRACTING THE JSON FROM ARXIV DATASET AND PUTTING IT IN A DATAFRAME OF THE RIGHT FORMAT

for paper in metadata:  # retrieves and loads each paper in JSON file
    paper_dict = json.loads(paper)
    ref = paper_dict.get('journal-ref')

    try:  # below code may cause error due to some formatting issues, hence the reason for try/except--only append data that causes no error
        # Commented out code is actual date of publication, however some entries are missing this
        #year = int(ref[-4:])
        # years.append(year)
        authors.append(paper_dict.get('authors'))
        titles.append(paper_dict.get('title'))
        abstracts.append(paper_dict.get('abstract'))
    except:
        pass
    count = count+1
    if count == 10:
        break

df = pd.DataFrame({  # convert the json to a pandas dataframe
    'title': titles,
    'abstract': abstracts,
    'authors': authors
})

for row_label in df.index:  # convert the multiple authors separated by ', and' to a list
    df['authors'][row_label] = re.split(
        ', | and ', df['authors'][row_label])

# concat the metadata into one column. Final dataframe is authors, title, abstracts(concatenated metadata)
df['abstract'] = df['title'] + df['abstract']

if __name__ == "__main__":
    documents = ["Information Retrieval", "Biology", "Artificial Intelligence"]
    model = SentenceTransformer('sentence-transformers/allenai-specter')
    dense_retriever = DenseRetriever(model, batch_size=1, use_gpu=False)
    dense_retriever.create_index_from_documents(documents)

    query = ["Machine Learning"]
    results = dense_retriever.search(query)

    print(results)

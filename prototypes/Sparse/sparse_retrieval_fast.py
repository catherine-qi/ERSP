import pandas as pd
import json
import regex as re
import numpy as np

#from sparse_retrieval import SparseRetrieverFast
# change this to whatever path you're using
import logging
import os
import tantivy

from tqdm import tqdm


class SparseRetrieverFast:
    def __init__(self, path='sparse_index', load=True):
        if not os.path.exists(path):
            os.mkdir(path)
        schema_builder = tantivy.SchemaBuilder()
        schema_builder.add_text_field("body", stored=False)
        schema_builder.add_unsigned_field("doc_id", stored=True)
        schema = schema_builder.build()
        self.index = tantivy.Index(schema, path=path, reuse=load)
        self.searcher = self.index.searcher()

    def index_documents(self, documents):
        logging.info(
            'Building sparse index of {} docs...'.format(len(documents)))
        writer = self.index.writer()
        for i, doc in enumerate(documents):
            writer.add_document(tantivy.Document(
                body=[doc],
                doc_id=i
            ))
            if (i+1) % 100000 == 0:
                writer.commit()
                logging.info('Indexed {} docs'.format(i+1))
        writer.commit()
        logging.info('Built sparse index')
        self.index.reload()
        self.searcher = self.index.searcher()

    def search(self, queries, topk=100):
        results = []
        for q in tqdm(queries, desc='searched'):
            docs = []
            # try:
            query = self.index.parse_query(q, ["body"])
            scores = self.searcher.search(query, topk).hits
            docs = [(self.searcher.doc(doc_id)['doc_id'][0], score)
                    for score, doc_id in scores]
            # except:
            # pass
            results.append(docs)

        return results


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
    df['authors'][row_label] = re.split(', | and ', df['authors'][row_label])

# concat the metadata into one column. Final dataframe is authors, title, abstracts(concatenated metadata)
df['abstract'] = df['title'] + df['abstract']

#documents = df["abstract"].values.tolist()
if __name__ == "__main__":
    documents = ["Information Retrieval", "Biology", "Artificial Intelligence"]
    print(documents)

    sparse_retriever = SparseRetrieverFast(path='sparse_index')
    sparse_retriever.index_documents(documents)

    query = ["Machine Learning"]
    results = sparse_retriever.search(query)

    print(results)

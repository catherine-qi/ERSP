from dense_retrieval import DenseRetriever
from sentence_transformers import SentenceTransformer
#from operator import itemgetter
#import globals
from pymongo import MongoClient

import pandas as pd
import json
import regex as re
import numpy as np
import pickle
import os

directory_path = os.getcwd()
directory_path = directory_path+'/dense_retriever_index'

# mongodb://localhost:27017
connection_string = input("Enter connection string: ")
#globals.connection_string = connection_string
client = MongoClient(connection_string)
database = input("Enter database name: ")
#globals.database = database
db = client[database]
collection = input("Enter collection name: ")
#globals.collection = collection
col = db[collection]


if(os.path.exists(directory_path)):
    # read the pickle file
    picklefile = open('dense_retriever_index', 'rb')
    # unpickle the file
    dense_retriever = pickle.load(picklefile)
    # close file
    picklefile.close()

    def result_search(author):
        author_dict = col.find_one({"authors": author})
        query = author_dict['title'] + author_dict['abstract']
        queries = []
        queries.append(query)
        result = dense_retriever.search(queries)
        index_num = result[0][0][1]-1
        index_num = int(index_num)
        result_author = col.find_one({"index": index_num})
        print(result_author['title'])

    author_search = input("Enter author name: ")
    result_search(author_search)

else:
    # change this to whatever path you're using
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
            authors.append(paper_dict.get('authors'))
            titles.append(paper_dict.get('title'))
            abstracts.append(paper_dict.get('abstract'))
        except:
            pass
        count = count+1
        if count == 10:
            break

    df_indexed = pd.DataFrame({  # convert the json to a pandas dataframe
        'title': titles,
        'abstract': abstracts,
        'authors': authors
    })

    df_mongo = pd.DataFrame({  # convert the json to a pandas dataframe
        'authors': authors,
        'title': titles,
        'abstract': abstracts
    })

    for row_label in df_indexed.index:  # convert the multiple authors separated by ', and' to a list
        df_indexed['authors'][row_label] = re.split(
            ', | and ', df_indexed['authors'][row_label])

    for row_label in df_mongo.index:  # convert the multiple authors separated by ', and' to a list
        df_mongo['authors'][row_label] = re.split(
            ', | and ', df_mongo['authors'][row_label])

    parsed_col = 'authors'
    df_mongo = pd.DataFrame({  # convert it to a new dataframe such that each author gets their own entry with the other columns preserved
        col: np.repeat(df_mongo[col].values, df_mongo[parsed_col].str.len())
        for col in df_mongo.columns.difference([parsed_col])
    }).assign(**{parsed_col: np.concatenate(df_mongo[parsed_col].values)})[df_mongo.columns.tolist()]

    # concat the metadata into one column. Final dataframe is authors, title, abstracts(concatenated metadata)
    df_indexed['abstract'] = df_indexed['title'] + df_indexed['abstract']

    documents = df_indexed["abstract"].values.tolist()

    # generate the similarities using faiss
    model = SentenceTransformer('sentence-transformers/allenai-specter')
    documents = df_indexed["abstract"].values.tolist()

    dense_retriever = DenseRetriever(model, batch_size=1, use_gpu=False)
    dense_retriever.create_index_from_documents(documents)
    # create a pickle file
    picklefile = open('dense_retriever_index', 'wb')
    # pickle the dictionary and write it to file
    pickle.dump(dense_retriever, picklefile)
    # close the file
    picklefile.close()

    df_mongo.reset_index(inplace=True)  # Reset Index
    data_dict = df_mongo.to_dict("records")  # Convert to dictionary

    col.insert_many(data_dict)


'''
df = pd.DataFrame({  # convert the json to a pandas dataframe
    'authors': authors,
    'title': titles,
    'abstract': abstracts,
    'date': years
})

for row_label in df.index:  # convert the multiple authors separated by ', and' to a list
    df['authors'][row_label] = re.split(', | and ', df['authors'][row_label])

# reformatting the dataframe
parsed_col = 'authors'
df = pd.DataFrame({  # convert it to a new dataframe such that each author gets their own entry with the other columns preserved
    col: np.repeat(df[col].values, df[parsed_col].str.len())
    for col in df.columns.difference([parsed_col])
}).assign(**{parsed_col: np.concatenate(df[parsed_col].values)})[df.columns.tolist()]

# concat the metadata into one column. Final dataframe is authors, title, abstracts(concatenated metadata)
for row_label in df.index:  # concat the data from title, abstract, title into one for preprocessing
    df['abstract'][row_label] = df['title'][row_label] + \
        df['abstract'][row_label] + df['date'][row_label]
df = df.iloc[:, :3]  # extracts the first 3 columns because that's all we need
concat_df = df.iloc[:, :2]

# generate the similarities using faiss
model = SentenceTransformer('sentence-transformers/allenai-specter')
batch_size = 1
use_gpu = False
documents = df["abstract"].values.tolist()

dense_retriever = DenseRetriever(model, batch_size, use_gpu)
dense_retriever.create_index_from_documents(documents)
queries = []
similar_titles = []
similarity_values = []
for document in documents:
    queries.append(document)
results = dense_retriever.search(queries)
for result in results:
    max_tuple = sorted(result, key=lambda x: x[1], reverse=True)[1]
    max_index = max_tuple[0]
    max_similarity = max_tuple[1]
    similar_titles.append(df['title'][max_index])
    similarity_values.append(max_similarity)
    """ This is for max value rather than second highest value. Peformance is better
    max_index = max(result, key=itemgetter(1))[0]
    max_similarity = max(result, key=itemgetter(1))[1]
    similar_titles.append(df['title'][max_index])
    similarity_values.append(max_similarity)
    """

similartitle_df = pd.DataFrame(similar_titles, columns=['similar title'])
similarity_df = pd.DataFrame(similarity_values, columns=['similarity value'])
result_df = pd.concat([concat_df, similartitle_df, similarity_df], axis=1)
print(result_df)
'''

# for document in documents:
#    results=dense_retriever.search([document])

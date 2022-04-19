import pandas as pd
import json
import regex as re
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


# change this to whatever path you're using
arxiv_path = 'C:\\Users\\VedCh\\ERSP\\archive\\arxiv-metadata-oai-snapshot.json'

titles = []
abstracts = []
authors = []
years = []


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
        years.append(paper_dict.get('update_date'))
        authors.append(paper_dict.get('authors'))
        titles.append(paper_dict.get('title'))
        abstracts.append(paper_dict.get('abstract'))
    except:
        pass
    count = count+1
    if count == 10:
        break

df = pd.DataFrame({  # convert the json to a pandas dataframe
    'authors': authors,
    'title': titles,
    'abstract': abstracts,
    'date': years
})

for row_label in df.index:  # convert the multiple authors separated by ', and' to a list
    df['authors'][row_label] = re.split(', | and ', df['authors'][row_label])

parsed_col = 'authors'
df = pd.DataFrame({  # convert it to a new dataframe such that each author gets their own entry with the other columns preserved
    col: np.repeat(df[col].values, df[parsed_col].str.len())
    for col in df.columns.difference([parsed_col])
}).assign(**{parsed_col: np.concatenate(df[parsed_col].values)})[df.columns.tolist()]

# PREPROCESSING THE DATA

for row_label in df.index:  # concat the data from title, abstract, title into one for preprocessing
    df['abstract'][row_label] = df['title'][row_label] + \
        df['abstract'][row_label] + df['date'][row_label]
df = df.iloc[:, :3]  # extracts the first 3 columns because that's all we need
concat_df = df.iloc[:, :2]

nltk.download('punkt')


def tokenize(column):
    # Tokenizes a Pandas dataframe column and returns a list of tokens.
    tokens = nltk.word_tokenize(column)
    return [w for w in tokens if w.isalpha()]


df['tokenized'] = df.apply(lambda x: tokenize(x['abstract']), axis=1)
df[['authors', 'title', 'tokenized']].head()

nltk.download('stopwords')


def remove_stopwords(tokenized_column):
    # Return a list of tokens with English stopwords removed.
    stops = set(stopwords.words("english"))
    return [word for word in tokenized_column if not word in stops]


df['stopwords_removed'] = df.apply(
    lambda x: remove_stopwords(x['tokenized']), axis=1)
df[['authors', 'title', 'stopwords_removed']].head()


def apply_stemming(tokenized_column):
    # Return a list of tokens with Porter stemming applied.
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in tokenized_column]


df['porter_stemmed'] = df.apply(
    lambda x: apply_stemming(x['stopwords_removed']), axis=1)
df[['authors', 'title', 'porter_stemmed']].head()


def rejoin_words(tokenized_column):
    # Rejoins a tokenized word list into a single string.
    return (" ".join(tokenized_column))


df['preprocessed'] = df.apply(
    lambda x: rejoin_words(x['porter_stemmed']), axis=1)
df[['authors', 'title', 'preprocessed']].head()

# list_allwords is a list(array) of all the preprocessed data. Each element in the list corresponds to the preprocessed data for each author
list_allwords = df["preprocessed"].values.tolist()

# VECTORIZE THE PREPROCESSED DATA
coun_vect = CountVectorizer()
count_matrix = coun_vect.fit_transform(list_allwords)
# count_array is a 2d array. each element is a vector corresponding to the author
count_array = count_matrix.toarray()

# Convert sparse matrix to df
# This gives u a dataframe view of word by word count w.r.t author
df = pd.DataFrame(data=count_array, columns=coun_vect.get_feature_names())


# COSINE SIMILARITY
df_1 = pd.DataFrame(cosine_similarity(df, dense_output=True))

t = []
# Create list of lists: each entry has [(row number,index position,similarity value)]
for j, k in enumerate(df_1.values):
    for n in range(len(k)):
        t.append([j, n, k[n]])

# When the index and row number are same then we have 1. Because, the matrix are corresponding to same preprocessed string, therefore I make it equal to 0 so we can find the max value for each row.
qq = []
for i in range(len(t)):
    if t[i][0] == t[i][1]:
        qq.append([t[i][0], t[i][1], 0])
    else:
        qq.append(t[i])

u = defaultdict(list)
# use the lists of lists from above and create a dictionary list. This will match all of our values back to a dataframe format but, with the updated zero values.
for i in range(len(qq)):
    u[qq[i][0]].append(qq[i][2])

updated_df = pd.DataFrame(u)

# find the position of each max value per row
position_maxVal = []
for i in range(len(updated_df)):
    position_maxVal.append(np.argmax(updated_df[i]))

sent_comp = []
for j in position_maxVal:  # list of highest similarity index positions
    # this creates in order our title w/ highest similiarity by row
    sent_comp.append(concat_df['title'][j])

#  based on highest similarity value per row as DF
similar_title = pd.DataFrame(sent_comp, columns=['Similar title'])

# similiarity values rounded 4 decimal places finding max value per row
similarity_value = pd.DataFrame(round(updated_df.max(axis=1), 4),
                                columns=['Similarity Value'])

# final similarity dataframe
cos_sim_df = pd.concat([concat_df, similar_title, similarity_value], axis=1)

print(cos_sim_df)
'''
df_vectorized = df  # df_vectorized is a dataframe with author and the author's vector
df_vectorized.rename(columns={'preprocessed': 'vector'}, inplace=True)
row_count = 0
for row_label in df_vectorized.index:
    df_vectorized['vector'][row_label] = count_array[row_count]
    row_count = row_count+1

print(df_vectorized)
'''
'''
df = pd.DataFrame(data=count_array,columns = coun_vect.get_feature_names()) # This gives u a dataframe view of word by word count w.r.t author
print(len(count_array)) #Number of authors
print(len(count_array[0])) #Number of distinct words (elements of the vector)
'''

'''
# To convert dataframe into json
json_records = df.to_json(orient='records')
print("json_records = ", json_records, "\n")
'''

from sklearn.base import BaseEstimator, TransformerMixin
import pickle
import pandas as pd
import os
from spacy.lang.fr import French

class TextStats(BaseEstimator, TransformerMixin):
    """Extract features from each document for DictVectorizer"""

    def fit(self, x, y=None):
        return self

    def transform(self, descs):
        return [{'stats_num_sentences': text.count(' ')}
                for text in descs]


class SingleColumnSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]

def saveMyModel(model, path):
    with open(path, 'wb') as f :
        pickle.dump(model,f)


def split_into_lemmas_spacy(desc) :
    nlp = French()
    doc = nlp(desc)
    return [w.lemma_ for w in doc]



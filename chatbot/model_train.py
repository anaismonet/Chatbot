#!/usr/bin/env python
# coding: utf-8

import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import string
from nltk.corpus import stopwords
from sklearn import metrics
from sklearn import model_selection
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.tree import DecisionTreeClassifier
from spacy.lang.fr import French
import os
import pickle
import joblib
from joblib import dump, load
import dill
from classes_func import SingleColumnSelector
from classes_func import TextStats
from classes_func import saveMyModel
from classes_func import split_into_lemmas_spacy

# Source : https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer.html


def train():
    database_path = os.getcwd() + "/data/"

    df = pd.DataFrame()
    for filename in os.listdir(database_path):
        if not filename.startswith('.'):
            df = df.append(pd.read_excel(database_path + filename, names = ['attente','message']), ignore_index = True)

    df = df.drop_duplicates()

    X = df['message']
    X = pd.DataFrame(X)
    y = df['attente']
    y = pd.DataFrame(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)


    nltk_stopwords = stopwords.words('french')+list(string.punctuation)

    # Objet TfidfVectorizer
    msg_vectorizer = TfidfVectorizer(tokenizer=split_into_lemmas_spacy,lowercase=True,stop_words=nltk_stopwords,min_df=0.001)

    # Pipeline spécifique
    msg_pipeline = make_pipeline(SingleColumnSelector(key="message"), msg_vectorizer)

    msg_pipeline.fit(X_train)
    
    stats_vectorizer = DictVectorizer()

    # Pipeline spécifique
    stats_pipeline = make_pipeline(SingleColumnSelector(key="message"),TextStats(),stats_vectorizer)

    stats_pipeline.fit(X_train)
    
    # Union des traits
    union = FeatureUnion(transformer_list = [
            ("msg_feature", msg_pipeline),
        ("stats_features", stats_pipeline)
        ])

    # Chaîne de prétraitement globale, composée de l'union des chaînes
    preprocess_pipeline = make_pipeline(union)

    preprocess_pipeline.fit(X_train)
    
    classifier_pipeline = make_pipeline(preprocess_pipeline,RandomForestClassifier())
    # Apprentissage avec les données d'entraînement
    classifier_pipeline.fit(X_train, y_train)

    # Saving model
    filename = 'model.pkl'
    saveMyModel(classifier_pipeline,filename)



if __name__ == '__main__' :
    #SingleColumnSelector.__module__ = '__main__'
    train()

import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from scipy.sparse import hstack
import streamlit as st
from src.text_cleaner import clean_text_pipeline


@st.cache_resource
def load_nlp():
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('russian'))
    stop_words.difference_update({'не', 'ни', 'нет'})
    stemmer = SnowballStemmer("russian")
    return stop_words, stemmer


@st.cache_resource
def load_model_artifacts():
    return joblib.load('toxic_classifier.joblib')


def get_toxicity_prob(text):
    stop_words, stemmer = load_nlp()
    artifacts = load_model_artifacts()

    model = artifacts['model']
    word_vec = artifacts['word_vectorizer']
    char_vec = artifacts['char_vectorizer']

    cleaned_text = clean_text_pipeline(text, stemmer, stop_words)

    vec_word = word_vec.transform([cleaned_text])
    vec_char = char_vec.transform([cleaned_text])
    vec_msg = hstack([vec_word, vec_char])

    return model.predict_proba(vec_msg)[0][1]
import streamlit as st
from st_keyup import st_keyup
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from scipy.sparse import hstack
import emoji

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Toxic Detector", page_icon="🛡️", layout="centered")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# --- ЗАГРУЗКА NLTK И МОДЕЛИ ---
@st.cache_resource
def load_nlp():
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('russian'))
    stop_words.difference_update({'не', 'ни', 'нет'})
    stemmer = SnowballStemmer("russian")
    return stop_words, stemmer


@st.cache_resource
def load_model():
    return joblib.load('toxic_classifier.joblib')

stop_words, stemmer = load_nlp()

try:
    artifacts = load_model()
    model = artifacts['model']
    word_vec = artifacts['word_vectorizer']
    char_vec = artifacts['char_vectorizer']
    threshold = artifacts['threshold']
except Exception as e:
    st.error(f"Ошибка загрузки модели! Проверь версии библиотек. Текст ошибки: {e}")
    st.stop()

# --- АБСОЛЮТНО НЕПРОБИВАЕМАЯ ОЧИСТКА ТЕКСТА ---
HOMOGLYPHS = str.maketrans({
    'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н', 'k': 'к',
    'm': 'м', 'o': 'о', 'p': 'р', 't': 'т', 'x': 'х', 'y': 'у'
})


def remove_spacing(text):
    words = text.split()
    res, temp = [], []
    for w in words:
        if len(w) == 1 and w.isalpha():
            temp.append(w)
        else:
            if len(temp) >= 3:
                res.append("".join(temp))
            else:
                res.extend(temp)
            temp = []
            res.append(w)
    if len(temp) >= 3:
        res.append("".join(temp))
    else:
        res.extend(temp)
    return " ".join(res)


def predict_toxicity(text):
    text = text.lower()
    text = emoji.demojize(text, language='ru', delimiters=(" ", " "))
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = text.translate(HOMOGLYPHS)

    leet_dict = {'4': 'ч', '3': 'з', '0': 'о', '6': 'б', '9': 'я', '1': 'и'}
    for digit, letter in leet_dict.items():
        text = re.sub(rf'(?<=[а-яёa-z]){digit}+|{digit}+(?=[а-яёa-z])', letter, text)
    text = re.sub(r'@+', 'а', text)

    text = re.sub(r'(?<=[а-яёa-z])[^а-яёa-z0-9\s!?]+(?=[а-яёa-z])', '', text)
    text = re.sub(r'[^а-яёa-z0-9!?]', ' ', text)
    text = remove_spacing(text)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    text = re.sub(r'\s+', ' ', text).strip()

    words = text.split()
    cleaned_words = [stemmer.stem(word) for word in words if word not in stop_words]
    cleaned_text = ' '.join(cleaned_words)

    vec_word = word_vec.transform([cleaned_text])
    vec_char = char_vec.transform([cleaned_text])
    vec_msg = hstack([vec_word, vec_char])
    return model.predict_proba(vec_msg)[0][1]


# --- ИНТЕРФЕЙС ---
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Анализатор токсичности чата 💬</h1>",
            unsafe_allow_html=True)

col1, col2 = st.columns([2, 1.2])

with col1:
    user_text = st_keyup("Введите сообщение:", key="text_input", debounce=100)

with col2:
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    if user_text and len(user_text.replace(" ", "")) >= 3:
        prob = predict_toxicity(user_text)
        prob_percent = int(prob * 100)

        # ТРЕХУРОВНЕВАЯ СИСТЕМА ЛОГИКИ
        if prob_percent >= 85:
            status_text = f"<span style='color: #FF4B4B;'>Авто-бан 🤬</span>"
        elif prob_percent >= 50:
            status_text = f"<span style='color: #FFA500;'>Есть подозрения, на проверку ⚠️</span>"
        else:
            status_text = f"<span style='color: #00FF00;'>Нет признаков токсичности ✅</span>"

        grad_end = int(10000 / prob_percent) if prob_percent > 0 else 100

        html_bar = f"""
        <div style="font-size: 18px; margin-bottom: 5px; font-weight: bold;">
            Вердикт: {status_text} ({prob_percent}%)
        </div>
        <div style="background-color: #2b2b2b; border-radius: 10px; width: 100%; height: 30px; box-shadow: inset 0 1px 3px rgba(0,0,0,.5);">
            <div style="background: linear-gradient(to right, #00008B 0%, #FF0000 {grad_end}%); 
                        width: {prob_percent}%; 
                        height: 100%; 
                        border-radius: 10px;
                        transition: width 0.3s ease-in-out, background 0.3s ease-in-out;">
            </div>
        </div>
        """
        st.markdown(html_bar, unsafe_allow_html=True)
    else:
        placeholder_bar = """
        <div style="font-size: 18px; margin-bottom: 5px; color: gray;">Ожидание текста...</div>
        <div style="background-color: #2b2b2b; border-radius: 10px; width: 100%; height: 30px; box-shadow: inset 0 1px 3px rgba(0,0,0,.5);">
            <div style="width: 0%; height: 100%;"></div>
        </div>
        """
        st.markdown(placeholder_bar, unsafe_allow_html=True)
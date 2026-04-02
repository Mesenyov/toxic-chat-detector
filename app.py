import streamlit as st
from st_keyup import st_keyup
from src.model_handler import get_toxicity_prob

st.set_page_config(page_title="Toxic Detector", page_icon="🛡️", layout="centered")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Анализатор токсичности чата 💬</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1.2])

with col1:
    user_text = st_keyup("Введите сообщение:", key="text_input", debounce=100)

with col2:
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    if user_text and len(user_text.replace(" ", "")) >= 3:
        try:
            prob = get_toxicity_prob(user_text)
            prob_percent = int(prob * 100)

            if prob_percent >= 85:
                status_text = "<span style='color: #FF4B4B;'>Авто-бан 🤬</span>"
            elif prob_percent >= 50:
                status_text = "<span style='color: #FFA500;'>На проверку ⚠️</span>"
            else:
                status_text = "<span style='color: #00FF00;'>Чисто ✅</span>"

            grad_end = int(10000 / prob_percent) if prob_percent > 0 else 100

            html_bar = f"""
            <div style="font-size: 18px; margin-bottom: 5px; font-weight: bold;">
                Вердикт: {status_text} ({prob_percent}%)
            </div>
            <div style="background-color: #2b2b2b; border-radius: 10px; width: 100%; height: 30px;">
                <div style="background: linear-gradient(to right, #00008B 0%, #FF0000 {grad_end}%); 
                            width: {prob_percent}%; height: 100%; border-radius: 10px;">
                </div>
            </div>
            """
            st.markdown(html_bar, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ошибка обработки: {e}")
    else:
        placeholder_bar = """
        <div style="font-size: 18px; margin-bottom: 5px; color: gray;">Ожидание текста...</div>
        <div style="background-color: #2b2b2b; border-radius: 10px; width: 100%; height: 30px;">
            <div style="width: 0%; height: 100%;"></div>
        </div>
        """
        st.markdown(placeholder_bar, unsafe_allow_html=True)
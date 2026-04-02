import re
import emoji

HOMOGLYPHS = str.maketrans({
    'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н', 'k': 'к',
    'm': 'м', 'o': 'о', 'p': 'р', 't': 'т', 'x': 'х', 'y': 'у'
})

def remove_spacing(text):
    words = text.split()
    res, temp = [],[]
    for w in words:
        if len(w) == 1 and w.isalpha():
            temp.append(w)
        else:
            if len(temp) >= 3:
                res.append("".join(temp))
            else:
                res.extend(temp)
            temp =[]
            res.append(w)
    if len(temp) >= 3:
        res.append("".join(temp))
    else:
        res.extend(temp)
    return " ".join(res)

def clean_text_pipeline(text, stemmer, stop_words):
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
    cleaned_words =[stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(cleaned_words)
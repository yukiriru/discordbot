import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from konlpy.tag import Okt

okt = Okt()

def tokenize_text(text, okt, stopwords):
    if isinstance(text, list):
        ttext = ' '.join(ttext)

    word_tokens = okt.morphs(ttext)

    ttext = [word for word in word_tokens if not word in stopwords]

    answer_dict = {
        '시간': ':clock8: 현재 시간은 {}입니다.'.format(get_time()),

    }

    if not ttext:
        return "빈 문자열입니다."

    for key in answer_dict.keys():
        if any(word in ttext for word in key.split()):
            return answer_dict[key]
    
    return "해당하는 답변이 없습니다."

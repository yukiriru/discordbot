from konlpy.tag import Okt

okt = Okt()

def save_nouns(text):

    nouns_list = okt.nouns(text)

    with open('stopwords.txt', 'r', encoding='utf-8') as file:
        stopwords = file.readlines()
    stopwords = [word.strip() for word in stopwords]
    nouns_list = [word for word in nouns_list if word not in stopwords]
    with open('save_text.txt', 'a', encoding='utf-8') as file:
        for noun in nouns_list:
            file.write(noun + '\n')

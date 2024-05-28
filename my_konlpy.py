from konlpy.tag import Okt

okt = Okt()

def save_nouns(text):
    nouns_list = okt.nouns(text)
    with open('save_text.txt', 'a', encoding='utf-8') as file:
        for noun in nouns_list:
            file.write(noun + '\n')

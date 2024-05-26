import discord
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from konlpy.tag import Okt



okt = Okt()

with open('stopwords.txt', 'r', encoding='utf-8') as file:
    stopwords = set([word.strip() for word in file.readlines()])

class MyClient(discord.Client):
    async def on_ready(self): #실행시 봇 실행
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))


    async def on_message(self, message): #수신될 떄
        if message.author == self.user: #봇이 말한 것은 예외
            return

        if message.content == 'ping': #메세지 내용이 ping이면 pong 답장을 보낸다.
            await message.channel.send('pong {0.author.mention}'.format(message))
        else:
            answer = self.get_answer(message.content) #아니면 get_answer을 실행한다.
            await message.channel.send(answer)

    def get_day_of_week(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        date = datetime.today().strftime("%Y년 %m월 %d일")
        result = '{}({})'.format(date, weekday)
        return result

    def get_time(self):
        return datetime.today().strftime("%H시 %M분 %S초")

    def get_answer(self, text):
        ttext = word_tokenize(text) #보낸 텍스트

        if isinstance(ttext, list):
            ttext = ' '.join(ttext)

        word_tokens = okt.morphs(ttext)

        ttext = [word for word in word_tokens if not word in stopwords]

        answer_dict = {
            '시간': ':clock8: 현재 시간은 {}입니다.'.format(self.get_time()),
        }


        if not ttext:
            return "빈 문자열입니다."

        for key in answer_dict.keys():
            if any(word in ttext for word in key.split()):
                return ' '.join(ttext) + answer_dict[key]
        return ' '.join(ttext)





intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)



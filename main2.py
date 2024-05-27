import discord
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import openai
from openai import OpenAI

from konlpy.tag import Okt

TOKEN = ''
'''
okt = Okt()

with open('stopwords.txt', 'r', encoding='utf-8') as file:
    stopwords = set([word.strip() for word in file.readlines()])
    '''

class MyClient(discord.Client):
    async def on_ready(self): #실행시
        print('디스코드 봇 로그인 완료')
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))


    async def on_message(self, message): #수신될 떄
        content = message.content
        author = message.author
        channel = message.channel
        if author == self.user: #봇이 말한 것은 예외
            return

        if content == 'ping': #메세지 내용이 ping이면 pong 답장을 보낸다.
            await channel.send('pong {0.author.mention}'.format(message))
        else:
            answer = self.get_answer(content) #아니면 get_answer을 실행한다.
            await channel.send(answer)

    def get_day_of_week(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        date = datetime.today().strftime("%Y년 %m월 %d일")
        result = '{}({})'.format(date, weekday)
        return result

    def get_time(self):
        return datetime.today().strftime("%H시 %M분 %S초")

    def chat_with_gpt(self,prompt):
        # 중요!!: 발급받은 API Key를 입력해야 함
        client = OpenAI(api_key="")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        message = response.choices[0].message.content.strip()
        return message
    def get_answer(self, text):

        answer_dict = {
            '시간': ':clock8: 현재 시간은 {}입니다.'.format(self.get_time()),
        }

        if not text:
            return "빈 문자열입니다."

        for key in answer_dict.keys():
            if key.find(text) != -1:
                return  answer_dict[key]
        return self.chat_with_gpt(text)





intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)

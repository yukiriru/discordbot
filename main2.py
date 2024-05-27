# my_discord_bot.py

import discord
from datetime import datetime
import random
import requests
import nltk
from nltk.tokenize import word_tokenize
from konlpy.tag import Okt
import openai
from openai import OpenAI

# Initialize NLP tools
nltk.download('punkt')
okt = Okt()

# Read stopwords from file
with open('stopwords.txt', 'r', encoding='utf-8') as file:
    stopwords = set([word.strip() for word in file.readlines()])

# Define the Discord bot client class
class MyClient(discord.Client):
    async def on_ready(self):
        print('디스코드 봇 로그인 완료')
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content
        channel = message.channel

        if content == 'ping':
            await channel.send('pong {0.author.mention}'.format(message))
        elif content == 'flip':
            outcome = '앞면' if random.choice([True, False]) else '뒷면'
            await channel.send('동전 뒤집기 결과: {}'.format(outcome))
        elif content == 'help':
            commands = """
            사용 가능한 명령어:
            1. ping - 'pong'으로 응답
            2. flip - 동전을 뒤집고 결과를 보여줌
            3. 시간 - 현재 시간을 보여줌
            4. 날씨 <도시명> - 지정된 도시의 날씨를 보여줌
            """
            await channel.send(commands)
        elif content.startswith('날씨 '):
            city = content.split(' ', 1)[1]
            weather = self.get_weather(city)
            await channel.send(weather)
        else:
            answer = self.get_answer(content)
            await channel.send(answer)

    def get_day_of_week(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        date = datetime.today().strftime("%Y년 %m월 %d일")
        result = '{}({})'.format(date, weekday)
        return result

    def get_time(self):
        return datetime.today().strftime("%H시 %M분 %S초")

    def get_answer(self, text):
        ttext = word_tokenize(text)

        if isinstance(ttext, list):
            ttext = ' '.join(ttext)

        word_tokens = okt.morphs(ttext)
        ttext = [word for word in word_tokens if word not in stopwords]

        answer_dict = {
            '시간': ':clock8: 현재 시간은 {}입니다.'.format(self.get_time()),
        }

        if not ttext:
            return "빈 문자열입니다."

        for key in answer_dict.keys():
            if any(word in ttext for word in key.split()):
                return answer_dict[key]
        return self.chat_with_gpt(text)

    def chat_with_gpt(self, prompt):
        # 중요!!: 발급받은 API Key를 입력해야 함
        client = OpenAI(api_key="your openai api")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        message = response.choices[0].message.content.strip()
        return message

    def get_weather(self, city):
        lat, lon = 37.5665, 126.9780  # 서울의 위도와 경도
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True
        }
        response = requests.get('https://api.open-meteo.com/v1/forecast', params=params)
        if response.status_code == 200:
            data = response.json()
            current_weather = data['current_weather']
            weather_desc = current_weather['weathercode']
            temp = current_weather['temperature']
            windspeed = current_weather['windspeed']
            weather_info = f"{city}의 현재 날씨는 코드 {weather_desc}입니다.\n온도: {temp}°C, 풍속: {windspeed} m/s"
            return weather_info
        else:
            error_message = response.json().get('error', '알 수 없는 오류')
            return f"날씨 정보를 가져올 수 없습니다: {response.status_code} - {error_message}"

# Initialize and run the bot
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
TOKEN = 'yourtoken'
client.run(TOKEN)

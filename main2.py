import discord
from datetime import datetime
import random
import requests
import nltk
from nltk.tokenize import word_tokenize
import openai
from openai import OpenAI

class MyClient(discord.Client):
    async def on_ready(self):
        print('디스코드 봇 로그인 완료')
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

    async def on_message(self, message):
        content = message.content
        channel = message.channel
        if message.author == self.user:
            return
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
        answer_dict = {
            '시간': ':clock8: 현재 시간은 {}입니다.'.format(self.get_time()),
        }

        if not text:
            return "빈 문자열입니다."

        for key in answer_dict.keys():
            if key.find(text) != -1:
                return  answer_dict[key]
        return self.chat_with_gpt(text)


    def chat_with_gpt(self, prompt):
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

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)

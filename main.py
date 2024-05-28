

import discord
from datetime import datetime
import random
import requests
import openai
from openai import OpenAI
import asyncio


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
            5. joke - 무작위 농담을 보여줌
            6. quote - 무작위 명언을 보여줌
            7. remind <시간(분)> <메시지> - 지정된 시간 후에 메시지를 보냄
            8. 뉴스 <키워드> - 지정된 키워드에 대한 최신 뉴스를 보여줌
            """
            await channel.send(commands)
        elif content == 'joke':
            joke = self.generate_joke()
            await channel.send(joke)
        elif content == 'quote':
            quote = self.generate_quote()
            await channel.send(quote)
        elif content.startswith('날씨 '):
            city = content.split(' ', 1)[1]
            weather = self.get_weather(city)
            await channel.send(weather)
        elif content.startswith('remind '):
            try:
                parts = content.split(' ', 2)
                delay = int(parts[1])
                reminder_message = parts[2]
                await channel.send(f"{delay}분 후에 알림을 설정했습니다: {reminder_message}")
                await asyncio.sleep(delay * 60)
                await channel.send(f"알림: {reminder_message} - {message.author.mention}")
            except (IndexError, ValueError):
                await channel.send("잘못된 형식입니다. 사용 예시: remind 10 잠에서 깨어나세요!")
        elif content.startswith('뉴스 '):
            keyword = content.split(' ', 1)[1]
            news = self.get_news(keyword)
            await channel.send(news)
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
                return answer_dict[key]
        return self.chat_with_gpt(text)

    def chat_with_gpt(self, prompt):
        client = OpenAI(api_key="your api")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        message = response.choices[0].message.content.strip()
        return message

    def generate_joke(self):
        prompt = "농담 하나 해줘."
        return self.chat_with_gpt(prompt)

    def generate_quote(self):
        prompt = "영감을 주는 명언 하나 해줘."
        return self.chat_with_gpt(prompt)

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

    def get_news(self, keyword):
        client = OpenAI(api_key="your api")
        prompt = f"{keyword}에 대한 최신 뉴스를 제공해줘."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        message = response.choices[0].message.content.strip()
        return message

# 봇 초기화 및 실행
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
TOKEN = 'your token'
client.run(TOKEN)

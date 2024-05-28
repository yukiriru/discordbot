import discord
from datetime import datetime
import random
import requests
import openai
from discord.ext.commands import bot
from geopy import Nominatim
from openai import OpenAI
import asyncio
from my_konlpy import save_nouns

TOKEN = ''



class MyClient(discord.Client):
    async def on_ready(self):
        print('디스코드 봇 로그인 완료')
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

    async def on_message(self, message):
        content = message.content
        channel = message.channel

        if message.author == self.user:
            return

        elif content == 'help':
            commands = """
           사용 가능한 명령어:
            0.'help' - 명령어를 알립니다.
            1. ping - 'pong'으로 응답합니다.
            2. flip - 동전을 던지고 결과를 보여줍니다.
            3. 요일 / 날짜 / 시간 - 현재 요일 / 날짜 /시간을 보여줍니다.
            4. 날씨 <도시명> - 지정된 도시의 날씨를 보여줍니다.
            5. joke - 무작위 농담을 보여줍니다.
            6. quote - 무작위 명언을 보여줍니다.
            7. remind <시간(분)> <메시지> - 지정된 시간 후에 메시지를 보냅니다.
            8. 뉴스 <키워드> - 지정된 키워드에 대한 최신 뉴스를 보여줍니다.
            9. 이외의 명령어는 챗GPT가 대신 답변해드립니다. (채팅 메세지 중에서 명사만 가져와서 text 파일에 저장합니다.)
            """
            await channel.send(commands)
        elif content == 'ping':
            await channel.send('pong{0.author.mention}'.format(message))
        elif content == 'flip':
            outcome = '앞면' if random.choice([True, False]) else '뒷면'
            await channel.send('동전 뒤집기 결과: {}'.format(outcome))
        elif content.startswith('날씨 '):
            if ' ' in content:
                city = content.split(' ', 1)[1]
            else:
                city = '서울'
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
    def get_answer(self, text):
        dict = {
            '시간': ':clock8: 현재 시간은 {}입니다.'.format(self.get_time()),
            '요일': '오늘은 {}입니다.'.format(self.get_day_of_week()),
            '날짜': '오늘은 {}입니다.'.format(self.get_date()),
            'joke': '{}'.format(self.generate_joke()),
            'quote': '{}'.format(self.generate_quote()),

        }

        if not text:
            return "빈 문자열입니다."

        for key in dict.keys():
            if key.find(text) != -1:
                return dict[key]
        return "챗GPT가 대신 답변해드립니다 \n"+self.chat_with_gpt(text)

    def get_day_of_week(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        return weekday

    def get_date(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        return datetime.now().strftime("%Y년 %m월 %d일 ") + weekday

    def get_time(self):
        return datetime.today().strftime("%H시 %M분 %S초")

    def chat_with_gpt(self, prompt):
        client = OpenAI(api_key="")
        save_nouns(prompt)
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



    def get_lat_lon(self, city):
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(city)

        if location is None:
            return None, None  # 위치를 찾을 수 없을 경우 None 반환

        return location.latitude, location.longitude

    def get_weather(self, city):
        lat, lon = self.get_lat_lon(city)

        if lat is None or lon is None:
            return f"{city}의 위치를 찾을 수 없습니다."

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
        client = OpenAI(api_key="")
        prompt = f"{keyword}에 대한 최신 뉴스를 제공해줘."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        message = response.choices[0].message.content.strip()
        return message


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)

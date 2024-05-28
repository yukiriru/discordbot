import discord
from discord.ext import commands
import aiosqlite

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 데이터베이스 초기화
async def init_db():
    async with aiosqlite.connect('leveling.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                xp INTEGER,
                level INTEGER
            )
        ''')
        await db.commit()

# 봇이 준비되었을 때 호출되는 이벤트
@bot.event
async def on_ready():
    await init_db()
    print(f'We have logged in as {bot.user}')

# 메시지가 수신되었을 때 호출되는 이벤트
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    async with aiosqlite.connect('leveling.db') as db:
        cursor = await db.execute('SELECT xp, level FROM users WHERE user_id = ?', (message.author.id,))
        result = await cursor.fetchone()

        if result:
            xp, level = result
            xp += 10
            new_level = int(xp ** (1 / 4))

            if new_level > level:
                await message.channel.send(f'Congratulations {message.author.mention}, you reached level {new_level}!')
                await db.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?', (xp, new_level, message.author.id))
            else:
                await db.execute('UPDATE users SET xp = ? WHERE user_id = ?', (xp, message.author.id))
        else:
            await db.execute('INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)', (message.author.id, 10, 1))

        await db.commit()

    await bot.process_commands(message)

# 레벨 확인 명령어
@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    async with aiosqlite.connect('leveling.db') as db:
        cursor = await db.execute('SELECT xp, level FROM users WHERE user_id = ?', (member.id,))
        result = await cursor.fetchone()

    if result:
        xp, level = result
        await ctx.send(f'{member.mention} is at level {level} with {xp} XP.')
    else:
        await ctx.send(f'{member.mention} has no levels yet.')

# 봇 토큰을 사용하여 봇을 실행
bot.run('YOUR_DISCORD_BOT_TOKEN')

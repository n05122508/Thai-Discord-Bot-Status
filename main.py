import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

CHANNELS_FILE = 'channels_config.json'

def load_channels():
    """โหลดการตั้งค่าช่อง"""
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'channels': {},
        'report_settings': {}
    }

def save_channels(data):
    """บันทึกการตั้งค่าช่อง"""
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

channels_data = load_channels()

try:
    from commands import weather, football, lottery, currency, oil, school, jokes, channel_manager
    from utils import embeds
except ImportError as e:
    print(f'Import error: {e}')

async def load_cogs():
    """โหลด Cogs ทั้งหมด"""
    try:
        await bot.add_cog(weather.WeatherCog(bot))
        await bot.add_cog(football.FootballCog(bot))
        await bot.add_cog(lottery.LotteryCog(bot))
        await bot.add_cog(currency.CurrencyCog(bot))
        await bot.add_cog(oil.OilCog(bot))
        await bot.add_cog(school.SchoolCog(bot))
        await bot.add_cog(jokes.JokesCog(bot))
        await bot.add_cog(channel_manager.ChannelManagerCog(bot))
        print('✅ โหลด Cogs สำเร็จ')
    except Exception as e:
        print(f'❌ ข้อผิดพลาดในการโหลด Cogs: {e}')

@bot.event
async def on_ready():
    print(f'✅ บอทเข้าสู่ระบบเป็น {bot.user}')
    print(f'🚀 บอทพร้อมส่งรายงาน!')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="สถานะข้อมูลไทยอัปเดต ทุก 5 นาที"
        )
    )
    
    if not report_task.is_running():
        report_task.start()

@tasks.loop(minutes=5)
async def report_task():
    """ส่งรายงานอัตโนมัติทุก 5 นาที"""
    try:
        global channels_data
        channels_data = load_channels()
        
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        print(f'📊 เริ่มส่งรายงานเวลา {now}')
        
        # ส่งรายงานไปยังทุกช่อง
        for channel_name, channel_info in channels_data.get('channels', {}).items():
            if not channel_info.get('enabled', False):
                continue
            
            channel_id = channel_info.get('id')
            if not channel_id:
                continue
            
            channel = bot.get_channel(channel_id)
            if not channel:
                print(f'❌ ไม่พบช่อง {channel_name} (ID: {channel_id})')
                continue
            
            reports = channel_info.get('reports', [])
            
            for report_type in reports:
                try:
                    if report_type == 'weather':
                        weather_cog = bot.get_cog('WeatherCog')
                        if weather_cog:
                            embed = await weather_cog.get_bangkok_weather()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'jokes':
                        jokes_cog = bot.get_cog('JokesCog')
                        if jokes_cog:
                            embed = await jokes_cog.get_random_joke()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'oil':
                        oil_cog = bot.get_cog('OilCog')
                        if oil_cog:
                            embed = await oil_cog.get_oil_prices()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'lottery':
                        lottery_cog = bot.get_cog('LotteryCog')
                        if lottery_cog:
                            embed = await lottery_cog.get_lottery()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'currency':
                        currency_cog = bot.get_cog('CurrencyCog')
                        if currency_cog:
                            embed = await currency_cog.get_currency_rates()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'football':
                        football_cog = bot.get_cog('FootballCog')
                        if football_cog:
                            embed = await football_cog.get_football_standings()
                            await channel.send(embed=embed)
                    
                    elif report_type == 'school':
                        school_cog = bot.get_cog('SchoolCog')
                        if school_cog:
                            embed = await school_cog.get_school_info()
                            await channel.send(embed=embed)
                
                except Exception as e:
                    print(f'❌ ข้อผิดพลาด {report_type}: {e}')
        
        print(f'✅ ส่งรายงานเสร็จเวลา {now}')
        
    except Exception as e:
        print(f'❌ ข้อผิดพลาดในการส่งรายงาน: {e}')

@bot.event
async def on_command_error(ctx, error):
    print(f'❌ ข้อผิดพลาด: {error}')
    await ctx.send(f'❌ เกิดข้อผิดพลาด: {str(error)[:100]}')

async def main():
    async with bot:
        await load_cogs()
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print('❌ ไม่พบ DISCORD_BOT_TOKEN ในตัวแปรสภาพแวดล้อม')
            return
        await bot.start(token)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n👋 บอทหยุดการทำงาน')

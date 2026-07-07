import discord
from discord.ext import commands
import json
import os

CHANNELS_FILE = 'channels_config.json'

def load_channels():
    """โหลดการตั้งค่าช่อง"""
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'channels': {}, 'report_settings': {}}

def save_channels(data):
    """บันทึกการตั้งค่าช่อง"""
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class ChannelManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.report_types = {
            'สภาพอากาศ': 'weather',
            'ตลกขัน': 'jokes',
            'ราคาน้ำมัน': 'oil',
            'หวย': 'lottery',
            'อัตราแลก': 'currency',
            'ฟุตบอล': 'football',
            'ปิดเทอม': 'school'
        }
    
    @commands.command(name='สร้างช่องรายงาน', description='สร้างช่องรายงานใหม่')
    async def create_channel(self, ctx, channel_type: str):
        """สร้างช่องรายงานใหม่"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('❌ ต้องเป็นผู้ดูแลเท่านั้น')
            return
        
        # แปลงชื่อเป็นประเภท
        report_type = self.report_types.get(channel_type)
        if not report_type:
            types = ', '.join(self.report_types.keys())
            await ctx.send(f'❌ ประเภทไม่ถูกต้อง\n📋 ประเภทที่มี: {types}')
            return
        
        try:
            # สร้างช่องใหม่
            channel_name = f'📢-{channel_type}'
            new_channel = await ctx.guild.create_text_channel(channel_name)
            
            # บันทึกลงไฟล์
            data = load_channels()
            data['channels'][channel_name] = {
                'id': new_channel.id,
                'name': channel_type,
                'enabled': True,
                'reports': [report_type]
            }
            save_channels(data)
            
            embed = discord.Embed(
                title='✅ สร้างช่องสำเร็จ',
                description=f'ช่อง {new_channel.mention} ถูกสร้างแล้ว',
                color=discord.Color.green()
            )
            embed.add_field(name='ประเภท', value=channel_type, inline=False)
            embed.add_field(name='Channel ID', value=new_channel.id, inline=False)
            
            await ctx.send(embed=embed)
            await new_channel.send(f'🎯 ช่องนี้สำหรับรายงาน **{channel_type}**')
            
        except Exception as e:
            await ctx.send(f'❌ ข้อผิดพลาด: {str(e)}')
    
    @commands.command(name='ลบช่อง', description='ลบช่องรายงาน')
    async def delete_channel(self, ctx, channel_name: str = None):
        """ลบช่องรายงาน"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('❌ ต้องเป็นผู้ดูแลเท่านั้น')
            return
        
        if not channel_name:
            await ctx.send('❌ ระบุชื่อช่องให้ด้วย\n💡 ตัวอย่าง: `/ลบช่อง 📢-ตลกขัน`')
            return
        
        try:
            data = load_channels()
            
            # ค้นหาช่อง
            found = False
            for ch_name, ch_info in data['channels'].items():
                if ch_name == channel_name or str(ch_info.get('id')) == channel_name:
                    channel_id = ch_info['id']
                    channel = self.bot.get_channel(channel_id)
                    
                    if channel:
                        await channel.delete()
                    
                    del data['channels'][ch_name]
                    save_channels(data)
                    found = True
                    
                    embed = discord.Embed(
                        title='✅ ลบช่องสำเร็จ',
                        description=f'ลบช่อง **{ch_name}** แล้ว',
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=embed)
                    break
            
            if not found:
                await ctx.send(f'❌ ไม่พบช่อง **{channel_name}**')
        
        except Exception as e:
            await ctx.send(f'❌ ข้อผิดพลาด: {str(e)}')
    
    @commands.command(name='แสดงช่องทั้งหมด', description='แสดงรายชื่อช่องทั้งหมด')
    async def list_channels(self, ctx):
        """แสดงรายชื่อช่องรายงานทั้งหมด"""
        data = load_channels()
        channels = data.get('channels', {})
        
        if not channels:
            await ctx.send('❌ ยังไม่มีช่องรายงานใดๆ')
            return
        
        embed = discord.Embed(
            title='📋 รายชื่อช่องทั้งหมด',
            color=discord.Color.blue()
        )
        
        for ch_name, ch_info in channels.items():
            status = '✅ เปิด' if ch_info.get('enabled') else '❌ ปิด'
            reports = ', '.join(ch_info.get('reports', []))
            embed.add_field(
                name=f'{ch_name} {status}',
                value=f'📊 รายงาน: {reports}\n🔢 ID: {ch_info.get("id")}',
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='เปิดรายงาน', description='เปิดการส่งรายงาน')
    async def enable_report(self, ctx, channel_type: str):
        """เปิดการส่งรายงาน"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('❌ ต้องเป็นผู้ดูแลเท่านั้น')
            return
        
        report_type = self.report_types.get(channel_type)
        if not report_type:
            types = ', '.join(self.report_types.keys())
            await ctx.send(f'❌ ประเภทไม่ถูกต้อง\n📋 ประเภทที่มี: {types}')
            return
        
        try:
            data = load_channels()
            data['report_settings'][report_type] = {'enabled': True}
            save_channels(data)
            
            embed = discord.Embed(
                title='✅ เปิดรายงานสำเร็จ',
                description=f'เปิดการส่งรายงาน **{channel_type}** แล้ว',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f'❌ ข้อผิดพลาด: {str(e)}')
    
    @commands.command(name='ปิดรายงาน', description='ปิดการส่งรายงาน')
    async def disable_report(self, ctx, channel_type: str):
        """ปิดการส่งรายงาน"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('❌ ต้องเป็นผู้ดูแลเท่านั้น')
            return
        
        report_type = self.report_types.get(channel_type)
        if not report_type:
            types = ', '.join(self.report_types.keys())
            await ctx.send(f'❌ ประเภทไม่ถูกต้อง\n📋 ประเภทที่มี: {types}')
            return
        
        try:
            data = load_channels()
            data['report_settings'][report_type] = {'enabled': False}
            save_channels(data)
            
            embed = discord.Embed(
                title='✅ ปิดรายงานสำเร็จ',
                description=f'ปิดการส่งรายงาน **{channel_type}** แล้ว',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f'❌ ข้อผิดพลาด: {str(e)}')
    
    @commands.command(name='ช่วยเหลือ', description='แสดงคำสั่งทั้งหมด')
    async def help_command(self, ctx):
        """แสดงคำสั่งจัดการช่องทั้งหมด"""
        embed = discord.Embed(
            title='📚 คำสั่งจัดการช่อง',
            color=discord.Color.purple()
        )
        
        commands_info = [
            ('สร้างช่องรายงาน [ประเภท]', 'สร้างช่องรายงานใหม่'),
            ('ลบช่อง [ชื่อช่อง]', 'ลบช่องรายงาน'),
            ('แสดงช่องทั้งหมด', 'ดูรายชื่อช่องทั้งหมด'),
            ('เปิดรายงาน [ประเภท]', 'เปิดการส่งรายงาน'),
            ('ปิดรายงาน [ประเภท]', 'ปิดการส่งรายงาน'),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=f'/{cmd}', value=desc, inline=False)
        
        embed.add_field(
            name='📋 ประเภทรายงาน',
            value='สภาพอากาศ, ตลกขัน, ราคาน้ำมัน, หวย, อัตราแลก, ฟุตบอล, ปิดเทอม',
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChannelManagerCog(bot))

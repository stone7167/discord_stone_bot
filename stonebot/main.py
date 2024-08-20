import security, youtube_dl, json, requests
import asyncio, disnake, aiosqlite, platform, math
import os, random, time, string, datetime, psutil, koreanbots
from def_list import *
import yt_dlp as youtube_dl
from youtube_dl import YoutubeDL
from googletrans import Translator
from captcha.image import ImageCaptcha
from disnake.ext import commands, tasks
from datetime import datetime, timedelta
from disnake import FFmpegPCMAudio, PCMVolumeTransformer
from importlib.metadata import version, PackageNotFoundError

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
token = security.token
developer = int(security.developer_id)

# 시작 시간 기록
start_time = datetime.now()

embedcolor = 0xff00ff
embedwarning = 0xff9900
embedsuccess = 0x00ff00
embederrorcolor = 0xff0000
##################################################################################################
@bot.slash_command(name="ai질문", description="GPT에게 질문하거나 DALL·E에게 이미지생성을 요청합니다. [9/1이후 유료전환예정]")
async def ai_ask(ctx: disnake.CommandInteraction, choice: str = commands.Param(name="모델", choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "DALL·E"]), ask: str = commands.Param(name="질문")):
    #await membership(ctx)  # 회원 상태 확인
    # 이미 응답을 보냈는지 확인
    if ctx.response.is_done():  # 응답이 이미 완료된 경우
        return  # 더 이상 진행하지 않음
    await ctx.response.defer()  # 응답 준비 중임을 알림
    if choice == "DALL·E":
        # DALL·E 호출
        image_url = generate_image(ask)  # 이미지 생성 요청
        if "오류" in image_url:
            await ctx.send(image_url)  # 오류 메시지 전송
        else:
            # 임베드 응답 생성
            embed = disnake.Embed(title="이미지 생성", color=0x00ff00)
            embed.add_field(name="질문", value=f"{ask}", inline=False)
            embed.set_image(url=image_url)  # 생성된 이미지 추가
            embed.add_field(name="이미지 링크", value=f"[전체 크기 보기]({image_url})", inline=False)  # 클릭 가능한 링크 추가
            await ctx.send(embed=embed)
    else:
        # GPT API 호출
        answer = get_gpt_response(ask, choice)  # 선택한 모델을 전달합니다.
        
        # 임베드 응답 생성
        embed = disnake.Embed(title="GPT 응답", color=0x00ff00)
        embed.add_field(name="모델", value=f"{choice}", inline=False)
        embed.add_field(name="질문", value=f"{ask}", inline=False)
        embed.add_field(name="답변", value=f"{answer}")
        await ctx.send(embed=embed)

LANGUAGES = {
    'af': '아프리칸스 (afrikaans)',
    'sq': '알바니아어 (albanian)',
    'am': '암하라어 (amharic)',
    'ar': '아랍어 (arabic)',
    'hy': '아르메니아어 (armenian)',
    'az': '아제르바이잔어 (azerbaijani)',
    'eu': '바스크어 (basque)',
    'be': '벨라루스어 (belarusian)',
    'bn': '벵골어 (bengali)',
    'bs': '보스니아어 (bosnian)',
    'bg': '불가리아어 (bulgarian)',
    'ca': '카탈루냐어 (catalan)',
    'ceb': '세부아노어 (cebuano)',
    'ny': '치체와어 (chichewa)',
    'zh-cn': '중국어 (간체) (chinese (simplified))',
    'zh-tw': '중국어 (번체) (chinese (traditional))',
    'co': '코르시카어 (corsican)',
    'hr': '크로아티아어 (croatian)',
    'cs': '체코어 (czech)',
    'da': '덴마크어 (danish)',
    'nl': '네덜란드어 (dutch)',
    'en': '영어 (english)',
    'eo': '에스페란토 (esperanto)',
    'et': '에스토니아어 (estonian)',
    'tl': '필리핀어 (filipino)',
    'fi': '핀란드어 (finnish)',
    'fr': '프랑스어 (french)',
    'fy': '프리슬란드어 (frisian)',
    'gl': '갈리시아어 (galician)',
    'ka': '조지아어 (georgian)',
    'de': '독일어 (german)',
    'el': '그리스어 (greek)',
    'gu': '구자라트어 (gujarati)',
    'ht': '아이티 크리올어 (haitian creole)',
    'ha': '하우사어 (hausa)',
    'haw': '하와이어 (hawaiian)',
    'iw': '히브리어 (hebrew)',
    'he': '히브리어 (hebrew)',
    'hi': '힌디어 (hindi)',
    'hmn': '몽골어 (hmong)',
    'hu': '헝가리어 (hungarian)',
    'is': '아이슬란드어 (icelandic)',
    'ig': '이그보어 (igbo)',
    'id': '인도네시아어 (indonesian)',
    'ga': '아일랜드어 (irish)',
    'it': '이탈리아어 (italian)',
    'ja': '일본어 (japanese)',
    'jw': '자바어 (javanese)',
    'kn': '칸나다어 (kannada)',
    'kk': '카자흐어 (kazakh)',
    'km': '크메르어 (khmer)',
    'ko': '한국어 (korean)',
    'ku': '쿠르드어 (kurmanji)',
    'ky': '키르기스어 (kyrgyz)',
    'lo': '라오어 (lao)',
    'la': '라틴어 (latin)',
    'lv': '라트비아어 (latvian)',
    'lt': '리투아니아어 (lithuanian)',
    'lb': '룩셈부르크어 (luxembourgish)',
    'mk': '마케도니아어 (macedonian)',
    'mg': '말라가시어 (malagasy)',
    'ms': '말레이어 (malay)',
    'ml': '말라얄람어 (malayalam)',
    'mt': '몰타어 (maltese)',
    'mi': '마오리어 (maori)',
    'mr': '마라티어 (marathi)',
    'mn': '몽골어 (mongolian)',
    'my': '미얀마어 (burmese)',
    'ne': '네팔어 (nepali)',
    'no': '노르웨이어 (norwegian)',
    'or': '오디아어 (odia)',
    'ps': '파슈토어 (pashto)',
    'fa': '페르시아어 (persian)',
    'pl': '폴란드어 (polish)',
    'pt': '포르투갈어 (portuguese)',
    'pa': '펀자브어 (punjabi)',
    'ro': '루마니아어 (romanian)',
    'ru': '러시아어 (russian)',
    'sm': '사모아어 (samoan)',
    'gd': '스코틀랜드 게일어 (scots gaelic)',
    'sr': '세르비아어 (serbian)',
    'st': '세소토어 (sesotho)',
    'sn': '쇼나어 (shona)',
    'sd': '신디어 (sindhi)',
    'si': '신할라어 (sinhala)',
    'sk': '슬로바키아어 (slovak)',
    'sl': '슬로베니아어 (slovenian)',
    'so': '소말리어 (somali)',
    'es': '스페인어 (spanish)',
    'su': '순다어 (sundanese)',
    'sw': '스와힐리어 (swahili)',
    'sv': '스웨덴어 (swedish)',
    'tg': '타지크어 (tajik)',
    'ta': '타밀어 (tamil)',
    'te': '텔루구어 (telugu)',
    'th': '태국어 (thai)',
    'tr': '터키어 (turkish)',
    'uk': '우크라이나어 (ukrainian)',
    'ur': '우르두어 (urdu)',
    'ug': '위구르어 (uyghur)',
    'uz': '우즈벡어 (uzbek)',
    'vi': '베트남어 (vietnamese)',
    'cy': '웨일스어 (welsh)',
    'xh': '코사어 (xhosa)',
    'yi': '이디시어 (yiddish)',
    'yo': '요루바어 (yoruba)',
    'zu': '줄루어 (zulu)'
}

# LANGUAGES 딕셔너리를 언어 코드 목록으로 변환
LANGUAGE_CHOICES = list(LANGUAGES.keys())

@bot.slash_command(name="번역", description="텍스트를 선택한 언어로 번역합니다.")
async def translation(ctx, languages: str = commands.Param(name="언어"), text: str = commands.Param(name="내용")):
    translator = Translator()
    
    # 유효한 언어 코드인지 확인
    if languages not in LANGUAGE_CHOICES:
        embed = disnake.Embed(color=0xFF0000)
        embed.add_field(name="❌ 오류", value="유효한 언어 코드를 입력하세요.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    result = translator.translate(text, dest=languages)
    translated_text = result.text

    embed = disnake.Embed(title="번역 결과", color=0x00ff00)
    embed.add_field(name="언어", value=f"{LANGUAGES[languages]}")  # 선택한 언어 이름을 표시
    embed.add_field(name="원본 텍스트", value=text, inline=False)
    embed.add_field(name="번역된 텍스트", value=translated_text, inline=False)
    await ctx.send(embed=embed)

LANGUAGE_LIST = list(LANGUAGES.items())
PAGE_SIZE = 10  # 한 페이지에 표시할 언어 개수

@bot.slash_command(name="언어리스트", description="번역 명령어가 지원하는 언어목록을 표시합니다.")
async def language_list(interaction: disnake.ApplicationCommandInteraction):
    await send_language_page(interaction, 0)

async def send_language_page(interaction: disnake.ApplicationCommandInteraction, page: int):

    embed = disnake.Embed(title="언어 리스트", color=disnake.Color.blue())
    
    # 페이지에 맞는 언어 목록 추출
    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    languages_to_display = LANGUAGE_LIST[start_index:end_index]

    # 언어 목록을 추가
    for code, name in languages_to_display:
        embed.add_field(name=code, value=name, inline=False)

    # 현재 페이지와 총 페이지 수 추가
    total_pages = (len(LANGUAGE_LIST) + PAGE_SIZE - 1) // PAGE_SIZE  # 총 페이지 수 계산
    embed.set_footer(text=f"페이지 {page + 1}/{total_pages}")

    # 버튼 만들기
    view = disnake.ui.View(timeout=None)
    
    # 이전 페이지 버튼
    if page > 0:
        prev_button = disnake.ui.Button(label="이전 페이지", style=disnake.ButtonStyle.secondary)

        async def prev_button_callback(interaction: disnake.MessageInteraction):
            await send_language_page(interaction, page - 1)

        prev_button.callback = prev_button_callback
        view.add_item(prev_button)
    
    # 다음 페이지 버튼
    if end_index < len(LANGUAGE_LIST):
        next_button = disnake.ui.Button(label="다음 페이지", style=disnake.ButtonStyle.primary)

        async def next_button_callback(interaction: disnake.MessageInteraction):
            await send_language_page(interaction, page + 1)

        next_button.callback = next_button_callback
        view.add_item(next_button)

    await interaction.send(embed=embed, view=view)

@bot.slash_command(name='노래리스트', description='서버의 저장된 노래리스트를 보여줍니다.')
async def list_mp3(inter: disnake.ApplicationCommandInteraction):
    mp3_directory = './music/'  # MP3 파일이 저장된 디렉토리
    try:
        # 디렉토리에서 MP3 파일 목록 가져오기
        mp3_files = [f for f in os.listdir(mp3_directory) if f.endswith('.mp3')]
        
        embed = disnake.Embed(title="노래 목록", color=0x00ff00)  # 초록색 임베드

        if mp3_files:
            # 파일 리스트를 문자열로 변환
            file_list = '\n'.join(mp3_files)
            embed.description = f"```\n{file_list}\n```"
        else:
            embed.description = "노래가 존재하지 않습니다."

        await inter.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="오류", color=0xff0000)  # 빨간색 임베드
        embed.description = f"오류가 발생했습니다: {str(e)}"
        await inter.send(embed=embed, ephemeral=True)

# 유튜브 다운로드 설정
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# 음악 소스 클래스
class YTDLSource(disnake.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
    }

    def __init__(self, source, *, data):
        super().__init__(source)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        ydl = youtube_dl.YoutubeDL(cls.YTDL_OPTIONS)
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ydl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.slash_command(name='재생', description='유튜브 링크 또는 제목으로 음악을 재생합니다.')
async def play(ctx, url_or_music: str):
    if ctx.author.voice is None:
        return await ctx.send("음성 채널에 연결되어 있지 않습니다. 먼저 음성 채널에 들어가세요.")

    if ctx.guild.voice_client is None:
        await ctx.author.voice.channel.connect()

    embed = disnake.Embed(color=0x00ff00, description="음악을 재생하는 중입니다...")
    await ctx.send(embed=embed)

    file_path = f"./music/{url_or_music}.mp3"
    player = None

    # 파일 경로가 존재하지 않을 경우 검색어로 처리
    if os.path.isfile(file_path):
        player = disnake.FFmpegPCMAudio(file_path)
        embed.title = "음악 재생"
        embed.description = f'재생 중: {url_or_music}.mp3'
    else:
        # 유튜브 검색 처리
        try:
            player = await YTDLSource.from_url(f"ytsearch:{url_or_music}", loop=bot.loop, stream=True)
            embed.title = "음악 재생"
            embed.description = f'재생 중: {player.title}\n[링크]({player.url})'
        except Exception as e:
            embed.color = 0xff0000
            embed.title = "오류"
            embed.description = str(e)
            return await ctx.send(embed=embed)

    if ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.stop()

    ctx.guild.voice_client.play(player)

    buttons = [
        disnake.ui.Button(label="일시 정지", style=disnake.ButtonStyle.red, custom_id="pause"),
        disnake.ui.Button(label="다시 재생", style=disnake.ButtonStyle.green, custom_id="resume"),
        disnake.ui.Button(label="음량 증가", style=disnake.ButtonStyle.blurple, custom_id="volume_up"),
        disnake.ui.Button(label="음량 감소", style=disnake.ButtonStyle.blurple, custom_id="volume_down"),
        disnake.ui.Button(label="노래 변경", style=disnake.ButtonStyle.grey, custom_id="change_song")
    ]

    button_row = disnake.ui.View(timeout=None)
    for button in buttons:
        button_row.add_item(button)

    await ctx.send(embed=embed, view=button_row)

    # 각 버튼의 콜백 설정
    button_row.children[0].callback = lambda i: pause_callback(i, ctx)
    button_row.children[1].callback = lambda i: resume_callback(i, ctx)
    button_row.children[2].callback = lambda i: volume_change_callback(i, ctx, 0.1)
    button_row.children[3].callback = lambda i: volume_change_callback(i, ctx, -0.1)
    button_row.children[4].callback = lambda i: change_song_callback(i, ctx)

async def pause_callback(interaction, ctx):
    ctx.guild.voice_client.pause()
    await interaction.response.send_message("음악이 정지되었습니다.", ephemeral=True)

async def resume_callback(interaction, ctx):
    if ctx.guild.voice_client.is_paused():
        ctx.guild.voice_client.resume()
        await interaction.response.send_message("음악을 재개했습니다.", ephemeral=True)
    else:
        await interaction.response.send_message("현재 재생 중인 음악이 없습니다.", ephemeral=True)

async def volume_change_callback(interaction, ctx, change):
    if ctx.guild.voice_client.source:
        new_volume = min(max(ctx.guild.voice_client.source.volume + change, 0.0), 1.0)
        ctx.guild.voice_client.source.volume = new_volume
        await interaction.response.send_message(f"현재 음량: {new_volume:.1f}", ephemeral=True)

async def change_song_callback(interaction, ctx):
    await interaction.response.send_message("변경할 음악의 유튜브 링크 또는 mp3 파일 이름을 입력해주세요:", ephemeral=True)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        new_url_or_filename = msg.content
        new_file_path = f"./music/{new_url_or_filename}.mp3"

        if os.path.isfile(new_file_path):
            new_player = disnake.FFmpegPCMAudio(new_file_path)
        else:
            new_player = await YTDLSource.from_url(new_url_or_filename, loop=bot.loop, stream=True)

        ctx.guild.voice_client.stop()
        ctx.guild.voice_client.play(new_player)

        change_embed = disnake.Embed(color=0x00ff00, description=f"새로운 음악을 재생합니다: {new_url_or_filename}")
        await interaction.followup.send(embed=change_embed, ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("시간이 초과되었습니다. 다시 시도해주세요.", ephemeral=True)

@bot.slash_command(name='입장')
async def join(ctx):
    """음성 채널에 입장합니다."""
    embed = disnake.Embed(color=0x00ff00)
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.move_to(channel)
            embed.description = "음성 채널로 이동했습니다."
        else:
            await channel.connect()
            embed.description = "음성 채널에 연결되었습니다."
    else:
        embed.description = "음성 채널에 연결되어 있지 않습니다."
        embed.color = 0xff0000

    await ctx.send(embed=embed)

@bot.slash_command(name='볼륨')
async def volume(ctx, volume: int):
    """플레이어의 볼륨을 변경합니다."""
    embed = disnake.Embed(color=0x00ff00)
    if ctx.guild.voice_client is None:
        embed.description = "음성 채널에 연결되어 있지 않습니다."
        embed.color = 0xff0000
    else:
        ctx.guild.voice_client.source.volume = volume / 100
        embed.description = f"볼륨을 {volume}%로 변경했습니다."

    await ctx.send(embed=embed)

@bot.slash_command(name='정지')
async def stop(ctx):
    """음악을 중지하고 음성 채널에서 나갑니다."""
    embed = disnake.Embed(color=0x00ff00)
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        embed.description = "음악을 중지하고 음성 채널에서 나갔습니다."
    else:
        embed.description = "봇이 음성 채널에 연결되어 있지 않습니다."
        embed.color = 0xff0000

    await ctx.send(embed=embed)

@bot.slash_command(name='일시정지')
async def pause(ctx):
    """음악을 일시정지합니다."""
    embed = disnake.Embed(color=0x00ff00)
    if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
        embed.description = "음악이 이미 일시 정지 중이거나 재생 중이지 않습니다."
        embed.color = 0xff0000
    else:
        ctx.guild.voice_client.pause()
        embed.description = "음악을 일시 정지했습니다."

    await ctx.send(embed=embed)

@bot.slash_command(name='다시재생')
async def resume(ctx):
    """일시중지된 음악을 다시 재생합니다."""
    voice_client = ctx.guild.voice_client

    if voice_client is None:
        await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
        return

    embed = disnake.Embed(color=0x00ff00)
    if voice_client.is_playing() or not voice_client.is_paused():
        embed.description = "음악이 이미 재생 중이거나 재생할 음악이 존재하지 않습니다."
        embed.color = 0xff0000
    else:
        voice_client.resume()
        embed.description = "음악을 재개했습니다."

    await ctx.send(embed=embed)

@bot.slash_command(name='인증_문자', description='문자 인증')
async def sms_verify(ctx, phone_number: str):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
    
    if not os.path.exists(db_path):
        await database_create(ctx)
    else:
        aiodb = await aiosqlite.connect(db_path)
        aiocursor = await aiodb.execute("SELECT 인증역할, 인증채널 FROM 설정")
        role_id, channel_id = await aiocursor.fetchone()
        await aiocursor.close()
        await aiodb.close()

    if role_id:
        role = ctx.guild.get_role(role_id)
        if role:
            # 인증 역할이 이미 부여된 경우
            if role in ctx.author.roles:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="이미 인증된 상태입니다.")
                await ctx.send(embed=embed, ephemeral=True)
                return
            if channel_id:
                channel = ctx.guild.get_channel(channel_id)
                if channel and channel == ctx.channel:
                    # 인증 채널에서만 작동하는 코드 작성
                    verify_code = random.randint(100000, 999999)
                    text = f"인증번호: {verify_code}"
                    
                    # 문자 메시지 전송
                    send_sms(phone_number, text)

                    embed = disnake.Embed(color=embedsuccess)
                    embed.add_field(name="문자 인증", value=f"**{phone_number}** 으로 인증번호를 전송했습니다.")
                    await ctx.send(embed=embed, ephemeral=True)
                    print(f'''인증번호({verify_code})가 "{phone_number}"로 전송되었습니다.''')

                    def check(m):
                        return m.author == ctx.author and m.content == str(verify_code)

                    try:
                        msg = await bot.wait_for('message', check=check, timeout=180)
                        if msg:
                            await ctx.channel.purge(limit=1)
                            await ctx.author.add_roles(role)
                            embed = disnake.Embed(color=embedsuccess)
                            embed.add_field(name="문자 인증", value=f"{ctx.author.mention} 문자 인증이 완료되었습니다.")
                            await ctx.send(embed=embed)
                    except disnake.TimeoutError:
                        embed = disnake.Embed(color=embederrorcolor)
                        embed.add_field(name="❌ 오류", value="인증 시간이 초과되었습니다. 다시 시도해주세요.")
                        await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(color=embederrorcolor)
                    embed.add_field(name="❌ 오류", value="인증 채널에서만 인증 명령어를 사용할 수 있습니다.")
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="인증채널이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
                await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="**인증역할**이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
            await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="**인증역할**이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
        await ctx.send(embed=embed, ephemeral=True)
        
@bot.slash_command(name='인증_이메일', description='이메일 인증')
async def email_verify(ctx, email: str):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")

    # 데이터베이스가 존재하지 않는 경우
    if not os.path.exists(db_path):
        await database_create(ctx)
        await ctx.send("데이터베이스가 생성되었습니다.", ephemeral=True)
        return

    # 데이터베이스 연결 및 설정 가져오기
    aiodb = await aiosqlite.connect(db_path)
    aiocursor = await aiodb.execute("SELECT 인증역할, 인증채널 FROM 설정")
    row = await aiocursor.fetchone()
    await aiocursor.close()
    await aiodb.close()

    role_id, channel_id = row if row else (None, None)

    if role_id:
        role = ctx.guild.get_role(role_id)

        if role:
            # 인증 역할이 이미 부여된 경우
            if role in ctx.author.roles:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="이미 인증된 상태입니다.")
                await ctx.send(embed=embed, ephemeral=True)
                return

            if channel_id:
                channel = ctx.guild.get_channel(channel_id)
                if channel and channel == ctx.channel:
                    # 인증 코드 생성 및 이메일 전송
                    verifycode = random.randint(100000, 999999)
                    send_email(ctx, email, verifycode)
                    embed = disnake.Embed(color=0x00FF00)
                    embed.add_field(name="이메일 인증", value=f"**{email}** 으로 인증번호를 전송했습니다.")
                    await ctx.send(embed=embed, ephemeral=True)
                    print(f'''인증번호({verifycode})가 "{email}"로 전송되었습니다.''')

                    def check(m):
                        return m.author == ctx.author and m.content == str(verifycode)

                    try:
                        msg = await bot.wait_for('message', check=check, timeout=180)
                        await ctx.channel.purge(limit=1)
                        await ctx.author.add_roles(role)
                        embed = disnake.Embed(color=0x00FF00)
                        embed.add_field(name="이메일 인증", value=f"{ctx.author.mention} 메일 인증이 완료되었습니다.")
                        await ctx.send(embed=embed)
                    except disnake.TimeoutError:
                        embed = disnake.Embed(color=embederrorcolor)
                        embed.add_field(name="❌ 오류", value="인증 시간이 초과되었습니다. 다시 시도해주세요.")
                        await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(color=embederrorcolor)
                    embed.add_field(name="❌ 오류", value="인증 채널에서만 인증 명령어를 사용할 수 있습니다.")
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="인증채널이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
                await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="**인증역할**이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
            await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="**인증역할**이 설정되지 않은 서버입니다.\n서버 관리자에게 문의하세요.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="인증", description="캡챠 인증")
async def captcha_verify(ctx):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
    if not os.path.exists(db_path):
        await database_create(ctx)
    else:
        aiodb = await aiosqlite.connect(db_path)
        aiocursor = await aiodb.execute("SELECT 인증역할, 인증채널 FROM 설정")
        role_id, channel_id = await aiocursor.fetchone()
        await aiocursor.close()
        await aiodb.close()
    if role_id:
        role_id = role_id
        role = ctx.guild.get_role(role_id)
        if role:
            # 인증 역할이 이미 부여된 경우
            if role in ctx.author.roles:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="이미 인증된 상태입니다.")
                await ctx.send(embed=embed, ephemeral=True)
                return
            if channel_id:
                channel_id = channel_id
                channel = ctx.guild.get_channel(channel_id)
                if channel and channel == ctx.channel:
                    # 인증 채널에서만 작동하는 코드 작성
                    image_captcha = ImageCaptcha()
                    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    data = image_captcha.generate(captcha_text)
                    image_path = 'captcha.png'  # 이미지 파일 경로
                    with open(image_path, 'wb') as f:
                        f.write(data.getvalue())  # BytesIO 객체를 파일로 저장
                    embed = disnake.Embed(color=embedsuccess)
                    embed.add_field(name="인증", value="코드를 입력해주세요(6 자리)")
                    file = disnake.File(image_path, filename='captcha.png')
                    embed.set_image(url="attachment://captcha.png")  # 이미지를 임베드에 첨부
                    await ctx.send(embed=embed, file=file, ephemeral=True)
                    def check(m):
                        return m.author == ctx.author and m.content == captcha_text
                    try:
                        msg = await bot.wait_for('message', timeout=60.0, check=check)
                        await ctx.channel.purge(limit=1)
                    except TimeoutError:
                        await ctx.channel.purge(limit=1)
                        embed = disnake.Embed(color=embederrorcolor)
                        embed.add_field(name="❌ 오류", value="시간이 초과되었습니다. 다시 시도해주세요.")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.author.add_roles(role)
                        embed = disnake.Embed(color=embedsuccess)
                        embed.add_field(name="인증 완료", value=f"{ctx.author.mention} 캡챠 인증이 완료되었습니다.")
                        await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(color=embederrorcolor)
                    embed.add_field(name="❌ 오류", value="인증 채널에서만 인증 명령어를 사용할 수 있습니다.")
                    await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value="인증채널을 선택해주세요.")
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="인증역할을 찾을 수 없습니다.")
            await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="인증역할을 선택해주세요.")
        await ctx.send(embed=embed)

@bot.slash_command(name="지갑", description="자신이나 다른 유저의 지갑 조회")
async def wallet(ctx, member_id: str = None):
    await member_status(ctx)
    await check_experience()
    if not ctx.response.is_done():
        await ctx.response.defer()
    
    if member_id is None:
        user = ctx.author
    else:
        try:
            user = await bot.fetch_user(member_id)
        except:
            await ctx.response.send_message("유효하지 않은 유저 ID입니다.", ephemeral=True)
            return

    conn = await aiosqlite.connect('economy.db')
    c = await conn.cursor()
    await c.execute('SELECT * FROM user WHERE id=?', (user.id,))
    data = await c.fetchone()
    
    if data is None:
        await ctx.response.send_message(f"{user.mention}, 가입되지 않은 유저입니다.", ephemeral=True)
        await conn.close()
        return
    
    money = data[1]
    level = data[3]
    exp = data[4]
    lose_money = data[5]
    await c.execute('SELECT tos FROM user WHERE id=?', (user.id,))
    tos_data = await c.fetchone()
    await conn.close()
    
    if tos_data == 1:
        await ctx.response.send_message(f"{user.mention}, 이용제한된 유저입니다.", ephemeral=True)
        return
    
    tos = '정상' if tos_data[0] == 0 else '이용제한'
    
    embed = disnake.Embed(title=f"{user.name}의 지갑 💰", color=0x00ff00)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="아이디", value=f"{user.id}", inline=False)
    embed.add_field(name="레벨", value=f"{level:,}({exp:,}) Level", inline=False)
    embed.add_field(name="잔액", value=f"{money:,}원", inline=False)
    embed.add_field(name="잃은돈", value=f"{lose_money:,}원", inline=False)
    await ctx.send(embed=embed)

@bot.slash_command(name="돈순위", description="가장 돈이 많은 유저의 리스트를 보여줍니다.")
async def money_ranking(ctx: disnake.CommandInteraction, limit: int = 10):
    if limit <= 0:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="양수의 제한 값을 입력해야 합니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return

    # 제외할 유저 ID 리스트
    excluded_ids = developer

    economy_aiodb = await aiosqlite.connect("economy.db")  # 데이터베이스 연결

    # money를 기준으로 유저를 정렬하여 상위 limit명 가져오기 (제외할 ID 조건 추가)
    query = "SELECT id, money FROM user WHERE id NOT IN ({}) ORDER BY money DESC LIMIT ?".format(
        ','.join('?' for _ in excluded_ids)
    )
    
    # excluded_ids와 limit을 합쳐서 params 리스트 생성
    params = excluded_ids + [limit]

    aiocursor = await economy_aiodb.execute(query, params)
    richest_users = await aiocursor.fetchall()

    if not richest_users:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="등록된 유저가 없습니다.")
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = disnake.Embed(title="돈순위", color=0x00ff00)
        for rank, (user_id, money) in enumerate(richest_users, start=1):
            embed.add_field(name=f"{rank}위: {user_id}", value=f"돈: {money}", inline=False)

        await ctx.send(embed=embed)

    await aiocursor.close()
    await economy_aiodb.close()

@bot.slash_command(name="돈수정", description="돈수정 [개발자전용]")
async def money_edit(ctx, user: disnake.Member = commands.Param(name="유저"),choice: str = commands.Param(name="선택", choices=["차감", "추가"]), money: int = commands.Param(name="돈")):
    if ctx.author.id == developer:
        if choice == "차감":
            if not await removemoney(user.id, money):
                return await ctx.send("그 사용자의 포인트을 마이너스로 줄수없어요!")
            embed = disnake.Embed(title="잔액차감", color=embedsuccess)
            embed.add_field(name="차감금액", value=f"{money:,}원")
            embed.add_field(name="대상", value=f"{user.mention}")
            await ctx.send(embed=embed)
        elif choice == "추가":
            await addmoney(user.id, money)
            embed = disnake.Embed(title="잔액추가", color=embedsuccess)
            embed.add_field(name="추가금액", value=f"{money:,}원")
            embed.add_field(name="대상", value=f"{user.mention}")
            await ctx.send(embed=embed)
        else:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="차감, 추가중 선택해주세요.")
            await ctx.send(embed=embed, ephemeral=True)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="일하기", description="간단한 문제풀이로 5,000 ~ 30,000원을 얻습니다.")
async def earn_money(ctx):
    await member_status(ctx)
    cooldowns = load_cooldowns()
    last_execution_time = cooldowns.get(str(ctx.author.id), 0)
    current_time = time.time()
    cooldown_time = 30
    if current_time - last_execution_time < cooldown_time:
        remaining_time = round(cooldown_time - (current_time - last_execution_time))
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="쿨타임", value=f"{ctx.author.mention}, {remaining_time}초 후에 다시 시도해주세요.")
        await ctx.send(embed=embed)
        return
    number_1 = random.randrange(2, 10)
    number_2 = random.randrange(2, 10)
    random_add_money = random.randrange(5000, 30001)
    random_add_money = int(round(random_add_money, -3))

    correct_answer = number_1 + number_2
    await ctx.send(f"{number_1} + {number_2} =")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and int(msg.content) == correct_answer
    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('시간이 초과되었습니다. 다음 기회에 도전해주세요.')
    else:
        if msg.content == str(correct_answer):
            cooldowns[str(ctx.author.id)] = current_time
            save_cooldowns(cooldowns)
            embed = disnake.Embed(color=embedsuccess)
            await addmoney(ctx.author.id, random_add_money)
            await add_exp(ctx.author.id, round(random_add_money / 300))
            embed.add_field(name="정답", value=f"{ctx.author.mention}, {random_add_money:,}원이 지급되었습니다.")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'틀렸습니다! 정답은 {correct_answer}입니다.')

async def is_voted_bot(self, user_id: int, bot_id: int) -> koreanbots.model.KoreanbotsVote:
        """
        주어진 bot_id로 user_id를 통해 해당 user의 투표 여부를 반환합니다.
        """
        return koreanbots.model.KoreanbotsVote(**await self.get_bot_vote(user_id, bot_id))

@commands.slash_command(name="출석체크", description="봇 투표 여부를 확인하고 돈을 지급합니다.")
async def check_in(self, ctx: disnake.CommandInteraction):
    user_id = ctx.author.id
    bot_id = security.bot_id

    # 투표 여부 확인
    vote_info = await self.is_voted_bot(user_id, bot_id)

    if vote_info.voted:  # 'voted' 속성이 True인 경우
        # 사용자에게 지급할 금액
        payment_amount = 50000  # 지급할 금액 설정

        await addmoney(self.id, payment_amount)

        embed = disnake.Embed(title="✅ 출석 체크 완료", color=0x00FF00)
        embed.add_field(name="금액 지급", value=f"{payment_amount}원이 지급되었습니다.")
        await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(title="❌ 출석 체크 실패", color=0xFF0000)
        embed.add_field(name="오류", value="투표하지 않았습니다.")
        await ctx.send(embed=embed)
'''
@bot.slash_command(name="송금", description="돈 송금")
async def send_money(ctx, get_user: disnake.Member = commands.Param(name="받는사람"), money: int = commands.Param(name="금액")):
    await member_status(ctx)
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (get_user.id,))
    dbdata = await aiocursor.fetchone()
    await aiocursor.close()
    if dbdata is not None:
        if int(dbdata[0]) == 0:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="받는사람이 이용제한상태이므로 송금할수없습니다.")
            await ctx.send(embed=embed, ephemeral=True)
            await exit()
        else:
            pass
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="받는사람이 미가입상태이므로 송금할수없습니다.")
        await ctx.send(embed=embed, ephemeral=True)
        await exit()
    if money < 0:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="송금 금액은 음수가 될 수 없습니다.")
        await ctx.send(embed=embed, ephemeral=True)
    send_user = ctx.author
    send_user_money = await getmoney(send_user.id)
    if send_user_money < money:
        return await ctx.send(f"{send_user.mention}님의 잔액이 부족하여 송금할 수 없습니다.")
    await removemoney(send_user.id, money)
    await addmoney(get_user.id, money)
    embed = disnake.Embed(title="송금 완료", color=embedsuccess)
    embed.add_field(name="송금인", value=f"{send_user.mention}")
    embed.add_field(name="받는사람", value=f"{get_user.mention}")
    embed.add_field(name="송금 금액", value=f"{money:,}")
    await ctx.send(embed=embed)
'''
@bot.slash_command(name="도박", description="도박 (확률 25%, 2배, 실패시 -1배)")
async def betting(ctx, money: int = commands.Param(name="금액")):
    await member_status(ctx)
    user = ctx.author
    current_money = await getmoney(user.id)  # 현재 보유 금액 조회
    if money > current_money:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="가지고 있는 돈보다 배팅 금액이 많습니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    random_number = random.randrange(1, 101)
    if random_number <= 75: # 실패
        await removemoney(user.id, money)
        await add_lose_money(user.id, money)
        await add_exp(user.id, round(money / 1200))
        embed = disnake.Embed(title="실패", description=f"{money:,}원을 잃었습니다.", color=embederrorcolor)
        await ctx.send(embed=embed)
    elif random_number > 75: # 성공
        await addmoney(user.id, money)
        await add_exp(user.id, round(money / 600))
        embed = disnake.Embed(color=embedsuccess)
        money = money * 2
        embed.add_field(name="성공", value=f"{money:,}원을 얻었습니다.")
        await ctx.send(embed=embed)

@bot.slash_command(name="도박2", description="도박 (확률 50%, 1.5배, 실패시 -0.75배)")
async def betting_2(ctx, money: int = commands.Param(name="금액")):
    await member_status(ctx)
    user = ctx.author
    current_money = await getmoney(user.id)  # 현재 보유 금액 조회
    if money > current_money:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="가지고 있는 돈보다 배팅 금액이 많습니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    random_number = random.randrange(1, 101)
    if random_number <= 50: # 실패
        await removemoney(user.id, round(money * 0.75))
        await add_lose_money(user.id, round(money * 0.75))
        await add_exp(user.id, round((money * 0.75) / 1200))
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="실패", value=f"{money:,}원을 잃었습니다.")
        await ctx.send(embed=embed)
    elif random_number > 50: # 성공
        await addmoney(user.id, round(money * 0.5))
        await add_exp(user.id, round((money * 0.5) / 600))
        embed = disnake.Embed(color=embedsuccess)
        money = round(money * 1.5)
        embed.add_field(name="성공", value=f"{money:,}원을 얻었습니다.")
        await ctx.send(embed=embed)

@bot.slash_command(name="숫자도박", description="도박 (숫자맞추기 1~5, 확률 20%, 최대 3배, 실패시 -1.5배)")
async def betting_number(ctx, number: int = commands.Param(name="숫자"), money: int = commands.Param(name="금액")):
    await member_status(ctx)
    user = ctx.author
    current_money = await getmoney(user.id)  # 현재 보유 금액 조회
    if round(money * 1.5) > current_money:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="가진금액보다 배팅금이 많습니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    else:
        if number >= 6:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="1 ~ 5중 선택해주세요.")
            await ctx.send(embed=embed, ephemeral=True)
        elif number <= 0:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="1 ~ 5중 선택해주세요.")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            random_number = random.randrange(1, 6)
            if random_number == number:
                await addmoney(user.id, (money * 2))
                await add_exp(user.id, round((money * 2) / 600))
                embed = disnake.Embed(color=embedsuccess)
                money = money * 3
                embed.add_field(name="성공", value=f"{money:,}원을 얻었습니다.")
                await ctx.send(embed=embed)
            else:
                await removemoney(user.id, round(money * 1.5))
                await add_lose_money(user.id, round(money * 1.5))
                await add_exp(user.id, round((money * 1.5) / 1200))
                embed = disnake.Embed(color=embederrorcolor)
                money = round(money * 1.5)
                embed.add_field(name="실패", value=f"{money:,}원을 잃었습니다.")
                await ctx.send(embed=embed)

@bot.slash_command(name="이용제한", description="일부명령어 이용제한 [개발자전용]")
async def use_limit(ctx, user: disnake.Member = commands.Param(name="유저"), reason: str = commands.Param(name="사유", default=None)):
    if ctx.author.id == developer:
        if reason is None:
            reason = "없음"
        economy_aiodb = await aiosqlite.connect("economy.db")
        aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (user.id,))
        dbdata = await aiocursor.fetchone()
        await aiocursor.close()
        if dbdata is not None:
            if int(dbdata[0]) == 1:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value=f"{user.mention}는 이미 제한된 유저입니다.")
                await ctx.send(embed=embed)
            else:
                embed=disnake.Embed(title="✅ 이용제한", color=embederrorcolor)
                embed.add_field(name="대상", value=f"{user.mention}")
                embed.add_field(name="사유", value=f"{reason}")
                await ctx.send(embed=embed)
                aiocursor = await economy_aiodb.execute("UPDATE user SET tos=? WHERE id=?", (1, user.id))
                await economy_aiodb.commit()
                await aiocursor.close()
        else:
            # user 테이블에 새로운 유저 추가
            aiocursor = await economy_aiodb.execute("INSERT INTO user (id, money, tos) VALUES (?, ?, ?)", (user.id, 0, 1))
            await economy_aiodb.commit()
            await aiocursor.close()

            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="✅ 이용제한", value=f"{user.mention}\n가입되지 않은 유저였으므로 새로 추가되었습니다.")
            await ctx.send(embed=embed)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="제한해제", description="일부명령어 이용제한해제 [개발자전용]")
async def use_limit_release(ctx, user: disnake.Member = commands.Param(name="유저")):
    if ctx.author.id == developer:
        economy_aiodb = await aiosqlite.connect("economy.db")
        aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (user.id,))
        dbdata = await aiocursor.fetchone()
        await aiocursor.close()
        if dbdata is not None:
            if int(dbdata[0]) == 1:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="제한해제", value=f"{user.mention} 차단이 해제되었습니다.")
                await ctx.send(embed=embed)
                aiocursor = await economy_aiodb.execute("UPDATE user SET tos=? WHERE id=?", (0, user.id))
                await economy_aiodb.commit()
                await aiocursor.close()
            else:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value=f"{user.mention} 제한되지 않은 유저입니다.")
                await ctx.send(embed=embed)
        else:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value=f"{ctx.author.mention}\n가입되지 않은 유저입니다.")
            await ctx.send(embed=embed, ephemeral=True)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="회원추가", description="유료회원 등록 [개발자전용]")
async def member_add(ctx, user: disnake.Member = commands.Param(name="유저")):
    if ctx.author.id == developer:
        economy_aiodb = await aiosqlite.connect("membership.db")
        aiocursor = await economy_aiodb.execute("SELECT class FROM user WHERE id=?", (user.id,))
        dbdata = await aiocursor.fetchone()
        await aiocursor.close()
        if dbdata is not None:
            if int(dbdata[0]) == 1:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value=f"{user.mention}는 이미 유료회원입니다.")
                await ctx.send(embed=embed)
            elif int(dbdata[0]) == 2:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value=f"{user.mention}는 개발자입니다.")
                await ctx.send(embed=embed)
            elif int(dbdata[0]) == 0:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="✅ 회원등록", value=f"{user.mention}\n유료회원으로 등록되었습니다.")
                await ctx.send(embed=embed)
                aiocursor = await economy_aiodb.execute("UPDATE user SET class=? WHERE id=?", (1, user.id))
                await economy_aiodb.commit()
                await aiocursor.close()
        else:
            # user 테이블에 새로운 유저 추가
            aiocursor = await economy_aiodb.execute("INSERT INTO user (id, tos) VALUES (?, ?)", (user.id, 1))
            await economy_aiodb.commit()
            await aiocursor.close()

            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="✅ 회원등록", value=f"{user.mention}\n유료회원으로 등록되었습니다.")
            await ctx.send(embed=embed)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="회원삭제", description="유료회원 해제 [개발자전용]")
async def member_delete(ctx, user: disnake.Member = commands.Param(name="유저")):
    if ctx.author.id == developer:
        economy_aiodb = await aiosqlite.connect("membership.db")
        aiocursor = await economy_aiodb.execute("SELECT class FROM user WHERE id=?", (user.id,))
        dbdata = await aiocursor.fetchone()
        await aiocursor.close()
        if dbdata is not None:
            if int(dbdata[0]) == 1:
                aiocursor = await economy_aiodb.execute("UPDATE user SET class=? WHERE id=?", (0, user.id))
                await economy_aiodb.commit()
                await aiocursor.close()
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="제한해제", value=f"{user.mention} , 회원이 해제되었습니다.")
                await ctx.send(embed=embed)
            else:
                embed=disnake.Embed(color=embederrorcolor)
                embed.add_field(name="❌ 오류", value=f"{user.mention}, 유료회원이 아닙니다.")
                await ctx.send(embed=embed)
        else:
            # 데이터가 없을 경우 비회원으로 등록
            await economy_aiodb.execute("INSERT INTO user (id, class) VALUES (?, ?)", (ctx.author.id, 0))  # 0: 비회원
            await economy_aiodb.commit()
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value=f"{ctx.author.mention}\n, 유료회원이 아닙니다.")
            await ctx.send(embed=embed, ephemeral=True)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="코드추가", description="새로운 코드를 추가하고 기간을 설정합니다.")
async def license_code_add(ctx: disnake.CommandInteraction, code: str, 기간: int):
    # 기간을 일 단위로 받아서 설정
    if 기간 <= 0:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="유효한 기간을 입력해야 합니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return

    economy_aiodb = await aiosqlite.connect("membership.db")  # 데이터베이스 연결
    await economy_aiodb.execute("INSERT INTO license (code, day, use) VALUES (?, ?, ?)", (code, 기간, 0))
    await economy_aiodb.commit()

    embed = disnake.Embed(color=0x00ff00)
    embed.add_field(name="✅ 성공", value="코드가 추가되었습니다.")
    await ctx.send(embed=embed, ephemeral=True)
    await economy_aiodb.close()

@bot.slash_command(name="코드삭제", description="추가한 코드를 삭제합니다.")
async def license_code_remove(ctx: disnake.CommandInteraction, code: str):
    economy_aiodb = await aiosqlite.connect("membership.db")  # 데이터베이스 연결

    # 해당 코드가 존재하는지 확인
    aiocursor = await economy_aiodb.execute("SELECT * FROM license WHERE code=?", (code,))
    license_data = await aiocursor.fetchone()

    if license_data is None:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="유효하지 않은 코드입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        await aiocursor.close()
        await economy_aiodb.close()
        return

    # 코드 삭제
    await economy_aiodb.execute("DELETE FROM license WHERE code=?", (code,))
    await economy_aiodb.commit()

    embed = disnake.Embed(color=0x00ff00)
    embed.add_field(name="✅ 성공", value="코드가 삭제되었습니다.")
    await ctx.send(embed=embed, ephemeral=True)

    await aiocursor.close()
    await economy_aiodb.close()

@bot.slash_command(name="코드사용", description="회원 가입을 위한 코드 사용.")
async def license_code_use(ctx: disnake.CommandInteraction, code: str):
    economy_aiodb = await aiosqlite.connect("membership.db")

    # license 테이블에서 code 확인
    aiocursor = await economy_aiodb.execute("SELECT use, day FROM license WHERE code=?", (code,))
    license_data = await aiocursor.fetchone()

    if license_data is None:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="유효하지 않은 코드입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        await aiocursor.close()
        return

    # use 값이 1이면 이미 사용된 코드
    if license_data[0] == 1:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="이미 사용된 코드입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        await aiocursor.close()
        return

    # 현재 날짜 계산
    current_date = datetime.now()
    expiration_date = current_date + timedelta(days=license_data[1])
    
    # user 테이블에서 현재 사용자 확인
    aiocursor = await economy_aiodb.execute("SELECT class, expiration_date FROM user WHERE id=?", (ctx.author.id,))
    dbdata = await aiocursor.fetchone()

    if dbdata is None:
        # 데이터가 없을 경우 비회원으로 등록
        await economy_aiodb.execute("INSERT INTO user (id, class, expiration_date) VALUES (?, ?, ?)", 
                                     (ctx.author.id, 1, expiration_date.strftime('%Y/%m/%d')))  # 1: 회원
        await economy_aiodb.commit()
        embed = disnake.Embed(color=0x00ff00)
        embed.add_field(name="✅ 성공", value="비회원에서 회원으로 등록되었습니다.")
        await ctx.send(embed=embed, ephemeral=True)
    else:
        member_class = int(dbdata[0])
        if member_class == 0:  # 0: 비회원
            # 비회원에서 회원으로 변경
            await economy_aiodb.execute("UPDATE user SET class = ?, expiration_date = ? WHERE id = ?", 
                                         (1, expiration_date.strftime('%Y/%m/%d'), ctx.author.id))
            await economy_aiodb.commit()
            embed = disnake.Embed(color=0x00ff00)
            embed.add_field(name="✅ 성공", value="비회원에서 회원으로 변경되었습니다.")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="이미 회원입니다.")
            await ctx.send(embed=embed, ephemeral=True)

    # 코드 사용 처리 (use 값을 1로 업데이트)
    await economy_aiodb.execute("UPDATE license SET use = ? WHERE code = ?", (1, code))
    await economy_aiodb.commit()

    await aiocursor.close()
    await economy_aiodb.close()

@bot.slash_command(name="가입", description="게임기능 가입")
async def economy_join(ctx):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (ctx.author.id,))
    dbdata = await aiocursor.fetchone()
    await aiocursor.close()
    if dbdata == None:
        aiocursor = await economy_aiodb.execute("INSERT INTO user (id, money, tos) VALUES (?, ?, ?)", (ctx.author.id, 0, 0))
        await economy_aiodb.commit()
        await aiocursor.close()
        await addmoney(ctx.author.id, 30000)
        embed=disnake.Embed(color=embedsuccess)
        embed.add_field(name="✅ 가입", value=f"{ctx.author.mention} 가입이 완료되었습니다.\n지원금 30,000원이 지급되었습니다.")
        await ctx.send(embed=embed)
    else:
        if int(dbdata[0]) == 1:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="이용제한된 유저입니다.")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed=disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value=f"{ctx.author.mention} 이미 가입된 유저입니다.")
            await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="탈퇴", description="게임기능 탈퇴")
async def economy_secession(ctx):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (ctx.author.id,))
    dbdata = await aiocursor.fetchone()
    await aiocursor.close()
    
    if dbdata is not None:
        if int(dbdata[0]) == 1:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="이용제한된 유저입니다.")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(color=0xffff00)
            embed.add_field(name="탈퇴", value="경고! 탈퇴시 모든 데이터가 **즉시 삭제**되며\n보유중인 잔액이 초기화됩니다.")
            message = await ctx.send(embed=embed, view=AuthButton(economy_aiodb, ctx.author.id))

    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value=f"{ctx.author.mention}\n가입되지 않은 유저입니다.")
        await ctx.send(embed=embed, ephemeral=True)

class AuthButton(disnake.ui.View):
    def __init__(self, economy_aiodb, author_id):
        super().__init__(timeout=None)
        self.economy_aiodb = economy_aiodb
        self.author_id = author_id
        self.closed = False  # 새로운 속성 추가

    @disnake.ui.button(label="탈퇴", style=disnake.ButtonStyle.green)
    async def 탈퇴(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(color=0x00FF00)
        embed.add_field(name="탈퇴 완료!", value="탈퇴가 완료되었습니다!")
        await interaction.message.edit(embed=embed, view=None)
        aiocursor = await self.economy_aiodb.execute("DELETE FROM user WHERE id=?", (self.author_id,))
        await self.economy_aiodb.commit()
        await aiocursor.close()
        self.stop()
        button.disabled = True

    @disnake.ui.button(label="취소", style=disnake.ButtonStyle.red)
    async def 취소(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(color=0x00FF00)
        embed.add_field(name="탈퇴 취소", value="탈퇴가 취소되었습니다.")
        await interaction.message.edit(embed=embed, view=None)
        self.stop()
        button.disabled = True

async def update_stock_prices():
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("SELECT name, price FROM stock")
    stocks = await aiocursor.fetchall()

    for stock in stocks:
        name, price = stock
        new_price = round(price * random.uniform(0.9, 1.1), -1)
        new_price = min(new_price, 500000)  # 주식 가격 상한가
        new_price = max(new_price, 5000)  # 주식 가격 하한가
        new_price = int(new_price)
        await aiocursor.execute("UPDATE stock SET price = ? WHERE name = ?", (new_price, name))

    await economy_aiodb.commit()
    await aiocursor.close()

class StockView(disnake.ui.View):
    def __init__(self, data, per_page=5):
        super().__init__(timeout=None)
        self.data = data
        self.per_page = per_page
        self.current_page = 0
        self.max_page = (len(data) - 1) // per_page
        self.message = None
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.current_page > 0:
            self.add_item(PreviousButton())
        if self.current_page < self.max_page:
            self.add_item(NextButton())

    async def update_message(self, interaction=None):
        embed = self.create_embed()
        self.update_buttons()
        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        elif self.message:
            await self.message.edit(embed=embed, view=self)

    def create_embed(self):
        embed = disnake.Embed(title="주식 리스트", color=0x00ff00)
        start = self.current_page * self.per_page
        end = start + self.per_page
        for name, price in self.data[start:end]:
            embed.add_field(name=name, value=f"{price:,}원", inline=False)
        embed.set_footer(text=f"페이지 {self.current_page + 1}/{self.max_page + 1} | 마지막 업데이트: {self.last_updated}")
        return embed

class PreviousButton(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="이전", style=disnake.ButtonStyle.primary)

    async def callback(self, interaction: disnake.Interaction):
        view: StockView = self.view
        view.current_page -= 1
        await view.update_message(interaction)

class NextButton(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="다음", style=disnake.ButtonStyle.primary)

    async def callback(self, interaction: disnake.Interaction):
        view: StockView = self.view
        view.current_page += 1
        await view.update_message(interaction)

@bot.slash_command(name="주식리스트", description="주식리스트")
async def stock_list(ctx):
    data = await getstock()
    view = StockView(data)
    embed = view.create_embed()
    view.message = await ctx.send(embed=embed, view=view)
    view_update.start(view)

@tasks.loop(seconds=20)
async def view_update(view: StockView):
    view.data = await getstock()
    view.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await view.update_message()

@bot.slash_command(name="주식관리", description="주식을 추가하거나 삭제할 수 있습니다. [개발자전용]")
async def stock_management(ctx, _name: str, choice: str = commands.Param(name="선택", choices=["추가", "삭제"]), _price: float = commands.Param(name="가격", default=None)):
    if ctx.author.id == developer:
        if choice == "추가":
            await addstock(_name, _price)
            price = int(_price)
            embed = disnake.Embed(color=embedsuccess)
            embed.add_field(name="✅ 성공", value=f"{_name} 주식을 {price:,} 가격으로 추가하였습니다.")
            await ctx.send(embed=embed)
        elif choice == "삭제":
            await removestock(_name)
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="🗑️ 삭제", value=f"{_name} 주식을 삭제하였습니다.")
            await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="주식통장", description="보유주식확인")
async def stock_wallet(ctx):
    await member_status(ctx)
    stocks = await getuser_stock(ctx.author.id)
    
    embed = disnake.Embed(title=f"{ctx.name}의 주식통장 💰", color=0x00ff00)

    if not stocks:
        embed.add_field(name="❌ 오류", value="보유하고 있는 주식이 없습니다.")
        await ctx.send(embed=embed)
    else:
        market_stocks = await getstock()
        for name, count in stocks:
            stock_price = next((price for stock_name, price in market_stocks if stock_name == name), None)
            if stock_price is None:
                embed.add_field(name=name, value=f"{count}개 (현재 가격 정보를 가져오지 못했습니다.)", inline=False)
            else:
                embed.add_field(name=name, value=f"가격: {stock_price:,} | 보유 수량: {count:,}개", inline=False)

        await ctx.send(embed=embed)

@bot.slash_command(name="주식거래", description="주식을 구매 또는 판매할수 있습니다.")
async def stock_trading(ctx, _name: str, _count: int, choice: str = commands.Param(name="선택", choices=["구매", "판매"])):
    await member_status(ctx)
    embed = disnake.Embed(color=0x00ff00)
    try:
        stocks = await getstock()
        stock_info = next((price for name, price in stocks if name == _name), None)

        if stock_info is None:
            raise ValueError(f"{_name} 주식은 존재하지 않습니다.")
        else:
            stock_price = stock_info

        total_price = stock_price * _count
        
        if choice == "구매":
            await adduser_stock(ctx.author.id, _name, _count)
            embed.title = "주식 구매 완료"
            embed.add_field(name="주식 이름", value=_name, inline=False)
            embed.add_field(name="구매 수량", value=f"{_count:,}개", inline=False)
            await add_exp(ctx.id, round((total_price * 0.5) / 1000))
            embed.add_field(name="총 구매 가격", value=f"{total_price:,}원", inline=False)

        elif choice == "판매":
            await removeuser_stock(ctx.author.id, _name, _count)
            embed.title = "주식 판매 완료"
            embed.add_field(name="주식 이름", value=_name, inline=False)
            embed.add_field(name="판매 수량", value=f"{_count:,}개", inline=False)
            await add_exp(ctx.id, round((total_price * 0.5) / 1000))
            embed.add_field(name="총 판매 가격", value=f"{total_price:,}원", inline=False)

        await ctx.send(embed=embed)
    except ValueError as e:
        embed = disnake.Embed(color=0xff0000)
        embed.add_field(name="❌ 오류", value=str(e))
        await ctx.send(embed=embed)

@bot.slash_command(name="서버설정_채널", description="채널설정(로그채널 및 기타채널을 설정합니다) [관리자전용]")
async def server_set(ctx, kind: str = commands.Param(name="종류", choices=["공지채널", "처벌로그", "입장로그", "퇴장로그", "인증채널"]), channel: disnake.TextChannel = commands.Param(name="채널")):
    if ctx.author.guild_permissions.manage_messages:
        db_path = os.path.join(os.getcwd(), "database", f"{channel.guild.id}.db")
        if not os.path.exists(db_path):
            await database_create(ctx)
        else:
            try:
                aiodb = await aiosqlite.connect(db_path)
                aiocursor = await aiodb.execute("SELECT * FROM 설정")
                dat = await aiocursor.fetchall()
                await aiocursor.close()
                if not dat:
                    aiocursor = await aiodb.execute(
                        f"INSERT INTO 설정 ({kind}) VALUES (?)", (channel.id,))
                    await aiodb.commit()
                    await aiocursor.close()
                else:
                    aiocursor = await aiodb.execute(f"UPDATE 설정 SET {kind} = ?", (channel.id,))
                    await aiodb.commit()
                    await aiocursor.close()
                    embed = disnake.Embed(color=embedsuccess)
                    embed.add_field(name="채널설정", value=f"{channel.mention}이(가) **{kind}**로 설정되었습니다")
                    await ctx.send(embed=embed)
            except Exception as e:
                embed = disnake.Embed(color=embederrorcolor)
                embed.add_field(name="오류 발생", value=f"데이터베이스 연결 중 오류가 발생했습니다: {e}")
                await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행 가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="서버설정_역할", description="역할설정(인증역할 및 기타역할을 설정합니다) [관리자전용]")
async def server_set_role(ctx, kind: str = commands.Param(name="종류", choices=["인증역할"]), role: disnake.Role = commands.Param(name="역할")):
    if ctx.author.guild_permissions.manage_messages:
        db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
        if not os.path.exists(db_path):
            await database_create(ctx)
        else:
            aiodb = await aiosqlite.connect(db_path)
            aiocursor = await aiodb.execute("SELECT * FROM 설정")
            dat = await aiocursor.fetchall()
            await aiocursor.close()
            if not dat:
                aiocursor = await aiodb.execute(
                    f"INSERT INTO 설정 ({kind}) VALUES (?)", (role.id,))
                await aiodb.commit()
                await aiocursor.close()
            else:
                aiocursor = await aiodb.execute(f"UPDATE 설정 SET {kind} = ?", (role.id,))
                await aiodb.commit()
                await aiocursor.close()
                embed = disnake.Embed(color=embedsuccess)
                embed.add_field(name="역할설정", value=f"{role.mention}이(가) **{kind}**로 설정되었습니다")
                await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행 가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="서버정보", description="설정되있는 로그채널을 확인할수있습니다 [관리자전용]")
async def server_info(ctx):
    if ctx.author.guild_permissions.manage_messages:
        db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
        if not os.path.exists(db_path):
            await database_create(ctx)
        aiodb = await aiosqlite.connect(db_path)
        aiocursor = await aiodb.execute("SELECT * FROM 설정")
        dat = await aiocursor.fetchone()
        await aiocursor.close()
        embed = disnake.Embed(title="서버설정", color=embedcolor)
        
        if dat:
            # 공지 채널
            if dat[0] is not None:
                announcement_channel = ctx.guild.get_channel(int(dat[0]))
                if announcement_channel:  # 채널이 존재하는지 확인
                    embed.add_field(name="공지채널", value=f"<#{announcement_channel.id}>", inline=False)
                else:
                    embed.add_field(name="공지채널", value="채널을 찾을 수 없음", inline=False)
            else:
                embed.add_field(name="공지채널", value="설정되지 않음", inline=False)

            # 처벌 로그 채널
            if dat[1] is not None:
                punishment_log_channel = ctx.guild.get_channel(int(dat[1]))
                if punishment_log_channel:
                    embed.add_field(name="처벌로그", value=f"<#{punishment_log_channel.id}>", inline=False)
                else:
                    embed.add_field(name="처벌로그", value="채널을 찾을 수 없음", inline=False)
            else:
                embed.add_field(name="처벌로그", value="설정되지 않음", inline=False)

            # 입장 로그 채널
            if dat[2] is not None:
                entry_log_channel = ctx.guild.get_channel(int(dat[2]))
                if entry_log_channel:
                    embed.add_field(name="입장로그", value=f"<#{entry_log_channel.id}>", inline=False)
                else:
                    embed.add_field(name="입장로그", value="채널을 찾을 수 없음", inline=False)
            else:
                embed.add_field(name="입장로그", value="설정되지 않음", inline=False)

            # 퇴장 로그 채널
            if dat[3] is not None:
                exit_log_channel = ctx.guild.get_channel(int(dat[3]))
                if exit_log_channel:
                    embed.add_field(name="퇴장로그", value=f"<#{exit_log_channel.id}>", inline=False)
                else:
                    embed.add_field(name="퇴장로그", value="채널을 찾을 수 없음", inline=False)
            else:
                embed.add_field(name="퇴장로그", value="설정되지 않음", inline=False)

            # 인증 역할
            if dat[4] is not None:
                auth_role = ctx.guild.get_role(int(dat[4]))
                if auth_role:
                    embed.add_field(name="인증역할", value=f"<@&{auth_role.id}>", inline=False)
                else:
                    embed.add_field(name="인증역할", value="역할을 찾을 수 없음", inline=False)
            else:
                embed.add_field(name="인증역할", value="설정되지 않음", inline=False)

            # 인증 채널
            if dat[5] is not None:
                exit_log_channel = ctx.guild.get_channel(int(dat[5]))
                if exit_log_channel:
                    embed.add_field(name="인증채널", value=f"<#{exit_log_channel.id}>")
                else:
                    embed.add_field(name="인증채널", value="채널을 찾을 수 없음")
            else:
                embed.add_field(name="인증채널", value="설정되지 않음")
        
        await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="정보", description="봇의 실시간 상태와 정보를 알 수 있습니다.")
async def bot_info(ctx):
    start_time = time.time()  # 시작 시간 기록
    await ctx.response.defer()
    end_time = time.time()  # 끝 시간 기록
    ping_time = (end_time - start_time) * 1000  # 밀리초로 변환

    # 응답 시간에 따라 임베드 색상 및 메시지 결정
    if ping_time < 100:
        embed_color = 0x00ff00  # 초록색 (좋음)
        status = "응답 속도가 매우 좋습니다! 🚀"
    elif ping_time < 300:
        embed_color = 0xffff00  # 노란색 (보통)
        status = "응답 속도가 좋습니다! 😊"
    elif ping_time < 1000:
        embed_color = 0xffa500  # 주황색 (나쁨)
        status = "응답 속도가 느립니다. 😕"
    else:
        embed_color = 0xff0000  # 빨간색 (매우 나쁨)
        status = "응답 속도가 매우 느립니다! ⚠️"
    embed = disnake.Embed(title="봇 정보", color=embed_color)
    embed.add_field(name="서버수", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="업타임", value=f"{get_uptime()}", inline=True)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="서포트서버", value=f"[support]({security.support_server_url})", inline=True)
    embed.add_field(name="개발자", value=f"{security.developer_name}", inline=True)
    # 운영 체제의 상세 정보 가져오기
    uname_info = platform.uname()

    # 메모리 정보 가져오기
    memory_info = psutil.virtual_memory()

    total_memory = f"{memory_info.total / (1024 ** 3):.2f}"
    used_memory = f"{memory_info.used / (1024 ** 3):.2f}"
    percent_memory = memory_info.percent
    # 서버 시간
    server_date = datetime.now()
    embed.add_field(name="시스템 정보", value=f"```python {platform.python_version()}\ndiscord.py {version("discord.py")}\ndisnake {version("disnake")}\nOS : {uname_info.system} {uname_info.release}\nMemory : {total_memory}GB / {used_memory}GB ({percent_memory}%)```\n응답속도 : {int(ping_time)}ms / {status}\n{server_date.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")}", inline=False)
    await ctx.send(embed=embed)

@bot.slash_command(name="개발자_공지", description="개발자 공지 [개발자전용]")
async def developer_notification(ctx, *, content: str = commands.Param(name="내용")):
    if ctx.author.id == developer:
        for guild in bot.guilds:
            server_remove_date = datetime.now()
            embed1 = disnake.Embed(title="개발자 공지", description=f"```{content}```", color=embedcolor)
            embed1.set_footer(text=f'To. {security.developer_company}({ctx.author.name})\n{server_remove_date.strftime("전송시간 %Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")}')
            
            chan = None  # 채널 변수를 초기화합니다.
            for channel in guild.text_channels:
                try:
                    if channel.topic and security.notification_topic in channel.topic:  # topic이 None이 아닐 때 확인
                        chan = channel
                        break  # 첫 번째 채널을 찾으면 루프를 종료합니다.
                except:
                    pass
            
            try:
                if chan and chan.permissions_for(guild.me).send_messages:
                    await chan.send(embed=embed1)
                else:
                    raise ValueError("채널이 없거나 메시지 전송 권한이 없습니다.")
            except:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        embed1.set_footer(text=f'To. CodeStone({ctx.author.name})\n{server_remove_date.strftime("전송시간 %Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")}')
                        try:
                            await channel.send(embed=embed1)
                        except Exception as e:
                            print(f"Error sending message to {channel.name}: {e}")  # 예외 로그 추가
                        break

        embed = disnake.Embed(title="공지 업로드 완료!", color=embedsuccess)
        await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="개발자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="슬로우모드", description="슬로우모드 설정 [관리자전용]")
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, time: int = commands.Param(name="시간", description="시간(초)")):
    if ctx.author.guild_permissions.manage_messages:
        if time == 0:
            embed = disnake.Embed(title="\✅슬로우모드를 껐어요.", color=embedsuccess)
            await ctx.send(embed=embed)
            await ctx.channel.edit(slowmode_delay=0)
            return
        elif time > 21600:
            embed = disnake.Embed(title="\❌슬로우모드를 6시간 이상 설정할수 없어요.", color=embederrorcolor)
            await ctx.send(embed=embed, ephemeral=True)
            return
        else:
            await ctx.channel.edit(slowmode_delay=time)
            embed = disnake.Embed(title=f"\✅ 성공적으로 슬로우모드를 {time}초로 설정했어요.", color=embedsuccess)
            await ctx.send(embed=embed)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="청소", description="메시지를 삭제합니다. [관리자전용]")
async def clear(ctx, num: int = commands.Param(name="개수")):
    if ctx.author.guild_permissions.manage_messages:
        num = int(num)
        await ctx.channel.purge(limit=num)
        embed = disnake.Embed(color=embedsuccess)
        embed.add_field(name=f"{num}개의 메시지를 지웠습니다.", value="")
        await ctx.send(embed=embed)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="공지", description="서버 공지를 전송합니다. [관리자전용]")
async def notification(ctx, *, content: str = commands.Param(name="내용")):
    if ctx.author.guild_permissions.manage_messages:
        db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
        if not os.path.exists(db_path):
            await database_create(ctx)
        else:
            aiodb = await aiosqlite.connect(db_path)
            aiocursor = await aiodb.execute("SELECT 공지채널 FROM 설정")
            설정_result = await aiocursor.fetchone()
            await aiocursor.close()
            
            if 설정_result:
                공지채널_id = 설정_result[0]
                공지채널 = bot.get_channel(공지채널_id)
            
            if 공지채널:
                for guild in bot.guilds:
                    server_remove_date = datetime.now()
                    embed1 = disnake.Embed(title=f"{guild.name} 공지", description=f"```{content}```", color=embedcolor)
                    embed1.set_footer(text=f'To. {ctx.author.display_name}\n{server_remove_date.strftime("전송시간 %Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")}')
                    try:
                        chan = guild.get_channel(공지채널_id)
                        if chan and chan.permissions_for(guild.me).send_messages:
                            await chan.send(embed=embed1)
                    except Exception as e:
                        print(f"Error sending message to {guild.name}: {e}")  # 예외 로그 추가
            else:
                embed = disnake.Embed(title="오류", description="공지채널이 없습니다.\n공지채널을 설정해주세요.")
                await ctx.send(embed=embed)  # 오류 메시지 전송

            embed = disnake.Embed(title="공지 업로드 완료!", color=embedsuccess)
            await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="추방", description="추방 [관리자전용]")
async def kick(ctx, user: disnake.Member = commands.Param(name="유저"), reason: str = commands.Param(name="사유", default=None)):
    if ctx.author.guild_permissions.kick_members:
        try:
            await ctx.guild.kick(user)
        except:
            embed = disnake.Embed(title=f"{user.name}를 추방하기엔 권한이 부족해요...", color=embederrorcolor)
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="✅추방을 완료했어요", color=embedsuccess)
            embed.add_field(name="대상", value=f"{user.mention}")
            embed.add_field(name="사유", value=f"{reason}", inline=False)
            await ctx.send(embed=embed)
            db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
            if not os.path.exists(db_path):
                await database_create(ctx)
            aiodb = await aiosqlite.connect(db_path)
            aiocursor = await aiodb.execute("select * from 설정 order by 공지채널 desc")
            dat = await aiocursor.fetchone()
            await aiocursor.close()
            aiocursor = await aiodb.execute("SELECT 처벌로그 FROM 설정")
            설정_result = await aiocursor.fetchone()
            await aiocursor.close()
            if 설정_result:
                경고채널_id = 설정_result[0]
                경고채널 = bot.get_channel(경고채널_id)
                if 경고채널:
                    embed = disnake.Embed(title="추방", color=embederrorcolor)
                    embed.add_field(name="관리자", value=f"{ctx.author.mention}")
                    embed.add_field(name="대상", value=f"{user.mention}")
                    embed.add_field(name="사유", value=f"{reason}", inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("경고채널을 찾을 수 없습니다.")
                    embed
            else:
                await ctx.send("경고채널이 설정되지 않았습니다.")
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="차단", description="차단 [관리자전용]")
async def ban(ctx, user: disnake.Member = commands.Param(description="유저"), reason: str = commands.Param(name="사유", default=None)):
    if ctx.author.guild_permissions.ban_members:
        try:
            await ctx.guild.ban(user)
        except:
            embed = disnake.Embed(title=f"{user.name}를 차단하기엔 권한이 부족해요...", color=embederrorcolor)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="차단", color=embederrorcolor)
            embed.add_field(name="관리자", value=f"{ctx.author.mention}")
            embed.add_field(name="대상", value=f"{user.mention}")
            embed.add_field(name="사유", value=f"{reason}", inline=False)
            await ctx.send(embed=embed)
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="경고확인", description="보유중인 경고를 확인합니다.")
async def warning_check(ctx, user: disnake.Member = commands.Param(name="유저", default=None)):
    if user is None:
        user = ctx.author
    dat, accumulatewarn = await getwarn(ctx, user)
    
    if not dat:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="확인된 경고가 없습니다.", value="")
        await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(title=f"{user.name}님의 경고 리스트", color=embedcolor)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=f"누적경고 : {accumulatewarn} / 30", value="", inline=False)
        for i in dat:
            embed.add_field(name=f"경고 #{i[0]}", value=f"경고수: {i[3]}\n사유: {i[4]}", inline=False)
        await ctx.send(embed=embed)

@bot.slash_command(name="경고", description="경고지급 [관리자전용]")
async def warning(ctx, user: disnake.Member, warn_num: int = None, reason: str = None):
    if ctx.author.guild_permissions.manage_messages:
        if warn_num is None:
            warn_num = "1"
        if reason is None:
            reason = "없음"
        new_id, accumulatewarn, 설정_result = await addwarn(ctx, user, warn_num, reason)
        if 설정_result:
            경고채널_id = 설정_result[0]
            경고채널 = bot.get_channel(경고채널_id)
            if 경고채널:
                embed = disnake.Embed(title=f"#{new_id} - 경고", color=embederrorcolor)
                embed.add_field(name="관리자", value=ctx.author.mention, inline=False)
                embed.add_field(name="대상", value=user.mention, inline=False)
                embed.add_field(name="사유", value=reason, inline=False)
                embed.add_field(name="누적 경고", value=f"{accumulatewarn} / 10 (+ {warn_num})", inline=False)
                await 경고채널.send(embed=embed)
            else:
                await ctx.send("경고채널을 찾을 수 없습니다.")
        else:
            await ctx.send("경고채널이 설정되지 않았습니다.")
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="경고취소", description="경고취소 [관리자전용]")
async def warning_cancel(ctx, warn_id: int, reason: str = None):
    if ctx.author.guild_permissions.manage_messages:
        if reason is None:
            reason = "없음"
        warn_id = await removewarn(ctx, warn_id)
        if warn_id is None:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="이미 취소되었거나 없는 경고입니다.", value="")
            await ctx.send(embed=embed)
        else:
            await aiocursor.execute("DELETE FROM 경고 WHERE 아이디 = ?", (warn_id,))
            await aiodb.commit()  # 변경 사항을 데이터베이스에 확정합니다.
            embed = disnake.Embed(color=embedsuccess)
            embed.add_field(name=f"경고 #{warn_id}(이)가 취소되었습니다.", value="")
            embed.add_field(name="사유", value=reason, inline=False)
            await ctx.send(embed=embed)
            aiocursor = await aiodb.execute("SELECT 처벌로그 FROM 설정")
            set_result = await aiocursor.fetchone()
            await aiocursor.close()
            if set_result:
                warnlog_id = set_result[0]
                warnlog = bot.get_channel(warnlog_id)
                if warnlog:
                    embed = disnake.Embed(title=f"#{warn_id} - 경고 취소", color=embedwarning)
                    embed.add_field(name="관리자", value=ctx.author.mention, inline=False)
                    embed.add_field(name="사유", value=reason, inline=False)
                    await warnlog.send(embed=embed)
                else:
                    await ctx.send("경고채널을 찾을 수 없습니다.")
            else:
                await ctx.send("경고채널이 설정되지 않았습니다.")
        await aiocursor.close()
    else:
        embed=disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="관리자만 실행가능한 명령어입니다.")
        await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="문의", description="개발자에게 문의하기")
async def inquire(ctx):
    embed = disnake.Embed(color=embederrorcolor)
    embed.add_field(name="❌ 오류", value=f"{ctx.author.mention}, 문의는 봇 DM으로 부탁드립니다!")
    await ctx.send(embed=embed)

@bot.slash_command(name="문의답장", description="개발자가 유저에게 답변을 보냅니다 [개발자전용]")
async def inquire_answer(ctx, member: str, message: str):
    # 멘션 형식에서 ID 추출
    member_id = int(member.replace('<@', '').replace('>', '').replace('!', ''))
    guild = ctx.guild  # 명령어가 실행된 서버

    user = guild.get_member(member_id)
    # 개발자 ID 확인
    if ctx.author.id != developer:  # 개발자가 아닐 경우 오류 메시지
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="이 명령어는 개발자만 사용할 수 있습니다.")
        await ctx.send(embed=embed)
        return
    
    if user is not None:
        try:
            await user.send(f"{ctx.author.mention} : {message}")
            embed = disnake.Embed(title="✅ 전송완료", color=embedcolor)
            embed.add_field(name="대상자", value=f"{user.mention}")
            embed.add_field(name="답장 내용", value=f"{message}")
            await ctx.send(embed=embed)
        except disnake.Forbidden:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value=f"{user.mention}님에게 메시지를 보낼 수 없습니다. DM을 허용하지 않았습니다.")
            await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value=f"{member}님을 찾을 수 없습니다.")
        await ctx.send(embed=embed)
##################################################################################################
# 처리된 멤버를 추적하기 위한 집합
processed_members = set()

@bot.event
async def on_member_join(member):
    # 이미 처리된 멤버인지 확인
    if member.id in processed_members:
        return  # 이미 처리된 멤버는 무시

    # 처리된 멤버 목록에 추가
    processed_members.add(member.id)

    # 데이터베이스 연결 및 비동기 커서 생성
    await database_create(member)
    db_path = os.path.join(os.getcwd(), "database", f"{member.guild.id}.db")
    aiodb = await aiosqlite.connect(db_path)
    aiocursor = await aiodb.cursor()  # 비동기 커서 생성
    try:
        # 설정 테이블에서 입장 로그 채널 아이디 가져오기
        await aiocursor.execute("SELECT 입장로그 FROM 설정")
        result = await aiocursor.fetchone()
        if result is not None:
            channel_id = result[0]
            # 채널 아이디에 해당하는 채널에 입장 로그 보내기
            channel = bot.get_channel(channel_id)
            if channel is not None:
                embedcolor = 0x00FF00  # 임베드 색상 설정
                embed = disnake.Embed(title="입장로그", color=embedcolor)
                embed.add_field(name="유저", value=f"{member.mention} ({member.name})")
                embed.set_thumbnail(url=member.display_avatar.url)
                server_join_date = datetime.now()  # datetime 클래스를 직접 사용
                account_creation_date = member.created_at
                embed.add_field(name="서버입장일", value=server_join_date.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후"), inline=False)
                embed.add_field(name="계정생성일", value=account_creation_date.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후"), inline=False)
                await channel.send(embed=embed)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    finally:
        # 데이터베이스 연결 종료
        await aiocursor.close()
        await aiodb.close()

@bot.event
async def on_member_remove(member):
    # 데이터베이스 연결 및 비동기 커서 생성
    await database_create(member)
    db_path = os.path.join(os.getcwd(), "database", f"{member.guild.id}.db")
    aiodb = await aiosqlite.connect(db_path)
    aiocursor = await aiodb.cursor()  # 비동기 커서 생성
    try:
        await aiocursor.execute("SELECT 퇴장로그 FROM 설정")
        result = await aiocursor.fetchone()
        if result is not None:
            channel_id = result[0]
            channel = bot.get_channel(channel_id)
            if channel is not None:
                embedcolor = 0x00FF00
                embed = disnake.Embed(title="퇴장로그", color=embedcolor)
                embed.add_field(name="유저", value=f"{member.mention} ({member.name})")
                server_remove_date = datetime.now()
                embed.add_field(name="서버퇴장일", value=server_remove_date.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후"), inline=False)
                await channel.send(embed=embed)
    finally:
        # 데이터베이스 연결 종료
        await aiocursor.close()
        await aiodb.close()

@bot.event
async def on_message(message):
    # 봇이 보낸 메시지는 무시
    if message.author == bot.user:
        return
    # 사용자 ID
    user_id = str(message.author.id)

    await add_exp(user_id, 5)

    if message.author.bot:
        return
    if isinstance(message.channel, disnake.DMChannel):
        user = str(f"{message.author.display_name}({message.author.name})")
        avatar_url = message.author.avatar.url if message.author.avatar else None

        # 데이터베이스 연결 및 TOS 확인
        economy_aiodb = await aiosqlite.connect("economy.db")
        aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (message.author.id,))
        dbdata = await aiocursor.fetchone()
        await aiocursor.close()

        if dbdata is not None and int(dbdata[0]) == 1:
            try:
                await message.add_reaction("❌")
            except Exception as e:
                print(f"이모지 반응 중 오류 발생: {e}")

            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="이용제한된 유저입니다.\nstone6718 DM으로 문의주세요.")
            await message.channel.send(embed=embed)
            return
        else:
            try:
                await message.add_reaction("✅")
            except Exception as e:
                print(f"이모지 반응 중 오류 발생: {e}")
        
        # 문의 접수 메시지 전송
        embed = disnake.Embed(color=embedcolor)
        embed.add_field(name="문의 접수", value=f"{user}, 문의가 접수되었습니다. 감사합니다!")
        await message.channel.send(embed=embed)
        
        print("문의가 접수되었습니다.")
        
        # 임베드 메시지 생성
        dm_embed = disnake.Embed(title="새로운 문의", color=embedcolor)
        dm_embed.add_field(name="사용자", value=user, inline=False)
        dm_embed.add_field(name="아이디", value=message.author.id, inline=False)
        dm_embed.add_field(name="내용", value=str(message.content), inline=False)
        if avatar_url:
            dm_embed.set_thumbnail(url=avatar_url)
        
        # 특정 채널로 전송
        channel_id = int(security.support_ch_id)
        channel = bot.get_channel(channel_id)
        
        if channel is None:
            print(f"채널 ID {channel_id}을(를) 찾을 수 없습니다.")
        else:
            try:
                await channel.send(embed=dm_embed)
                print(f"메시지가 채널 ID {channel_id}로 전송되었습니다.")
            except Exception as e:
                print(f"메시지를 채널로 전송하는 중 오류 발생: {e}")
        
        # 첨부 파일 처리
        if message.attachments:
            for attachment in message.attachments:
                try:
                    # 파일 다운로드
                    file = await attachment.to_file()
                    await channel.send(file=file)
                    print(f"파일 {attachment.filename}이(가) 채널 ID {channel_id}로 전송되었습니다.")
                except Exception as e:
                    print(f"파일을 채널로 전송하는 중 오류 발생: {e}")

def get_uptime():
    """업타임을 계산하는 함수."""
    now = datetime.now()
    uptime = now - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}시간 {minutes}분 {seconds}초"

@bot.event
async def on_ready():
    print("\n봇 온라인!")
    print(f'{bot.user.name}')
    change_status.start()
    koreabots.start()

@tasks.loop(seconds=3)
async def change_status():
    guild_len = len(bot.guilds)
    statuses = [f'음악 재생', '편리한 기능을 제공', f'{guild_len}개의 서버를 관리']
    for i in statuses:
        await bot.change_presence(status=disnake.Status.online, activity=disnake.Game(i))
        await asyncio.sleep(3)

aiodb = {}
economy_aiodb = None

@tasks.loop(seconds=3)
async def koreabots():
    url = f"https://koreanbots.dev/api/v2/bots/{bot.user.id}/stats"
    headers = {
        "Authorization": security.koreanbots_api_key,
        "Content-Type": "application/json"
    }
    body = {
        "servers": len(bot.guilds),
        "shards": 1,
    }

    response = requests.post(url=url, data=json.dumps(body), headers=headers)
    data = response.json()

@tasks.loop()
async def periodic_price_update():
    while True:
        await update_stock_prices()
        await asyncio.sleep(20)

periodic_price_update.start()

@tasks.loop(hours=12)
async def check_expired_members():
    economy_aiodb = await aiosqlite.connect("membership.db")
    current_date = datetime.now().strftime('%Y/%m/%d')
    
    # 만료된 회원을 비회원으로 변경
    await economy_aiodb.execute("UPDATE user SET class = 0 WHERE class = 1 AND expiration_date < ?", (current_date,))
    await economy_aiodb.commit()
    await economy_aiodb.close()

check_expired_members.start()

limit_level = 1000  # 최대 레벨 (예시)

def calculate_experience_for_level(current_level):
    if current_level is None:
        current_level = 1  # 기본값 설정
        
    E_0 = 100  # 기본 경험치 (예시)
    r = 1.5    # 경험치 증가 비율 (예시)
    k = 50     # 추가 경험치 (예시)

    n = current_level
    base_experience = math.floor(E_0 * (r ** (n - 1)) + k)
    return base_experience

@tasks.loop(seconds=20)  # 20초마다 실행
async def check_experience():
    conn = await aiosqlite.connect('economy.db')
    c = await conn.cursor()
    
    await c.execute('SELECT id, exp, level FROM user')
    rows = await c.fetchall()
    
    updates = []
    messages = []

    for row in rows:
        user_id, current_experience, current_level = row
        
        # current_experience와 current_level이 None인 경우 기본값 설정
        if current_experience is None:
            current_experience = 0  # 경험치 기본값 설정
        if current_level is None:
            current_level = 1  # 레벨 기본값 설정

        required_experience = calculate_experience_for_level(current_level)
        new_level = current_level  # 새로운 레벨을 추적
        
        while current_experience >= required_experience and new_level < limit_level:
            new_level += 1  # 레벨을 증가
            required_experience = calculate_experience_for_level(new_level)

        # 레벨을 1 빼기
        adjusted_level = new_level - 1

        # 레벨이 상승했으면 메시지를 준비
        if adjusted_level > current_level:
            updates.append((adjusted_level, user_id))  # 업데이트할 레벨 저장
            
            # 최대 레벨에 도달하지 않았을 때만 메시지 준비
            if adjusted_level < limit_level:
                messages.append((user_id, adjusted_level))  # 메시지를 보낼 사용자 및 새로운 레벨 저장

    # 사용자 레벨 업데이트
    if updates:  # updates가 비어있지 않으면 업데이트 실행
        await c.executemany('UPDATE user SET level = ? WHERE id = ?', updates)
    
    await conn.commit()
    await conn.close()

    # DM 메시지 전송
    for user_id, adjusted_level in messages:
        user = await bot.fetch_user(user_id)
        if user:
            try:
                channel = await user.create_dm()
                embed = disnake.Embed(
                    title="레벨 업! 🎉",
                    description=f'축하합니다! 레벨이 **{adjusted_level}**로 올랐습니다!', 
                    color=0x00ff00
                )
                await channel.send(embed=embed)
            except disnake.errors.HTTPException as e:
                print(f"DM을 보낼 수 없습니다: {e}")

check_experience.start()

async def startup():
    await bot.start(token, reconnect=True)
    global aiodb
    aiodb = {}
    for guild in bot.guilds:
        db_path = os.path.join(os.getcwd(), "database", f"{guild.id}.db")
        aiodb[guild.id] = await aiosqlite.connect(db_path)
    global economy_aiodb
    if economy_aiodb is None:
        economy_aiodb = await aiosqlite.connect("economy.db")

async def shutdown():
    for aiodb_instance in aiodb.values():
        await aiodb_instance.close()
    await aiodb.close()
    await economy_aiodb.close()
try:
    (asyncio.get_event_loop()).run_until_complete(startup())
except KeyboardInterrupt:
    (asyncio.get_event_loop()).run_until_complete(shutdown())
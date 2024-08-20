import json, smtplib, os, openai
import aiosqlite, disnake, security
from email.mime.text import MIMEText
from email.utils import formatdate
from email.headerregistry import Address
from email.mime.multipart import MIMEMultipart
from discord_webhook.webhook import DiscordWebhook
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from googletrans import Translator

embedcolor = 0xff00ff
embedwarning = 0xff9900
embedsuccess = 0x00ff00
embederrorcolor = 0xff0000

cooldown_file = "cooldowns.txt"
smtp_server = security.smtp_server
smtp_user = security.smtp_user
smtp_password = security.smtp_password

def translate_product(df):
    translator = Translator()
    df['Trans_result'] = df['Before_Trans'].apply(lambda x: translator.translate(x, dest='en').text)
    df['Language'] = df['Before_Trans'].apply(lambda x: translator.detect(x).lang)
    return df

openai.api_key = security.OpenAI_api_key

def get_gpt_response(prompt, model):
    try:
        # API 호출
        response = openai.ChatCompletion.create(
            model=model,  # 선택한 모델을 사용합니다.
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # 응답에서 텍스트 추출
        answer = response['choices'][0]['message']['content']
        return answer
    
    except Exception as e:
        return f"오류 발생: {str(e)}"

def generate_image(prompt):
    text = prompt
    translator = Translator()
    result= translator.translate(text, src='ko' ,dest='en')
    translated_text = result.text
    prompt = str(translated_text)
    try:
        # DALL·E API 호출
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",  # 이미지 크기 설정
        )
        
        # 이미지 URL 추출
        image_url = response['data'][0]['url']
        return image_url
    
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 문자 메시지 전송 함수
def send_sms(to, text):
    api_key = security.coolsms_api_key  # API KEY
    api_secret = security.coolsms_api_secret  # API 보안키
    from_ = security.send_number  # 보내는 번호
    type = 'sms'  # 메시지 타입

    params = {
        'type': type,  # 메시지 타입 (sms)
        'to': to,  # 받는 사람 번호
        'from': from_,  # 보내는 사람 번호
        'text': text  # 메시지 내용
    }

    cool = Message(api_key, api_secret)
    try:
        response = cool.send(params)
        print("Success Count : %s" % response['success_count'])
        print("Error Count : %s" % response['error_count'])
        print("Group ID : %s" % response['group_id'])

        if "error_list" in response:
            print("Error List : %s" % response['error_list'])

    except CoolsmsException as e:
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)

def send(username, content, avatar_url, url):
    webhook = DiscordWebhook(url=f'{security.webhook}', content=f'{content}', username=f'{username}', avatar_url=f'{avatar_url}')
    webhook.execute()

async def addstock(_name, _price):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("INSERT INTO stock (name, price) VALUES (?, ?)", (_name, _price))
    await economy_aiodb.commit()
    await aiocursor.close()

async def getstock():
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("SELECT name, price FROM stock")
    data = await aiocursor.fetchall()
    await aiocursor.close()
    return data

async def removestock(_name):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("DELETE FROM stock WHERE name=?", (_name, ))
    await economy_aiodb.commit()
    await aiocursor.close()

async def adduser_stock(user_id, _name, _count):
    # 주식이 존재하는지 확인합니다.
    stocks = await getstock()
    stock_info = next(((name, price) for name, price in stocks if name == _name), None)
    if stock_info is None:
        raise ValueError(f"{_name} 주식은 존재하지 않습니다.")
    else:
        _, stock_price = stock_info
    # 사용자가 충분한 돈을 가지고 있는지 확인합니다.
    user_money = await getmoney(user_id)
    total_price = stock_price * _count
    if user_money < total_price:
        raise ValueError(f"돈이 부족합니다. 필요한 금액: {total_price}, 현재 잔액: {user_money}")
    # 돈을 차감하고 주식을 추가합니다.
    await removemoney(user_id, total_price)
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("INSERT INTO user_stock (id, name, count) VALUES (?, ?, ?)", (user_id, _name, _count))
    await economy_aiodb.commit()
    await aiocursor.close()

async def getuser_stock(user_id):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("SELECT name, count FROM user_stock WHERE id=?", (user_id,))
    data = await aiocursor.fetchall()
    await aiocursor.close()
    return data

async def removeuser_stock(user_id, _name, _count):
    # 주식이 존재하는지 확인합니다.
    stocks = await getstock()
    stock_info = next((price for name, price in stocks if name == _name), None)

    if stock_info is None:
        raise ValueError(f"{_name} 주식은 존재하지 않습니다.")
    else:
        stock_price = stock_info

    # 주식을 판매하고 돈을 지급합니다.
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.cursor()
    await aiocursor.execute("UPDATE user_stock SET count = count - ? WHERE id = ? AND name = ? AND count >= ?", (_count, user_id, _name, _count))
    
    await aiocursor.execute("SELECT count FROM user_stock WHERE id = ? AND name = ?", (user_id, _name))
    new_count = await aiocursor.fetchone()

    # 주식의 개수가 0이면 레코드를 삭제합니다.
    if new_count and new_count[0] == 0:
        await aiocursor.execute("DELETE FROM user_stock WHERE id = ? AND name = ?", (user_id, _name))

    await economy_aiodb.commit()
    await aiocursor.close()

    sell_price = stock_price * _count
    await addmoney(user_id, sell_price)

async def addmoney(_id, _amount):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id,))
    dat = await aiocursor.fetchall()
    if not dat:
        await aiocursor.execute("insert into user (id, money, tos, level, exp, lose_money) values (?, ?, ?, ?, ?, ?)", (_id, _amount, 0, 0, 0, 0))
    else:
        await aiocursor.execute("update user set money = ? where id = ?", (dat[0][1] + _amount, _id))
    await economy_aiodb.commit()
    await aiocursor.close()

async def getmoney(_id):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id, ))
    dat = await aiocursor.fetchall()
    await aiocursor.close()
    if dat == False: return 0
    return dat[0][1]

async def removemoney(_id, _amount):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id, ))
    dat = await aiocursor.fetchall()
    await aiocursor.close()
    if dat == False: return False
    if dat[0][1] < _amount: return False
    aiocursor = await economy_aiodb.execute("update user set money = ? where id = ?", (dat[0][1] - _amount, _id))
    await economy_aiodb.commit()
    await aiocursor.close()
    return True

async def add_lose_money(_id, _amount):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id,))
    dat = await aiocursor.fetchall()
    if not dat:
        await aiocursor.execute("insert into user (id, money, tos, level, exp, lose_money) values (?, ?, ?, ?, ?, ?)", (_id, 0, 0, 0, 0, _amount))
    else:
        await aiocursor.execute("update user set lose_money = ? where id = ?", (dat[0][5] + _amount, _id))
    await economy_aiodb.commit()
    await aiocursor.close()

async def get_lose_money(_id):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id, ))
    dat = await aiocursor.fetchall()
    await aiocursor.close()
    if dat == False: return 0
    return dat[0][5]

async def add_exp(_id, _amount):
    # 데이터베이스 연결
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("SELECT * FROM user WHERE id=?", (_id,))
    dat = await aiocursor.fetchall()

    if not dat:
        # 사용자가 존재하지 않는 경우, 새 사용자 추가
        await aiocursor.execute(
            "INSERT INTO user (id, money, tos, level, exp, lose_money) VALUES (?, ?, ?, ?, ?, ?)", 
            (_id, 30000, 0, 0, _amount, 0)
        )
    else:
        # 사용자가 존재하는 경우, 경험치 업데이트
        current_exp = dat[0][4] if dat[0][4] is not None else 0  # None 체크
        await aiocursor.execute(
            "UPDATE user SET exp = ? WHERE id = ?", 
            (current_exp + _amount, _id)
        )

    # 변경 사항 커밋
    await economy_aiodb.commit()
    await aiocursor.close()
    await economy_aiodb.close()  # 데이터베이스 연결 종료

async def get_exp(_id):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("select * from user where id=?", (_id, ))
    dat = await aiocursor.fetchall()
    await aiocursor.close()
    if dat == False: return 0
    return dat[0][4]

async def dev_deactivate(ctx):
    embed = disnake.Embed(color=embederrorcolor)
    embed.add_field(name="❌ 오류", value=f"개발자에 의해 비활성화된 명령어입니다.\n개발자에게 문의하세요.")
    await ctx.send(embed=embed, ephemeral=True)
    return

async def member_status(ctx):
    economy_aiodb = await aiosqlite.connect("economy.db")
    aiocursor = await economy_aiodb.execute("SELECT tos FROM user WHERE id=?", (ctx.author.id,))
    dbdata = await aiocursor.fetchone()
    await aiocursor.close()
    if dbdata == None:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value=f"{ctx.author.mention}\n가입되지 않은 유저입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    else:
        tos = int(dbdata[0])
        if tos == 1:
            embed = disnake.Embed(color=embederrorcolor)
            embed.add_field(name="❌ 오류", value="이용제한된 유저입니다.")
            await ctx.send(embed=embed, ephemeral=True)
            return
        
async def membership(ctx):
    await member_status(ctx)
    economy_aiodb = await aiosqlite.connect("membership.db")
    aiocursor = await economy_aiodb.execute("SELECT class FROM user WHERE id=?", (ctx.author.id,))
    dbdata = await aiocursor.fetchone()
    
    if dbdata is None:
        # 데이터가 없을 경우 비회원으로 등록
        await economy_aiodb.execute("INSERT INTO user (id, class) VALUES (?, ?)", (ctx.author.id, 0))  # 0: 비회원
        await economy_aiodb.commit()
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="유료 회원만 이용가능한 기능입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    await aiocursor.close()
    member_class = int(dbdata[0])
    
    if member_class == 0: # 0: 비회원
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="유료 회원만 이용가능한 기능입니다.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    elif member_class == 1:  # 1: 회원
        pass
    elif member_class == 2:  # 2: 관리자
        pass
    else:
        embed = disnake.Embed(color=embederrorcolor)
        embed.add_field(name="❌ 오류", value="오류가 발생하였습니다, 개발자에게 문의해주세요.")
        await ctx.send(embed=embed, ephemeral=True)
        return

async def database_create(ctx):
    # 서버 아이디 및 서버 이름 가져오기
    server_id = str(ctx.guild.id)
    # 데이터베이스 생성
    conn = await aiosqlite.connect(f'database\\{server_id}.db')
    # 비동기로 커서를 가져옵니다.
    cursor = await conn.cursor()
    # 이후 쿼리를 실행합니다.
    await cursor.execute(f'CREATE TABLE IF NOT EXISTS 경고 (아이디 INTEGER , 관리자 INTEGER, 맴버 INTEGER, 경고 INTEGER, 사유 INTEGER)')
    await cursor.execute(f'CREATE TABLE IF NOT EXISTS 설정 (공지채널 INTEGER , 처벌로그 INTEGER, 입장로그 INTEGER, 퇴장로그 INTEGER, 인증역할 INTEGER, 인증채널 INTEGER)')
    await conn.commit()
    await conn.close()

def send_email(ctx, recipient, verifycode):
    msg = MIMEMultipart()
    msg['From'] = str(Address("CodeStone", addr_spec=smtp_user))  
    msg['To'] = recipient
    msg['Subject'] = '스톤봇 이메일 인증'
    msg['Date'] = formatdate(localtime=True)

    body = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>CodeStone Email Verify</title>
            <style>
                body {{ background-color: #333; color: #fff; font-family: Arial, sans-serif; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .outer-box {{ background-color: #333; max-width: 2400px; padding: 160px; border: 1px solid #777; box-shadow: 0 0 10px rgba(0, 0, 0, 0.5); }}
                .verification-box {{ background-color: #555; color: #fff; border: 2px solid #777; padding: 20px; text-align: center; max-width: 500px; margin: auto; border-radius: 30px; }}
                .verification-code {{ font-size: 24px; letter-spacing: 5px; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="outer-box">
                <div class="verification-box">
                    <h2>이메일 인증</h2>
                    <p>{ctx.author.name} 님 {ctx.guild.name} 가입 인증을 위한 코드를 입력해주세요.</p>
                    <div class="verification-code">{verifycode}</div>
                    <p>이 코드는 3분 후에 만료됩니다.</p>
                    <p>인증을 요청하지 않았다면, 이 메일을 무시해주세요.</p>
                    <h5>CodeStone 고객지원 +82 10-7460-6675</h5>
                </div>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))  # 'plain' 대신 'html' 사용
    
    server = smtplib.SMTP(smtp_server, 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()

# 쿨다운 정보를 로드하는 함수
def load_cooldowns():
    try:
        with open(cooldown_file, "r") as f:
            try:
                cooldowns = json.load(f)
            except json.JSONDecodeError:
                cooldowns = {}
    except FileNotFoundError:
        cooldowns = {}
    return cooldowns

# 쿨다운 정보를 저장하는 함수
def save_cooldowns(cooldowns):
    with open(cooldown_file, "w") as f:
        json.dump(cooldowns, f)

async def addwarn(ctx, _user, _warn, _reason):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
    if not os.path.exists(db_path):
            await database_create(ctx)
    try:
        aiodb = await aiosqlite.connect(db_path)
        aiocursor = await aiodb.cursor()     # 커서 생성
    except Exception as e:
        print(f"Database connection error: {e}")
        return
    aiocursor = await aiodb.execute("select * from 경고 order by 아이디 desc")
    dat = await aiocursor.fetchone()
    await aiocursor.close()
    if dat is None:
        dat = [0, "asdf"]
    new_id = dat[0] + 1 if dat else 1
    aiocursor = await aiodb.execute("INSERT INTO 경고 (아이디, 관리자, 맴버, 경고, 사유) VALUES (?, ?, ?, ?, ?)", (new_id, ctx.author.id, _user.id, _warn, _reason))
    await aiodb.commit()
    await aiocursor.close()
    aiocursor = await aiodb.execute("SELECT SUM(경고) FROM 경고 WHERE 맴버 = ?", (_user.id,))
    accumulatewarn_result = await aiocursor.fetchone()
    await aiocursor.close()
    accumulatewarn = accumulatewarn_result[0] if accumulatewarn_result and accumulatewarn_result[0] else 0
    embed = disnake.Embed(color=embedsuccess)
    embed.add_field(name="✅경고를 지급했어요", value="", inline=False)
    embed.add_field(name="대상", value=_user.mention)
    embed.add_field(name="누적 경고", value=f"{accumulatewarn} / 10 (+ {_warn})")
    embed.add_field(name="사유", value=_reason, inline=False)
    await ctx.send(embed=embed)
    aiocursor = await aiodb.execute("SELECT 처벌로그 FROM 설정")
    설정_result = await aiocursor.fetchone()
    await aiocursor.close()
    return new_id, accumulatewarn, 설정_result  # 설정_result 추가

async def getwarn(ctx, user):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
    if not os.path.exists(db_path):
        await database_create(ctx)
    aiodb = await aiosqlite.connect(db_path)
    aiocursor = await aiodb.execute(f"SELECT * FROM 경고 WHERE 맴버 = {user.id}")
    dat = await aiocursor.fetchall()
    await aiocursor.close()
    aiocursor = await aiodb.execute("SELECT SUM(경고) FROM 경고 WHERE 맴버 = ?", (user.id,))
    accumulatewarn_result = await aiocursor.fetchone()
    await aiocursor.close()
    accumulatewarn = accumulatewarn_result[0] if accumulatewarn_result and accumulatewarn_result[0] else 0
    return dat, accumulatewarn

async def removewarn(ctx, warn_id):
    db_path = os.path.join(os.getcwd(), "database", f"{ctx.guild.id}.db")
    if not os.path.exists(db_path):
        await database_create(ctx)
    aiodb = await aiosqlite.connect(db_path)
    aiocursor = await aiodb.execute("SELECT * FROM 경고 WHERE 아이디 = ?", (warn_id,))
    dat = await aiocursor.fetchall()
    if not dat:
        return None
    else:
        await aiocursor.execute("DELETE FROM 경고 WHERE 아이디 = ?", (warn_id,))
        await aiodb.commit()  # 변경 사항을 데이터베이스에 확정합니다.
        return warn_id
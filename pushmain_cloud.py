# -*- coding: UTF-8 -*-
import json
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl

# ===================== 配置区 =====================
JSON_PATH = "characters_url.json"
SENDER_EMAIL = "2279134404@qq.com"
EMAIL_PASSWORD = ""
RECEIVER_EMAIL = "hirasawasu@foxmail.com"
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# =============== 邮件正文模板 (Html Css) ===============
EMAIL_CONTENT = {
    'subject': "🎂 今日你推过生日啦~ {character_name} お誕生日おめでとう~",
    
    'header': """
    <html>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f8f5f2;">
            <div style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(to right, #ff9a9e, #66ccff); padding: 25px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: 600; letter-spacing: 1px;"> {character_name} </h1>
                    <p style="margin: 5px 0 0; font-size: 16px; opacity: 0.9;">❤️お誕生日おめでとう~❤️</p>
                </div>
        """,
        
    
    'image_template': """
    <div style="flex: 1; text-align: center; color: #888;">
        <a href="{wiki_link}"><img src="{image_url}" style="max-width: 250px; border-radius: 5px; border: 1px solid #eee;"/></a>
    </div>
    """,
    
    
    'no_image_template': """
    <div style="flex: 1; text-align: center; color: #888;">
        <p>⚠️ 暂无角色图片</p>
    </div>
    """,     
    
    
    'character_template': """
    <div style="background-color: #fff9fa; border-radius: 10px; padding: 20px; margin-bottom: 25px; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                
        <p>{image_content}</p>
        <h2 style="color: #333; margin-top: 0;">今天是来自 <i> {source} </i> 的 {alias} 的生日!</h2>
        <div style="display: flex;">
            <div style="flex: 1;">
                <p><strong>🎂 生日:</strong> {birthday} </p>
                <p><strong>🥰 喜欢程度:</strong> {push_level} </p>
                <p><strong>🔎 来源:</strong> {category} - <i>{source}</i></p>
                <p><strong>📌 人物百科:</strong> {wiki_link} </p>
            </div>
        </div>
    </div>
    """,
    
    
    'reason': """
        <div style="padding: 30px; text-align: center;">
            <p style="font-size: 18px; line-height: 1.6; margin-bottom: 20px; color: #555;">
                {reason}
            </p>
            <p style="font-size: 18px; line-height: 1.6; margin-bottom: 20px; color: #555;">
                让我们为她的诞生献上祝福~
            </p>
        </div>
    """,
    
    
    'footer': """
            <p style="font-size: 18px; line-height: 1.6; margin-bottom: 20px; color: #555; text-align: center;">
                最后，她真是太可爱了！
            </p>
            
            <p><a href="https://github.com/soung2279"><img src="https://i.loli.net/2020/11/14/RpeV19SiDHWKQ4I.png" alt="Soung@Github" style="width: 10%; height: 10%; object-fit: cover; display: block; margin: 0 auto;"></a></p>
            <div style="margin-top: 20px; font-style: italic; font-size: 15px; color: #ff9a9e; font-weight: 500; text-align: center;">
                —— Congratulations from Soung! 🎉
            </div>
            
            <h1 style="color: #ff6b88; border-bottom: 2px solid #ff6b88; padding-bottom: 10px;">
            </h1>
            
            <div style="text-align: center; margin-top: 40px; color: #888; font-size: 0.9em;">
                <p>此邮件由 <i><a href="https://gitee.com/soung2279/anime-chara-birthday-reminder">动漫角色生日提醒推送服务</a></i> 自动发送</p>
                <p>This email is automatically sent by <i><a href="https://gitee.com/soung2279/anime-chara-birthday-reminder">AnimeCharaBirthday-Reminder-Pusher</a></i></p>
                <p>Made by Soung, 2025</p>
                <p></p>
            </div>  
        </div>
        </html>
        """
}

# ==================================================

def find_birthday_characters():
    """查找今天过生日的角色"""
    try:
        # 读取JSON文件
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        today = datetime.now().strftime("%m-%d")
        birthday_chars = []
        
        # 遍历角色数据
        for character in data.get("data", []):
            try:
                # 跳过没有必要数据的项
                if not all(key in character for key in ["birthday", "character_name"]):
                    continue
                
                birthday = character.get("birthday", "").strip()
                
                # 跳过无效数据
                if not birthday or birthday.lower() in ['待补充', '未公布', 'nan', '#value!']:
                    continue
                
                # 统一日期格式
                month_day = normalize_date(birthday)
                if not month_day:
                    continue
                
                if month_day == today:
                    char_name = character.get("character_name", "").strip()
                    image_url = character.get("image_url", "")
                    wiki_link = character.get("wiki_link", "")
                    reason = character.get("reason", "")
                    category = character.get("category", "")
                    alias = character.get("alias", "")
                    push_level = character.get("push_level", "")
                    
                    
                    birthday_chars.append({
                        '角色名': char_name,
                        '生日': birthday,
                        '分类': category,
                        '别名': alias,
                        '推级': push_level,
                        '百科链接': wiki_link,
                        '来源': character.get("source", ""),
                        '图片链接': image_url,
                        '自推原因': reason,
                    })
                    
            except Exception as e:
                print(f"处理角色数据时出错: {e}")
                continue
        
        return birthday_chars
    
    except Exception as e:
        print(f"JSON读取错误: {e}")
        return []

def normalize_date(date_str):
    """统一日期格式为MM-DD"""
    date_str = str(date_str).strip()
    
    try:
        if '月' in date_str and '日' in date_str:
            # 处理 "7月14日" 格式
            month = date_str.split('月')[0].zfill(2)
            day = date_str.split('月')[1].replace('日', '').zfill(2)
            return f"{month}-{day}"
        elif '/' in date_str:
            # 处理 "7/14" 格式
            month, day = date_str.split('/')
            return f"{month.zfill(2)}-{day.zfill(2)}"
        elif '-' in date_str:
            # 处理 "07-14" 格式
            parts = date_str.split('-')
            if len(parts) >= 2:
                return f"{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    except:
        pass
    return None

def build_email_content(characters):
    """使用模板构建邮件HTML内容"""
    if not characters:
        return None
    
    # 将所有角色名合并成一个字符串，用逗号分隔
    all_character_names = "、".join([char['角色名'] for char in characters])
    
    # 使用合并后的所有角色名
    html_content = EMAIL_CONTENT['header'].format(character_name=all_character_names)

    for char in characters:
        if char.get('图片链接'):
            image_content = EMAIL_CONTENT['image_template'].format(
                image_url=char['图片链接'],
                wiki_link=char['百科链接']
            )
        else:
            image_content = EMAIL_CONTENT['no_image_template']
        
        # 添加角色卡片
        html_content += EMAIL_CONTENT['character_template'].format(
            character_name=char['角色名'],
            birthday=char['生日'],
            source=char['来源'],
            alias=char['别名'],
            push_level=char['推级'],
            category=char['分类'],
            wiki_link=char['百科链接'],
            reason=char['自推原因'],
            image_content=image_content
        )
        
        html_content += EMAIL_CONTENT['reason'].format(reason=char['自推原因'])
    
    # 添加页脚
    html_content += EMAIL_CONTENT['footer']
    return html_content

def send_birthday_email(characters):
    """发送生日提醒邮件"""
    if not characters:
        print("没有需要发送的角色")
        return
    
    # 创建邮件对象
    msg = MIMEMultipart('related')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    # 修改邮件主题以包含所有角色名
    all_character_names = "、".join([char['角色名'] for char in characters])
    msg['Subject'] = EMAIL_CONTENT['subject'].format(character_name=all_character_names)
    
    # 构建邮件内容
    html_content = build_email_content(characters)
    html_part = MIMEText(html_content, 'html', 'utf-8')
    
    # 添加HTML内容
    msg.attach(html_part)
    
    # 发送邮件
    try:
        ssl_context = ssl.create_default_context()
        server = None
        try:
            server = smtplib.SMTP_SSL(
                host=SMTP_SERVER,
                port=SMTP_PORT,
                context=ssl_context,
                timeout=30  # 增加超时时间
            )
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            print("✅ 邮件发送成功")
        except smtplib.SMTPException as e:
            # 判断是否是关闭连接时的错误
            if "b'\x00\x00\x00'" in str(e) and "已发送" in str(vars(msg)):
                print("✅ 邮件已成功发送，但关闭连接时出现问题")
            else:
                print(f"SMTP协议错误: {str(e)}")
        except ssl.SSLError as e:
            print(f"SSL连接错误: {str(e)}")
        except Exception as e:
            print(f"邮件发送失败: {e}")
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass  # 忽略关闭连接时的错误
    except Exception as e:
        print(f"创建SMTP连接失败: {e}")

def run_birthday_reminder():
    """主要流程函数，用于执行整个生日提醒逻辑"""
    print("正在查找今天过生日的角色...")
    birthday_chars = find_birthday_characters()
    
    if birthday_chars:
        print("\n找到以下过生日的角色:")
        for char in birthday_chars:
            print(f"\n角色: {char['角色名']}")
            print(f"生日: {char['生日']}")
            print(f"图片链接: {char.get('图片链接') or '未找到'}")

        # 发送邮件
        print("\n正在准备发送邮件...")
        send_birthday_email(birthday_chars)
        return {"status": "success", "message": "邮件已发送", "characters_count": len(birthday_chars)}
    else:
        print("\n今天没有角色过生日")
        return {"status": "success", "message": "今天没有角色过生日", "characters_count": 0}

# 云函数入口函数
def main_handler(event, context):
    """
    云函数入口点
    :param event: 事件触发数据
    :param context: 云函数上下文
    :return: 执行结果
    """
    print("动漫角色生日提醒系统 - 云函数启动")
    
    
    # 执行主逻辑
    result = run_birthday_reminder()
    
    print("云函数执行完毕")
    return result

# 当脚本直接运行时（非云函数环境）执行
if __name__ == "__main__":
    result = run_birthday_reminder()
    print(f"执行结果: {result}")
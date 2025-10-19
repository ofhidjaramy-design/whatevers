import os
import json
import requests
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = os.environ.get('8386577556:AAE7_D-m-NyWXipIEZ3Pl8pNxaFjNpNSI3w')
CHANNEL_ID = os.environ.get('@footballstuffhere')  # مثلاً: @your_channel أو -1001234567890
SUBREDDIT = 'soccer'
POSTS_FILE = 'posted_ids.json'

def load_posted_ids():
    """تحميل قائمة المنشورات المنشورة مسبقاً"""
    try:
        with open(POSTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_posted_ids(posted_ids):
    """حفظ قائمة المنشورات المنشورة"""
    with open(POSTS_FILE, 'w') as f:
        json.dump(posted_ids[-100:], f)  # نحفظ آخر 100 فقط

def get_reddit_posts():
    """جلب أحدث المنشورات من Reddit"""
    url = f'https://www.reddit.com/r/{SUBREDDIT}/new.json?limit=10'
    headers = {'User-Agent': 'TelegramBot/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['data']['children']
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
        return []

def send_to_telegram(post_data):
    """إرسال المنشور إلى Telegram"""
    post = post_data['data']
    
    # تجهيز النص
    title = post['title']
    author = post['author']
    url = f"https://reddit.com{post['permalink']}"
    score = post['score']
    
    message = f"⚽ <b>{title}</b>\n\n"
    message += f"👤 Posted by: u/{author}\n"
    message += f"⬆️ Score: {score}\n"
    message += f"🔗 <a href='{url}'>View on Reddit</a>"
    
    # إرسال الرسالة
    telegram_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    
    # إذا كان هناك صورة، نرسلها
    if post.get('post_hint') == 'image' and post.get('url'):
        image_url = post['url']
        photo_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        photo_payload = {
            'chat_id': CHANNEL_ID,
            'photo': image_url,
            'caption': message,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(photo_url, data=photo_payload)
            return True
        except:
            pass  # إذا فشلت الصورة، نرسل النص فقط
    
    try:
        response = requests.post(telegram_url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print(f"🤖 Bot started at {datetime.now()}")
    print(f"📡 Checking r/{SUBREDDIT}...")
    
    # تحميل المنشورات المنشورة مسبقاً
    posted_ids = load_posted_ids()
    
    # جلب المنشورات الجديدة
    posts = get_reddit_posts()
    
    new_posts_count = 0
    
    for post in reversed(posts):  # نبدأ من الأقدم للأحدث
        post_id = post['data']['id']
        
        # إذا لم يتم نشره من قبل
        if post_id not in posted_ids:
            print(f"📤 Posting: {post['data']['title'][:50]}...")
            
            if send_to_telegram(post):
                posted_ids.append(post_id)
                new_posts_count += 1
                print(f"✅ Posted successfully!")
            else:
                print(f"❌ Failed to post")
    
    # حفظ القائمة المحدثة
    save_posted_ids(posted_ids)
    
    print(f"✨ Done! Posted {new_posts_count} new posts")
    print(f"📊 Total tracked posts: {len(posted_ids)}")

if __name__ == '__main__':
    main()

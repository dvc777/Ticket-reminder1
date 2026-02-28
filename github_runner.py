#!/usr/bin/env python3
import os, json
from datetime import datetime, timedelta
import urllib.request, urllib.parse, ssl

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

TICKET_DATA = {
    'Arsenal': {'vs Bayer Leverkusen (CL H)': {'date': '2026-03-02', 'type': 'Ballot Open', 'time': '12:00 GMT', 'status': 'Starting tomorrow'}},
    'Chelsea': {'vs Newcastle (PL H)': {'date': '2026-02-27', 'type': 'Sale', 'time': '10:00 GMT', 'status': 'Open'}},
    'Man City': {'vs Nottingham Forest (PL H)': {'date': '2026-03-04', 'type': 'Sale', 'time': 'Available', 'status': 'On Sale'}},
    'Newcastle': {'vs Man City (FA Cup A)': {'date': '2026-03-02', 'type': 'Sale', 'time': '10:00 GMT', 'status': 'Starting soon'}},
    'Man Utd': {'vs Crystal Palace (PL H)': {'date': '2026-03-01', 'type': 'Sale', 'time': 'Available', 'status': 'Last tickets'}}
}

def get_today_date(): return datetime.now().strftime('%Y-%m-%d')
def get_tomorrow_date(): return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

def check_activities(date_str):
    activities = []
    for club, matches in TICKET_DATA.items():
        for match, info in matches.items():
            if info['date'] == date_str:
                activities.append({'club': club, 'match': match, 'type': info['type'], 'time': info['time'], 'status': info['status']})
    return activities

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': message}).encode()
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            return json.loads(response.read().decode()).get('ok', False)
    except: return False

def generate_notification():
    today = check_activities(get_today_date())
    tomorrow = check_activities(get_tomorrow_date())
    msg = f"PL Ticket Daily - {datetime.now().strftime('%b %d, %Y')}\nToday:\n"
    msg += '\n'.join([f"  - {a['club']} {a['match']} | {a['type']}" for a in today]) or "  No activities"
    msg += f"\n\nTomorrow:\n"
    msg += '\n'.join([f"  - {a['club']} {a['match']} | {a['type']}" for a in tomorrow]) or "  No activities"
    return msg

if __name__ == '__main__':
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        print("Sending..."); send_telegram_message(generate_notification())
    else: print("Missing credentials")

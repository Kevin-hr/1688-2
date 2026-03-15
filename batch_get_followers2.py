import subprocess
import re
import os
import json
import time

def get_user_followers(username):
    """获取用户粉丝数"""
    url = f"https://urlebird.com/user/{username}/"
    cmd = [
        'curl', '-s', '--max-time', '60',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        '-H', 'Accept-Language: en-US,en;q=0.9',
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=90)
        content = result.stdout.decode('utf-8', errors='ignore')

        # 提取粉丝数
        match = re.search(r'<div class="col-3 p-0"><b>([0-9.,]+[KM]?)</b>', content)
        if match:
            followers = match.group(1)
            return followers
        return "0"
    except Exception as e:
        print(f"Error getting {username}: {e}")
        return "0"

# 需要检查的用户列表
usernames = [
    'kick12__official',
    'nextupfashion',
    'mj_snkrs_',
    'archived.fits19',
    'flame.reps',
    'oopbuy620',
    'you1stlondon',
    'originalparadigms',
    'kick12.com_',
    'jordan_lawson',
    'prcmaker',
    'kicks.sverige',
    'mothershipsg',
    'nat_hearn'
]

base_path = r'C:\Users\52648\Documents\GitHub\1688-2'

print("=== Fetching user followers ===")
results = []

for username in usernames:
    print(f"Checking @{username}...", end=" ", flush=True)
    followers = get_user_followers(username)
    print(f"{followers} followers")
    results.append({
        'username': username,
        'followers': followers,
        'url': f"https://urlebird.com/user/{username}/"
    })
    time.sleep(1)

# 保存
with open(os.path.join(base_path, 'user_followers.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved to user_followers.json")

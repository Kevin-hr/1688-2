import subprocess
import re
import json
import time
import os

def get_user_detail(username):
    """获取用户详细信息"""
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

        # 提取各项数据
        data = {'username': username, 'url': url}

        # 粉丝数
        match = re.search(r'<div class="col-3 p-0"><b>([0-9.,]+[KM]?)</b>.*?<span class="user">followers</span>', content, re.DOTALL)
        data['followers'] = match.group(1) if match else "0"

        # 平均播放量
        match = re.search(r'Average views per video:.*?<b>([0-9.,]+[KM]?)</b>', content)
        data['avg_views'] = match.group(1) if match else "0"

        # 平均点赞
        match = re.search(r'Average hearts per video:.*?<b>([0-9.,]+[KM]?)</b>', content)
        data['avg_likes'] = match.group(1) if match else "0"

        # 平均评论
        match = re.search(r'Average comments per video:.*?<b>([0-9.,]+[KM]?)</b>', content)
        data['avg_comments'] = match.group(1) if match else "0"

        # 平均分享
        match = re.search(r'Average shares per video:.*?<b>([0-9.,]+[KM]?)</b>', content)
        data['avg_shares'] = match.group(1) if match else "0"

        # 视频数
        match = re.search(r'<div class="col-3 p-0"><b>([0-9.,]+[KM]?)</b>.*?<span class="user">videos</span>', content, re.DOTALL)
        data['video_count'] = match.group(1) if match else "0"

        # 描述
        match = re.search(r'<meta name="description" content="([^"]+)"', content)
        data['description'] = match.group(1)[:150] if match else ""

        # 互动率
        match = re.search(r'engagement rate.*?<b>([0-9.,]+%)', content)
        data['engagement_rate'] = match.group(1) if match else "N/A"

        return data
    except Exception as e:
        return {'username': username, 'error': str(e)}

# 需要获取详细数据的账号
usernames = [
    'kick12__official',
    'kick12.com_',
    'jordan_lawson',
    'kicks.sverige',
    'mothershipsg',
    'nat_hearn',
    'originalparadigms',
    'you1stlondon',
    'kalundatheplug',
    'nicekicks',
    'sneakernews',
    'complex',
    'prcmaker'
]

base_path = r'C:\Users\52648\Documents\GitHub\1688-2'

print("=== Getting detailed stats ===\n")
results = []

for username in usernames:
    print(f"Fetching @{username}...", flush=True)
    data = get_user_detail(username)
    print(f"  Followers: {data.get('followers', 'N/A')}, Avg Views: {data.get('avg_views', 'N/A')}")
    results.append(data)
    time.sleep(1)

# 保存结果
with open(os.path.join(base_path, 'reps_influencers_detail.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n=== Results ===")
for r in results:
    print(f"\n@{r['username']}")
    print(f"  Followers: {r.get('followers', 'N/A')}")
    print(f"  Avg Views: {r.get('avg_views', 'N/A')}")
    print(f"  Avg Likes: {r.get('avg_likes', 'N/A')}")
    print(f"  Avg Comments: {r.get('avg_comments', 'N/A')}")
    print(f"  Avg Shares: {r.get('avg_shares', 'N/A')}")
    print(f"  Videos: {r.get('video_count', 'N/A')}")
    print(f"  Engagement: {r.get('engagement_rate', 'N/A')}")
    print(f"  Description: {r.get('description', 'N/A')[:80]}")

print(f"\n\nSaved to reps_influencers_detail.json")

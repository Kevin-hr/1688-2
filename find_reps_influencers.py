import subprocess
import re
import json
import time
import os

def get_user_stats(username):
    """获取用户统计数据"""
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
        followers_match = re.search(r'<div class="col-3 p-0"><b>([0-9.,]+[KM]?)</b>.*?<span class="user">followers</span>', content, re.DOTALL)
        # 提取平均播放量
        avg_views_match = re.search(r'Average views per video:.*?<b>([0-9.,]+[KM]?)</b>', content)
        # 提取描述
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
        # 提取视频数
        videos_match = re.search(r'<div class="col-3 p-0"><b>([0-9.,]+[KM]?)</b>.*?<span class="user">videos</span>', content, re.DOTALL)
        # 提取点赞数
        likes_match = re.search(r'<li class="mt-1">.*?(\d+\.\d+K|\d+K|\d+M).*?likes', content)

        followers = followers_match.group(1) if followers_match else "0"
        avg_views = avg_views_match.group(1) if avg_views_match else "0"
        description = desc_match.group(1) if desc_match else ""
        videos = videos_match.group(1) if videos_match else "0"
        likes = likes_match.group(1) if likes_match else "0"

        return {
            'username': username,
            'followers': followers,
            'avg_views': avg_views,
            'videos': videos,
            'likes_per_video': likes,
            'description': description[:100] if description else "",
            'url': url
        }
    except Exception as e:
        return {
            'username': username,
            'followers': "0",
            'avg_views': "0",
            'videos': "0",
            'likes_per_video': "0",
            'description': "",
            'url': url,
            'error': str(e)
        }

# 所有待检查的账号列表
usernames = [
    # 之前验证过的
    'kick12__official',
    'kick12.com_',
    'jordan_lawson',
    'kicks.sverige',
    'mothershipsg',
    'nat_hearn',
    'originalparadigms',
    'you1stlondon',
    # 新找到的
    'nic4timezz',
    'bg2trim',
    'wizzfashionwrld',
    'yunshoestore',
    'kalundatheplug',
    'sunnymanufacturer',
    # 更多鞋类账号
    'sneakerhead',
    'sneakershop',
    'kicksdaily',
    'shoe collection',
    'jordanretail',
    ' hypebeast',
    'sneakerfile',
    'kicksonfire',
    'complex',
    'nicekicks',
    'sneakernews',
]

base_path = r'C:\Users\52648\Documents\GitHub\1688-2'

print("=== Searching for REPS influencers ===\n")
results = []

for username in usernames:
    print(f"Checking @{username}...", flush=True)
    stats = get_user_stats(username)
    print(f"  Followers: {stats['followers']}, Avg Views: {stats['avg_views']}")
    results.append(stats)
    time.sleep(1)

# 筛选符合条件：100万粉丝以上 + 10万播放量以上
def parse_number(s):
    """将 K/M 转换为数字"""
    s = s.replace(',', '')
    if 'M' in s:
        return float(s.replace('M', '')) * 1000000
    elif 'K' in s:
        return float(s.replace('K', '')) * 1000
    else:
        try:
            return float(s)
        except:
            return 0

qualified = []
for r in results:
    followers = parse_number(r['followers'])
    avg_views = parse_number(r['avg_views'])
    if followers >= 1000000 and avg_views >= 100000:
        qualified.append(r)

print(f"\n=== Qualified (1M+ followers, 100K+ views) ===")
for q in qualified:
    print(f"@{q['username']} - {q['followers']} followers, {q['avg_views']} avg views")

print(f"\n=== All Results (sorted by followers) ===")
results.sort(key=lambda x: parse_number(x['followers']), reverse=True)
for r in results:
    print(f"@{r['username']} - {r['followers']} followers, {r['avg_views']} avg views, {r.get('description', '')[:50]}")

# 保存结果
with open(os.path.join(base_path, 'reps_influencers.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'qualified': qualified,
        'all': results
    }, f, ensure_ascii=False, indent=2)

print(f"\nTotal qualified: {len(qualified)}")
print("Results saved to reps_influencers.json")

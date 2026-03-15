import re
import os
import json

def extract_users_from_file(filepath):
    """从HTML文件中提取用户信息"""
    users = []
    if not os.path.exists(filepath):
        return users

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取用户链接和粉丝数
    # 匹配模式: <a href="https://urlebird.com/user/xxx/">@xxx</a> 和粉丝数
    user_pattern = r'<a href="https://urlebird\.com/user/([^/]+)/"[^>]*>@([^<]+)</a>'
    follower_pattern = r'<span class="followers">([0-9.,]+)\s*followers?</span>'

    user_matches = re.findall(user_pattern, content)
    follower_matches = re.findall(follower_pattern, content)

    for i, (user_path, username) in enumerate(user_matches):
        follower_count = follower_matches[i] if i < len(follower_matches) else "0"
        users.append({
            'username': username,
            'path': user_path,
            'url': f"https://urlebird.com/user/{user_path}/",
            'followers_raw': follower_count
        })

    return users

# 从所有搜索文件中提取用户
base_path = r'C:\Users\52648\Documents\GitHub\1688-2'
search_files = [
    'search_reps.html',
    'search_sneakers.html',
    'search_jordan.html',
    'search_PK.html',
    'search_kicks.html'
]

all_users = {}
for filename in search_files:
    filepath = os.path.join(base_path, filename)
    users = extract_users_from_file(filepath)
    for user in users:
        all_users[user['username']] = user

# 打印所有用户
print("=== All extracted users ===")
for username, user in sorted(all_users.items(), key=lambda x: x[1]['followers_raw'], reverse=True):
    print(f"@{user['username']} - {user['followers_raw']} followers - {user['url']}")

print(f"\nTotal: {len(all_users)} users")

# 保存
with open(os.path.join(base_path, 'all_users.json'), 'w', encoding='utf-8') as f:
    json.dump(all_users, f, ensure_ascii=False, indent=2)

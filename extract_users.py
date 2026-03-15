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

# 搜索关键词文件
search_files = {
    'reps': 'search_reps.html',
    'sneakers': 'search_sneakers.html',
    'jordan': 'search_jordan.html',
    'PK': 'search_PK.html'
}

base_path = r'C:\Users\52648\Documents\GitHub\1688-2'

all_users = {}
for keyword, filename in search_files.items():
    filepath = os.path.join(base_path, filename)
    users = extract_users_from_file(filepath)
    print(f"\n=== {keyword.upper()} ({len(users)} users) ===")
    for user in users[:10]:
        print(f"  @{user['username']} - {user['followers_raw']} followers")
        all_users[user['username']] = user

# 保存所有用户
with open(os.path.join(base_path, 'all_users.json'), 'w', encoding='utf-8') as f:
    json.dump(all_users, f, ensure_ascii=False, indent=2)

print(f"\n\nTotal unique users: {len(all_users)}")
print("Saved to all_users.json")

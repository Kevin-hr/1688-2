
import requests
import os
import json
from dotenv import load_dotenv

def get_categories():
    load_dotenv()
    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    
    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    url = "https://api-seller.ozon.ru/v2/category/tree"
    payload = {
        "language": "EN"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return
            
        data = response.json()
        
        # 打印前 5 个顶级类目
        categories = data.get("result", [])
        print(f"Total top categories: {len(categories)}")
        
        # 寻找包含 "Pet" 或 "Toy" 的类目
        found = []
        def search_tree(tree, query):
            for item in tree:
                name = item.get("title", "").lower()
                if query.lower() in name:
                    found.append(f"{item.get('category_id')}: {item.get('title')}")
                if item.get("children"):
                    search_tree(item["children"], query)
        
        search_tree(categories, "Pet")
        search_tree(categories, "Toy")
        
        print("\nFound categories:")
        for f in found[:20]:
            print(f)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_categories()

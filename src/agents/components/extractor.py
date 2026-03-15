# -*- coding: utf-8 -*-
"""
数据提取模块 (Extractor)
-----------------------
负责从 HTML 页面内容中解析和提取结构化数据 (Hybrid Parsing: JSON + BeautifulSoup)。
"""

from bs4 import BeautifulSoup
import re
import json

class Extractor:
    """
    提取器类 (Hybrid Parsing 实现)
    """
    
    def parse_product_detail(self, page_content: str, url: str) -> dict:
        """
        从页面内容中解析商品详情。
        """
        print(f"Extractor: 正在解析内容...")
        
        # 策略 A: 尝试从 JSON 数据中提取 (数据层采集)
        json_data = self._extract_json_data(page_content)
        if json_data:
            print("Extractor: ✅ 成功提取到 JSON 数据，使用数据层采集模式。")
            return self._parse_from_json(json_data, url)
            
        # 策略 B: 降级到 DOM 解析 (视觉层采集)
        print("Extractor: ⚠️ 未找到 JSON 数据，降级到 DOM 解析模式。")
        return self._parse_from_dom(page_content, url)

    def _extract_json_data(self, html: str):
        """正则提取 window.__INIT_DATA 或 __PRELOADED_STATE__"""
        try:
            # 模式 1: window.__INIT_DATA = {...}
            match = re.search(r'window\.__INIT_DATA\s*=\s*({.+?});', html, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # 模式 2: __PRELOADED_STATE__
            match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.+?});', html, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
        except json.JSONDecodeError:
            print("Extractor: JSON 解析失败")
        except Exception as e:
            print(f"Extractor: 正则提取异常 - {e}")
        return None

    def _parse_from_json(self, data: dict, url: str) -> dict:
        """从 JSON 对象中解析字段"""
        try:
            # 尝试适配多种 JSON 结构
            offer = data.get('globalData', {}).get('offerModel', {})
            if not offer:
                offer = data.get('data', {}).get('offer', {})
            if not offer:
                # 兼容性处理：如果是 AI 提取的结构化数据
                offer = data
                
            title = offer.get('subject') or offer.get('title', '未知标题')
            
            # 价格处理
            price_info = offer.get('price', {}).get('discountPrice', {})
            price = str(price_info.get('value', '0.00')) if price_info else '0.00'
            
            # 图片
            images = offer.get('image', {}).get('images', [])
            images = [img if img.startswith('http') else f"https:{img}" for img in images]
            
            # 属性
            attributes = {}
            sku_props = offer.get('productAttribute', {}).get('skuProperty', [])
            for p in sku_props:
                key = p.get('name')
                val = p.get('value')
                if key and val:
                    attributes[key] = val
                    
            description = offer.get('detail', {}).get('description', '')
            
            return {
                "title": title,
                "url": url,
                "price": price,
                "images": images[:10],
                "attributes": attributes,
                "description": description[:500]
            }
        except Exception as e:
            print(f"Extractor: JSON 结构解析失败 - {e}")
            return {"title": "Error Parsing JSON"}

    def _parse_from_dom(self, page_content: str, url: str) -> dict:
        """DOM 解析逻辑"""
        soup = BeautifulSoup(page_content, 'html.parser')
        
        title = self._extract_title(soup)
        price = self._extract_price(soup)
        images = self._extract_images(soup)
        attributes = self._extract_attributes(soup)
        description = self._extract_description(soup)
        
        return {
            "title": title,
            "url": url,
            "price": price,
            "images": images,
            "attributes": attributes,
            "description": description
        }

    # ... (辅助方法保持不变)
    def _extract_title(self, soup):
        selectors = ["h1.title-text", ".d-title", ".title-info", "meta[property='og:title']"]
        for sel in selectors:
            if "meta" in sel:
                tag = soup.select_one(sel)
                if tag and tag.get("content"): return tag["content"].strip()
            else:
                tag = soup.select_one(sel)
                if tag: return tag.get_text(strip=True)
        return "未知标题"

    def _extract_price(self, soup):
        meta_price = soup.select_one("meta[property='og:product:price:amount']")
        if meta_price and meta_price.get("content"): return meta_price["content"]
        selectors = [".price-text", ".discount-price", ".price-original-sku .value", ".ref-price"]
        for sel in selectors:
            tag = soup.select_one(sel)
            if tag: return tag.get_text(strip=True)
        return "0.00"

    def _extract_images(self, soup):
        images = []
        img_tags = soup.select(".tab-content-container img") or soup.select(".detail-gallery-img") or soup.select(".swipe-pane img")
        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if src:
                if "32x32" in src or ".svg" in src: continue
                if src.startswith("//"): src = "https:" + src
                src = re.sub(r'\.jpg_.*', '.jpg', src)
                src = re.sub(r'\.png_.*', '.png', src)
                if src not in images: images.append(src)
        return images[:10]

    def _extract_attributes(self, soup):
        attrs = {}
        items = soup.select(".offer-attr-item") or soup.select(".obj-content tr")
        for item in items:
            name_tag = item.select_one(".offer-attr-item-name") or item.select_one("td.name")
            value_tag = item.select_one(".offer-attr-item-value") or item.select_one("td.value")
            if name_tag and value_tag:
                key = name_tag.get_text(strip=True).rstrip("：:")
                val = value_tag.get_text(strip=True)
                attrs[key] = val
        return attrs

    def _extract_description(self, soup):
        desc_tag = soup.select_one("#detail-content-container") or soup.select_one(".desc-lazy-load-container")
        if desc_tag: return desc_tag.get_text(strip=True)[:500]
        return ""

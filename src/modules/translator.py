# -*- coding: utf-8 -*-
try:
    import translators as ts
    _HAS_TRANSLATORS = True
except ImportError:
    _HAS_TRANSLATORS = False

import time
import random

class Translator:
    """翻译工具类"""
    
    def __init__(self):
        self._available = _HAS_TRANSLATORS
        
    def translate_to_ru(self, text):
        """
        翻译文本为俄语
        
        Args:
            text (str): 待翻译文本
            
        Returns:
            str: 翻译后的文本
        """
        if not text:
            return ""
            
        if not self._available:
            print("警告: translators库未安装，无法翻译")
            return text
            
        try:
            # 使用google翻译引擎，增加重试机制
            # ts.translate_text API: query_text, to_language, translator
            result = ts.translate_text(text, to_language='ru', translator='google')
            # 简单的防风控延时
            time.sleep(random.uniform(0.5, 1.5))
            return result
        except Exception as e:
            print(f"翻译失败 (中->俄): {e}")
            return text
            
    def translate_to_en(self, text):
        """
        翻译文本为英语
        
        Args:
            text (str): 待翻译文本
            
        Returns:
            str: 翻译后的文本
        """
        if not text:
            return ""
            
        if not self._available:
            print("警告: translators库未安装，无法翻译")
            return text
            
        try:
            result = ts.translate_text(text, to_language='en', translator='google')
            time.sleep(random.uniform(0.5, 1.5))
            return result
        except Exception as e:
            print(f"翻译失败 (中->英): {e}")
            return text

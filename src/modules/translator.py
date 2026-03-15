<<<<<<< HEAD
"""
翻译模块 - 多引擎翻译支持（中→俄/英）
"""

from typing import Optional, Dict


class Translator:
    """
    多引擎翻译器

    支持 Google/Bing/Baidu 多引擎回退
    """

    def __init__(self):
        """初始化翻译器"""
        self._cache: Dict[str, str] = {}
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """检查翻译库是否可用"""
        try:
            import translators
            return True
        except ImportError:
            print("[Translator] 警告: 'translators' 库未安装，翻译功能不可用")
            print("         安装: pip install translators")
            return False

    def translate(
        self,
        text: str,
        from_lang: str = "zh",
        to_lang: str = "ru"
    ) -> str:
        """
        翻译文本

        Args:
            text: 待翻译文本
            from_lang: 源语言代码
            to_lang: 目标语言代码

        Returns:
            翻译后的文本
        """
        if not self._available:
            return f"[需安装translators库] {text}"

        if not text or not text.strip():
            return text

        # 检查缓存
        cache_key = f"{from_lang}|{to_lang}|{text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        import translators as ts

        # 多引擎回退
        engines = ["google", "bing", "baidu", "deepl"]
        for engine in engines:
            try:
                result = ts.translate_text(
                    text,
                    translator=engine,
                    from_language=from_lang,
                    to_language=to_lang,
                )
                if result and result.strip():
                    self._cache[cache_key] = result.strip()
                    return result.strip()
            except Exception:
                continue

        # 全部失败
        return f"[翻译失败] {text}"

    def translate_to_ru(self, text: str) -> str:
        """翻译为俄文"""
        return self.translate(text, "zh", "ru")

    def translate_to_en(self, text: str) -> str:
        """翻译为英文"""
        return self.translate(text, "zh", "en")

    def translate_batch(self, texts: list, to_lang: str = "ru") -> list:
        """
        批量翻译

        Args:
            texts: 文本列表
            to_lang: 目标语言

        Returns:
            翻译后的文本列表
        """
        return [self.translate(t, "zh", to_lang) for t in texts]

    def clear_cache(self):
        """清空翻译缓存"""
        self._cache.clear()


# 全局单例
_default_translator: Optional[Translator] = None


def get_translator() -> Translator:
    """获取全局翻译器实例"""
    global _default_translator
    if _default_translator is None:
        _default_translator = Translator()
    return _default_translator


# 便捷函数
def translate(text: str, to_lang: str = "ru") -> str:
    """快速翻译函数"""
    return get_translator().translate(text, "zh", to_lang)


def translate_to_ru(text: str) -> str:
    """快速翻译为俄文"""
    return translate(text, "ru")


def translate_to_en(text: str) -> str:
    """快速翻译为英文"""
    return translate(text, "en")


if __name__ == "__main__":
    # 测试
    translator = Translator()

    test_texts = [
        "猫咪玩具",
        "逗猫棒羽毛玩具",
        "高品质宠物用品",
    ]

    print("翻译测试:")
    for text in test_texts:
        ru = translator.translate_to_ru(text)
        en = translator.translate_to_en(text)
        print(f"原文: {text}")
        print(f"俄文: {ru}")
        print(f"英文: {en}")
        print()
=======
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
>>>>>>> release/v1.3.3-hotfix

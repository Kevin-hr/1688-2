"""
标题清洗模块 - 清洗1688商品标题中的营销垃圾词
"""

import re
from typing import List


class TitleCleaner:
    """
    1688 标题清洗器

    去除营销垃圾词（爆款/一件代发/包邮等）
    """

    # 1688 标题中常见的营销垃圾词
    BUZZWORDS = [
        # 销售话术
        "厂家直销", "一件代发", "批发", "工厂直销", "源头直供",
        "爆款", "爆爆款", "超级爆款", "抖音爆款", "网红款",
        "热销", "热卖", "畅销", "好评如潮", "超值",
        "特价", "限时特价", "秒杀价", "清仓", "亏本价",
        # 品质描述（夸张）
        "高品质", "超高品质", "精品", "顶级", "奢华",
        "超耐用", "超耐咬", "超大", "加大", "大号",
        # 快递/发货
        "包邮", "顺丰包邮", "三天达", "次日达", "极速发货",
        # 其他
        "新款", "新品", "2024年新款", "2025年新款", "2026年新款",
        "跨境", "出口款", "外贸款", "OEM", "ODM",
        "可定制", "支持定制", "可印logo", "可印LOGO",
        "买1发2", "买二发三", "买3发5",
    ]

    def __init__(self, buzzwords: List[str] = None, max_length: int = 200):
        """
        初始化

        Args:
            buzzwords: 自定义垃圾词列表（追加到默认列表）
            max_length: 标题最大长度
        """
        self.max_length = max_length
        self.buzzwords = set(self.BUZZWORDS)
        if buzzwords:
            self.buzzwords.update(buzzwords)

    def clean(self, title: str) -> str:
        """
        清洗标题

        Args:
            title: 原始标题

        Returns:
            清洗后的标题
        """
        if not title:
            return "Untitled Product"

        cleaned = title

        # 批量替换垃圾词
        for word in self.buzzwords:
            cleaned = cleaned.replace(word, "")

        # 清理括号内容（通常包含营销信息）
        cleaned = re.sub(r'[\[\]【】()（）]', " ", cleaned)

        # 压缩空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 截断
        if len(cleaned) > self.max_length:
            cleaned = cleaned[:self.max_length]

        # 如果太短，用原标题截断
        if len(cleaned) < 5:
            cleaned = title[:self.max_length]

        return cleaned

    def is_clean(self, title: str) -> bool:
        """检查标题是否需要清洗"""
        for word in self.buzzwords:
            if word in title:
                return False
        return True

    def count_buzzwords(self, title: str) -> int:
        """统计标题中的垃圾词数量"""
        count = 0
        for word in self.buzzwords:
            count += title.count(word)
        return count


# 便捷函数
def clean_title(title: str, max_length: int = 200) -> str:
    """快速清洗函数"""
    return TitleCleaner(max_length=max_length).clean(title)


if __name__ == "__main__":
    # 测试
    cleaner = TitleCleaner()

    test_cases = [
        "超耐咬爆款猫咪静音球一件代发批发包邮",
        "高品质工厂直销宠物玩具2026年新款",
        "普通商品名称",
        "买1发2限时特价网红款",
    ]

    for title in test_cases:
        cleaned = cleaner.clean(title)
        buzzword_count = cleaner.count_buzzwords(title)
        print(f"原文: {title}")
        print(f"清洗: {cleaned} (移除{buzzword_count}个垃圾词)")
        print()

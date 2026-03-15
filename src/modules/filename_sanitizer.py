"""
文件名清洗模块 - 清洗文件名中的非法字符
"""

import re
from typing import Optional


class FilenameSanitizer:
    """
    清洗文件名中的非法字符，确保跨平台可用

    Windows 不允许: \ / * ? : " < > |
    Windows 保留名: CON, PRN, AUX, NUL, COM1-9, LPT1-9
    """

    # Windows 非法字符
    ILLEGAL_CHARS = r'[\\/*?:"<>|]'

    # Windows 保留名（不区分大小写）
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
    }

    def __init__(self, max_length: int = 200):
        """
        初始化

        Args:
            max_length: 文件名最大长度
        """
        self.max_length = max_length

    def sanitize(self, filename: str) -> str:
        """
        清洗文件名

        Args:
            filename: 原始文件名

        Returns:
            清洗后的文件名
        """
        if not filename:
            return "unnamed"

        # 替换非法字符为空
        cleaned = re.sub(self.ILLEGAL_CHARS, "", filename)

        # 移除多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 检测 Windows 保留名（如 NUL, CON, PRN 等）
        name_without_ext = cleaned.split('.')[0].upper()
        if name_without_ext in self.RESERVED_NAMES:
            cleaned = f"file_{cleaned}"

        # 截断长度
        if len(cleaned) > self.max_length:
            cleaned = cleaned[:self.max_length]

        return cleaned if cleaned else "unnamed"

    def sanitize_for_windows(self, filename: str) -> str:
        """Windows 专用清洗（更严格）"""
        # 移除更多字符
        cleaned = re.sub(r'[\\\/*?:"<>|]', "", filename)
        # 移除控制字符
        cleaned = re.sub(r'[\x00-\x1f\x7f]', "", cleaned)
        # 移除空格开头结尾
        cleaned = cleaned.strip()
        return cleaned if cleaned else "unnamed"


# 便捷函数
def sanitize(filename: str, max_length: int = 200) -> str:
    """快速清洗函数"""
    return FilenameSanitizer(max_length).sanitize(filename)


if __name__ == "__main__":
    # 测试
    test_cases = [
        '测试商品<>:"/\\|*?',
        '商品/名称\\with*special?chars',
        'A' * 300,  # 超长
        '  前后空格  ',
        '正常文件名',
    ]

    sanitizer = FilenameSanitizer()
    for case in test_cases:
        result = sanitizer.sanitize(case)
        print(f"'{case}' -> '{result}'")

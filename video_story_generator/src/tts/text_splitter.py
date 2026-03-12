"""
文本分句模块
职责：将长文本按标点符号分割为句子片段
"""
import re


def split_text_by_sentences(text, min_length=5):
    """
    将文本按中/英文句号、问号、感叹号及换行符分割。

    Args:
        text: 完整文本
        min_length: 最短句子长度（过短的会被过滤）

    Returns:
        句子列表
    """
    sentences = re.split(r'[。！？\n]', text)
    return [s.strip() for s in sentences if len(s.strip()) > min_length]

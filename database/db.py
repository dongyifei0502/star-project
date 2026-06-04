# -*- coding: utf-8 -*-
# SQLite 情绪记录数据库封装模块

import sqlite3  # 使用 Python 标准库 sqlite3
import os  # 用于处理路径相关逻辑

# 数据库文件路径：当前脚本所在目录下的 emotions.db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emotions.db")

# 允许的情绪类型集合，用于校验
VALID_EMOTIONS = frozenset({"anger", "sad", "anxious", "neutral"})


def get_db_connection():
    """
    建立数据库连接，返回 connection 对象。
    使用 row_factory 使查询结果可通过列名访问。
    """
    try:
        # 连接 SQLite 数据库文件（不存在时会自动创建）
        connection = sqlite3.connect(DB_PATH)
        # 设置行工厂，便于将行转为字典
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        # 连接失败时抛出明确错误信息
        raise RuntimeError(f"无法连接数据库 {DB_PATH}: {e}") from e


def init_db():
    """
    初始化数据库：若 records 表不存在则创建。
    程序启动时应调用一次。
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # 创建 records 表，emotion 字段限制为四种合法值之一
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                positive_text TEXT NOT NULL,
                emotion TEXT NOT NULL CHECK (
                    emotion IN ('anger', 'sad', 'anxious', 'neutral')
                ),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise RuntimeError(f"初始化数据库失败: {e}") from e
    finally:
        if connection:
            connection.close()


def save_record(original, positive, emotion):
    """
    插入一条新记录。

    参数:
        original: 用户输入的原始负面文字
        positive: 转换后的正面表达
        emotion: 情绪分类，必须是 anger/sad/anxious/neutral 之一

    返回:
        新插入记录的 id（整数）
    """
    # 校验情绪类型
    if emotion not in VALID_EMOTIONS:
        raise ValueError(
            f"无效的情绪类型: {emotion}，必须是 {sorted(VALID_EMOTIONS)} 之一"
        )

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO records (original_text, positive_text, emotion)
            VALUES (?, ?, ?)
            """,
            (original, positive, emotion),
        )
        connection.commit()
        # 返回自增主键 id
        return cursor.lastrowid
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise RuntimeError(f"保存记录失败: {e}") from e
    finally:
        if connection:
            connection.close()


def get_all_records():
    """
    查询所有记录，按 id 倒序（最新在前）。

    返回:
        记录列表，每条记录为包含所有字段的字典
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, original_text, positive_text, emotion, created_at
            FROM records
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        # 将 Row 对象转为普通字典列表
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise RuntimeError(f"查询所有记录失败: {e}") from e
    finally:
        if connection:
            connection.close()


def get_stats():
    """
    统计每种情绪类型的数量。

    返回:
        字典，例如 {'anger': 3, 'sad': 5, 'anxious': 2, 'neutral': 1}
        没有记录的情绪类型计数为 0
    """
    # 先初始化四种情绪的计数为 0
    stats = {emotion: 0 for emotion in sorted(VALID_EMOTIONS)}
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT emotion, COUNT(*) AS count
            FROM records
            GROUP BY emotion
            """
        )
        for row in cursor.fetchall():
            stats[row["emotion"]] = row["count"]
        return stats
    except sqlite3.Error as e:
        raise RuntimeError(f"统计情绪数量失败: {e}") from e
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # 以下为模块自测代码
    try:
        print("=== 初始化数据库 ===")
        init_db()
        print("数据库初始化完成。\n")

        print("=== 插入测试数据 ===")
        id1 = save_record(
            "我今天又搞砸了，什么都做不好",
            "今天遇到了挑战，我正在从中学到经验",
            "sad",
        )
        id2 = save_record(
            "凭什么总是我吃亏，太不公平了",
            "我可以表达自己的感受，并寻找更公平的解决方式",
            "anger",
        )
        print(f"插入记录 id: {id1}, {id2}\n")

        print("=== 所有记录（按 id 倒序）===")
        records = get_all_records()
        for record in records:
            print(record)
        print()

        print("=== 情绪统计 ===")
        stats = get_stats()
        print(stats)

    except (ValueError, RuntimeError) as e:
        print(f"测试运行出错: {e}")

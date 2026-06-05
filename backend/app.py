from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加数据库模块的路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import save_record, get_stats

app = Flask(__name__)
CORS(app)

@app.route('/api/transform', methods=['POST'])
def transform():
    data = request.get_json()
    text = data.get('text', '')
    
    # 关键词匹配规则
    if '烦' in text:
        positive = "烦心事是成长的信号，你在前进"
        emotion = "sad"
    elif '累' in text:
        positive = "你的努力值得被看见，休息一下再出发"
        emotion = "sad"
    elif '气' in text or '怒' in text:
        positive = "情绪在提醒你重视自己，这是力量"
        emotion = "anger"
    elif '哭' in text or '难受' in text:
        positive = "允许自己感受，雨后会有新的开始"
        emotion = "anxious"
    else:
        positive = "你的感受很重要，宇宙在倾听"
        emotion = "neutral"
    
    # 保存记录到数据库
    try:
        save_record(text, positive, emotion)
        print(f"已保存记录: {text} -> {positive}")
    except Exception as e:
        print(f"保存记录失败: {e}")
    
    return jsonify({
        'positive': positive,
        'emotion': emotion
    })

@app.route('/api/records', methods=['GET'])
def get_records():
    """获取所有情绪记录（用于数据看板）"""
    from database.db import get_all_records
    records = get_all_records()
    return jsonify({'records': records})

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取情绪统计（用于数据看板）"""
    stats = get_stats()
    return jsonify({'stats': stats})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
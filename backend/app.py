from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/transform', methods=['POST'])
def transform():
    data = request.get_json()
    text = data.get('text', '')
    
    # 如果 text 是 bytes，解码成字符串
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    
    print(f"收到文字原始类型: {type(text)}")
    print(f"收到文字: {text}")
    print(f"文字repr: {repr(text)}")
    
    # 尝试多种判断方式
    has_fan = '烦' in text
    has_fan2 = '烦' in str(text)
    
    print(f"直接判断'烦' in text: {has_fan}")
    print(f"str判断: {has_fan2}")
    
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
    
    print(f"返回: {positive} / {emotion}")
    
    return jsonify({'positive': positive, 'emotion': emotion})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
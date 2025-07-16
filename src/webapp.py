from flask import Flask, render_template, request, jsonify, Response
import services.chat_service as chat_service
import services.signal_service as signal_service
import utils.deepseek as deepseek
import json,os
app = Flask(__name__)

# ===============网页显示显示===============
@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    return render_template('admin.html')

@app.route('/danger_signals')
def danger_signals():
    return render_template('danger_signals.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/user_operations')
def user_operations():
    return render_template('user_operations.html')

@app.route('/client_chat')
def client_chat():
    return render_template('client_chat.html')
# ==========================================

#危险数据接收与处理
@app.route('/api/receive', methods=['POST'])
def receive_data():
    data = request.json
    signal_service.add_signal(data)
    return jsonify({"status": "success"})

#危险数据获取
@app.route('/api/signals', methods=['GET'])
def get_signals():
    return jsonify(signal_service.get_signals())


#聊天功能
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'response': "请输入有效的信息。"})
    try:
        result = chat_service.process_message(user_message)
        #将历史记录转换为字符串
        history_str = ""
        for i in chat_service.get_chat_history():
            history_str += i['role'] + ":" + i['content'] + "\n"
        #危机处理
        if json.loads(result)['type'] == 'dangerous':
            signal_service.add_dangerous_chat("测试ID", user_message, deepseek.dangerAnayze(history_str))
        return jsonify({'response': json.loads(result)['message']})
    #异常处理
    except Exception as e:
        print(f"Error in chat API: {str(e)}")
        return jsonify({'response': "抱歉，处理您的消息时出现错误，请稍后重试。"})

# 流式聊天功能
@app.route('/api/stream_chat', methods=['POST'])
def stream_chat_api():
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'response': "请输入有效的信息。"})
    
    def generate():
        try:
            # 将历史记录转换为字符串
            history_str = ""
            for i in chat_service.get_chat_history():
                history_str += i['role'] + ":" + i['content'] + "\n"
            
            # 处理流式响应
            for chunk in chat_service.process_stream_message(user_message):
                try:
                    # 尝试解析JSON
                    if isinstance(chunk, str):
                        json_data = json.loads(chunk)
                    else:
                        json_data = chunk
                        
                    # 检查是否是危险内容
                    if json_data.get('type') == 'dangerous':
                        signal_service.add_dangerous_chat("测试ID", user_message, deepseek.dangerAnayze(history_str))
                    
                    # 只发送message字段的内容
                    if 'message' in json_data:
                        yield f"data: {json.dumps({'chunk': json_data['message']})}\n\n"
                    else:
                        # 如果没有message字段，发送原始内容
                        yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接发送文本
                    yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                except Exception as e:
                    print(f"Error processing chunk: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error in stream chat API: {str(e)}")
            yield f"data: {json.dumps({'error': '抱歉，处理您的消息时出现错误，请稍后重试。'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/save_history', methods=['GET'])
def save_chat_history():
    """
    保存历史记录到文件
    由于水平有限，本项目没有注意代码复用，编写较为随意。本函数无法指定路径。
    """
    history = chat_service.get_chat_history()
    try:
        signal_service.save_signals_to_file()
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            #indent:缩进以使格式美观 0,2,4等级可选
            json.dump(history, f, ensure_ascii=False, indent=4)
        return jsonify({'status': 'success', 'message': '聊天记录已保存'}), 200
    except Exception as e:
        print(f'保存聊天记录时出错: {str(e)}')
        return jsonify({'status': 'error', 'message': '保存聊天记录时出错，请稍后重试'}), 500
    
@app.route('/api/del_history',methods=['GET'])
def del_history():
    """
    删除程序中的历史记录(不保存更改)
    由于水平有限，本项目没有注意代码复用，编写较为随意。本函数无法指定路径。
    """
    try:
        chat_service.delete_chat_history()
        return jsonify({'status': 'success', 'message': '已经删了'}), 200
    except Exception as e:
        print(f'删除聊天记录时出错: {str(e)}')
        return jsonify({'status': 'error', 'message': '删除聊天记录时出错，请稍后重试'}), 500
@app.route('/api/analyze',methods=['GET'])
def analyze():
    """
    用户话题喜好分析，为聊天策略服务
    """
    try:
        history_str = ""
        for i in chat_service.get_chat_history():
            history_str += i['role'] + ":" + i['content'] + "\n"
        result = deepseek.preferenceAnayze(history_str)
        result = json.loads(result)
        with open('preference.json','w',encoding='utf-8') as f:
            json.dump(obj=result,fp=f)
        return jsonify({'status': 'success', 'message': '已经分析完毕并保存到文件'}), 200
    except Exception as e:
        print(f'出错: {str(e)}')
        return jsonify({'status': 'error', 'message': '出错，请稍后重试'}), 500

def load_history():
    """
    启动时加载历史记录和历史喜好
    """
    global pre
    pre = {}
    if os.path.exists('preference.json'):
        with open('preference.json','r',encoding='utf-8') as f:
            pre = json.load(fp=f)
            print("已载入喜好:",pre)
    else:
        print("还没保存过喜好记录")
    if os.path.exists('chat_history,'):
        with open('chat_history.json','r',encoding='utf-8') as f:
            try:
                history = json.load(f)
                chat_service.write_chat_history(history,pre)
                print("历史记录加载成功!")
            except Exception as e:
                print("错误:"+str(e))
    else: print("还没保存过历史记录")
if __name__ == '__main__':
    load_history()
    signal_service.load_signals_from_file()
    print("Luminest 工作坊网页版启动，")
    # debug=True 代码更改时重载服务器，蛮有用
    app.run(port=5000,debug=True)
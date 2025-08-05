from flask import Flask, render_template, request, jsonify, Response
from src.services.coze_chat_service import CozeChatService
from src.services.signalService import SignalService
from src.services.analysisService import DeepseekAnalysisService
import json
import os

class WebApp:
    """Luminest Web应用"""
    
    def __init__(self):
        """初始化Web应用"""
        self.app = Flask(__name__)
        self.chat_service = CozeChatService()
        self.signal_service = SignalService()
        self.analysis_service = DeepseekAnalysisService()
        self.preferences = {}
        self._setup_routes()
        
    def _setup_routes(self):
        """设置路由"""
        # 页面路由
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/dashboard', 'dashboard', self.dashboard)
        self.app.add_url_rule('/danger_signals', 'danger_signals', self.danger_signals)
        self.app.add_url_rule('/chat', 'chat_page', self.chat_page)
        self.app.add_url_rule('/user_operations', 'user_operations', self.user_operations)
        self.app.add_url_rule('/client_chat', 'client_chat', self.client_chat)
        
        # API路由
        self.app.add_url_rule('/api/receive', 'receive_data', self.receive_data, methods=['POST'])
        self.app.add_url_rule('/api/signals', 'get_signals', self.get_signals, methods=['GET'])
        self.app.add_url_rule('/api/chat', 'chat_api', self.chat_api, methods=['POST'])
        self.app.add_url_rule('/api/stream_chat', 'stream_chat_api', self.stream_chat_api, methods=['POST'])
        self.app.add_url_rule('/api/save_history', 'save_chat_history', self.save_chat_history, methods=['GET'])
        self.app.add_url_rule('/api/del_history', 'del_history', self.del_history, methods=['GET'])
        self.app.add_url_rule('/api/analyze', 'analyze', self.analyze, methods=['GET'])
        
    # 页面路由处理
    def index(self):
        return render_template('admin.html')
        
    def dashboard(self):
        return render_template('admin.html')
        
    def danger_signals(self):
        return render_template('danger_signals.html')
        
    def chat_page(self):
        return render_template('chat.html')
        
    def user_operations(self):
        return render_template('user_operations.html')
        
    def client_chat(self):
        return render_template('client_chat.html')

#危险数据接收与处理
    # API路由处理
    def receive_data(self):
        """处理接收到的危险数据"""
        data = request.json
        self.signal_service.add_signal(data)
        return jsonify({"status": "success"})
        
    def get_signals(self):
        """获取所有危险信号"""
        return jsonify(self.signal_service.get_signals())
        
    def chat_api(self):
        """处理聊天请求"""
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({'response': "请输入有效的信息。"})
            
        try:
            result = self.chat_service.process_message(user_message)
            result_dict = json.loads(result)
            
            if result_dict['type'] == 'dangerous':
                # 获取历史记录并转换为字符串
                history = self.chat_service.get_chat_history()
                history_str = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
                
                # 进行危险分析
                analysis = self.analysis_service.analyze_danger(history)
                self.signal_service.add_dangerous_chat("测试ID", user_message, analysis)
                
            return jsonify({'response': result_dict['message']})
            
        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            return jsonify({'response': "抱歉，处理您的消息时出现错误，请稍后重试。"})

    def stream_chat_api(self):
        """处理流式聊天请求"""
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({'response': "请输入有效的信息。"})
        
        def generate():
            try:
                # 获取历史记录
                history = self.chat_service.get_chat_history()
                history_str = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
                
                # 处理流式响应
                for chunk in self.chat_service.process_stream_message(user_message):
                    try:
                        # 解析响应
                        json_data = chunk if isinstance(chunk, dict) else json.loads(chunk)
                        
                        # 检查是否是危险内容
                        if json_data.get('type') == 'dangerous':
                            analysis = self.analysis_service.analyze_danger(history)
                            self.signal_service.add_dangerous_chat("测试ID", user_message, analysis)
                        
                        # 发送响应
                        if 'message' in json_data:
                            yield f"data: {json.dumps({'chunk': json_data['message']})}\n\n"
                        else:
                            yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                            
                    except json.JSONDecodeError:
                        yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                    except Exception as e:
                        print(f"Error processing chunk: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error in stream chat API: {str(e)}")
                yield f"data: {json.dumps({'error': '抱歉，处理您的消息时出现错误，请稍后重试。'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')

    def save_chat_history(self):
        """保存历史记录到文件"""
        try:
            # 保存聊天历史
            self.chat_service.save_chat_history()
            # 保存信号
            self.signal_service.save_signals()
            return jsonify({'status': 'success', 'message': '聊天记录已保存'}), 200
        except Exception as e:
            print(f'保存聊天记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '保存聊天记录时出错，请稍后重试'}), 500
    
    def del_history(self):
        """删除历史记录"""
        try:
            self.chat_service.delete_chat_history()
            return jsonify({'status': 'success', 'message': '已经删了'}), 200
        except Exception as e:
            print(f'删除聊天记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '删除聊天记录时出错，请稍后重试'}), 500
            
    def analyze(self):
        """分析用户喜好"""
        try:
            # 获取历史记录
            history = self.chat_service.get_chat_history()
            history_str = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
            
            # 分析喜好
            result = self.analysis_service.analyze_preferences(history)
            
            # 保存分析结果
            with open('preference.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            return jsonify({'status': 'success', 'message': '已经分析完毕并保存到文件'}), 200
        except Exception as e:
            print(f'分析用户喜好时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '分析用户喜好时出错，请稍后重试'}), 500
            
    def _load_preferences(self):
        """加载用户喜好"""
        try:
            if os.path.exists('preference.json'):
                with open('preference.json', 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
                    print("已载入喜好:", self.preferences)
            else:
                print("还没保存过喜好记录")
        except Exception as e:
            print(f"加载用户喜好时出错: {str(e)}")
            self.preferences = {}
            
    def _load_history(self):
        """加载聊天历史和信号"""
        self.chat_service.load_chat_history()
        self.signal_service.load_signals()
        self._load_preferences()
        if self.preferences:
            self.chat_service.update_user_preferences(self.preferences)
            
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web应用"""
        self._load_history()
        print("Luminest 工作坊网页版启动")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """创建并配置Web应用"""
    webapp = WebApp()
    return webapp
    
    
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
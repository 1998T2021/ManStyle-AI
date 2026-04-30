
## 📄 backend/app.py (核心入口)

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from config.config import get_config
from utils.database import init_db
from api.routes import register_routes
from services.weather_service import WeatherService
from ai.outfit_generator import OutfitGenerator
import logging

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化配置
config = get_config()
app.config.update(config)

# 初始化数据库
init_db(app)

# 初始化服务
weather_service = WeatherService(config['weather_api_key'])
outfit_generator = OutfitGenerator()

# 注册路由
register_routes(app)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/status', methods=['GET'])
def system_status():
    """系统状态检查"""
    return jsonify({
        'database': 'connected' if init_db(app) else 'disconnected',
        'ai_models': 'loaded' if outfit_generator.is_ready() else 'loading',
        'weather_service': 'active' if weather_service.is_available() else 'inactive'
    })

if __name__ == '__main__':
    app.run(
        host=config.get('host', '0.0.0.0'),
        port=config.get('port', 5000),
        debug=config.get('debug', True)
    )
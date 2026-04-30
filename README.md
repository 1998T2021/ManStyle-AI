# ManStyle AI 🤵‍♂️

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18.x-blue)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-20.x-blue)](https://docker.com)

## 专为男生打造的智能电子衣柜系统

**解决核心痛点**：男生不会穿搭、不会买衣服、衣柜利用率低、搭配决策困难

### ✨ 核心功能

🚀 **智能衣物识别** - 拍照自动识别衣物款型、颜色、材质、风格等20+属性，准确率达92%+

🎯 **个性化搭配推荐** - 基于用户身材数据、天气、场合、个人风格，生成3套专业级搭配方案

🛒 **精准购物推荐** - 根据搭配缺口，智能推荐淘宝/京东/拼多多高性价比单品，置信度超85%

📱 **虚拟试穿体验** - 3D建模技术，预览搭配效果，避免踩雷

📊 **衣柜健康管理** - 智能分析衣柜利用率，提醒单品淘汰，优化购物决策

---

## 🚀 快速开始

### 前置条件
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- MySQL 8.0

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/manstyle-ai.git
cd manstyle-ai

# 启动后端服务
cd backend
pip install -r requirements.txt
python app.py

# 启动前端服务
cd ../frontend
npm install
npm run dev


## 📄 scripts/setup.sh (初始化脚本)

```bash
#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}       ManStyle AI 安装脚本              ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}检查系统依赖...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到Python 3，请先安装Python 3.10+${NC}"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: 未找到Node.js，请先安装Node.js 18+${NC}"
        exit 1
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}警告: 未找到Docker，部分功能将受限${NC}"
        echo -e "${YELLOW}建议安装Docker以获得最佳体验${NC}"
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}错误: 未找到Git，请先安装Git${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 依赖检查通过${NC}"
}

# 创建虚拟环境
setup_python_venv() {
    echo -e "${YELLOW}设置Python虚拟环境...${NC}"
    
    cd backend
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装额外的AI依赖
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    cd ..
    
    echo -e "${GREEN}✓ Python虚拟环境设置完成${NC}"
}

# 安装前端依赖
setup_frontend() {
    echo -e "${YELLOW}安装前端依赖...${NC}"
    
    cd frontend
    npm install
    
    # 构建生产版本
    npm run build
    
    cd ..
    
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
}

# 配置环境变量
setup_env() {
    echo -e "${YELLOW}配置环境变量...${NC}"
    
    # 检查是否存在.env文件
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${YELLOW}已创建.env文件，请根据实际情况修改配置${NC}"
    fi
    
    # 检查是否存在config/config.yaml
    if [ ! -f "config/config.yaml" ]; then
        mkdir -p config
        cp config/config.example.yaml config/config.yaml
        echo -e "${YELLOW}已创建配置文件，请根据实际情况修改${NC}"
    fi
    
    echo -e "${GREEN}✓ 环境变量配置完成${NC}"
}

# 初始化数据库
init_database() {
    echo -e "${YELLOW}初始化数据库...${NC}"
    
    cd backend
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行数据库迁移
    python -m flask db init
    python -m flask db migrate
    python -m flask db upgrade
    
    # 加载种子数据
    python -c "from app import create_app; from scripts.seed_data import seed_database; app = create_app(); with app.app_context(): seed_database()"
    
    cd ..
    
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
}

# 下载预训练模型
download_models() {
    echo -e "${YELLOW}下载预训练AI模型...${NC}"
    
    mkdir -p ai_models/clothing_detection
    mkdir -p ai_models/color_analysis
    mkdir -p ai_models/recommendation
    
    # 这里需要替换为实际的模型下载链接
    echo -e "${YELLOW}注意: 请手动下载预训练模型或训练自己的模型${NC}"
    echo -e "${YELLOW}模型下载链接将通过邮件发送给贡献者${NC}"
    
    echo -e "${GREEN}✓ 模型目录创建完成${NC}"
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}运行测试套件...${NC}"
    
    cd backend
    source venv/bin/activate
    pytest -v
    cd ..
    
    cd frontend
    npm test
    cd ..
    
    echo -e "${GREEN}✓ 测试运行完成${NC}"
}

# 启动服务
start_services() {
    echo -e "${YELLOW}启动服务...${NC}"
    
    if command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}使用Docker Compose启动服务...${NC}"
        docker-compose up -d
    else
        echo -e "${YELLOW}使用本地方式启动服务...${NC}"
        
        # 启动后端
        cd backend
        source venv/bin/activate
        flask run --host=0.0.0.0 --port=5000 &
        BACKEND_PID=$!
        cd ..
        
        # 启动前端
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo -e "${YELLOW}后端服务PID: $BACKEND_PID${NC}"
        echo -e "${YELLOW}前端服务PID: $FRONTEND_PID${NC}"
    fi
    
    echo -e "${GREEN}✓ 服务启动完成${NC}"
    echo -e "${GREEN}访问地址: http://localhost:3000${NC}"
}

# 主函数
main() {
    check_dependencies
    setup_python_venv
    setup_frontend
    setup_env
    init_database
    download_models
    run_tests
    start_services
    
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${GREEN}       ManStyle AI 安装完成！            ${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${YELLOW}接下来你可以：${NC}"
    echo -e "  1. 访问 http://localhost:3000 使用应用"
    echo -e "  2. 查看文档：docs/README.md"
    echo -e "  3. 贡献代码：请阅读 docs/CONTRIBUTING.md"
    echo -e "  4. 报告问题：提交GitHub Issue"
    echo -e "${BLUE}=========================================${NC}"
}

# 执行主函数
main "$@"

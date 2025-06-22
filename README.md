# B站NLP分析系统

一个基于FastAPI和Vue.js的B站用户评论分析系统，支持用户评论爬取、情感分析和数据可视化。

## 功能特性

- 🔐 用户认证系统（注册/登录）
- 📊 B站视频评论数据爬取
- 🤖 用户评论情感分析
- 📈 数据可视化展示
- 📝 查询历史记录管理
- 🔄 异步任务处理（Redis队列）
- 🗄️ 向量数据库存储

## 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **Redis** - 缓存和任务队列
- **Milvus** - 向量数据库
- **Kafka** - 消息队列
- **JWT** - 用户认证
- **Bilibili API** - B站数据爬取

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

## 项目结构

```
bilibili_NLP/
├── backend/                 # 后端代码
│   ├── routers/            # API路由
│   ├── database.py         # 数据库操作
│   ├── bilibili.py         # B站API封装
│   ├── vector_db.py        # 向量数据库操作
│   ├── kafka_producer.py   # Kafka生产者
│   └── main.py             # 主应用入口
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # 状态管理
│   │   └── router/        # 路由配置
│   └── package.json
├── requirements.txt        # Python依赖
└── README.md
```

## 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis
- MySQL/PostgreSQL
- Kafka (可选)

### 后端设置

1. 创建虚拟环境：
```bash
python -m venv python3.12_env
source python3.12_env/bin/activate  # Linux/Mac
# 或
python3.12_env\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息
```

4. 运行后端服务：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 运行开发服务器：
```bash
npm run dev
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要API端点

### 用户认证
- `POST /user/register` - 用户注册
- `POST /user/login` - 用户登录

### 数据分析
- `GET /api/select/{BV}` - 获取视频评论数据
- `POST /api/user/analysis/{uid}` - 提交用户分析任务
- `GET /api/job/status/{job_id}` - 获取任务状态
- `GET /api/history` - 获取查询历史

## 开发指南

### 代码规范
- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 使用类型注解

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请通过Issue联系。 
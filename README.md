# MoneyTree - 金融知识学习Agent

一个对话式金融知识私教，通过知识树 + 教学对话 + 验证机制，帮助用户系统性地学习金融知识。

## 核心功能

- **知识树规划**：输入学习目标，AI自动规划知识点依赖关系图
- **对话式教学**：用生活比喻、具体数字讲解抽象金融概念，支持 Markdown/Mermaid 图表渲染
- **解释验证**：教学完成后要求用户用自己的话解释，通过才能解锁下一节点
- **投资日记**：记录买入/卖出/定投操作及决策理由
- **学习护照**：可视化学习进度总览

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + Python |
| 数据库 | MySQL (pymysql) |
| 前端 | 原生 HTML/CSS/JS |
| AI | OpenAI 兼容接口 |
| 渲染 | markdown-it + mermaid.js |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API key 和数据库配置

# 3. 创建数据库
mysql -u root -e "CREATE DATABASE moneytree;"
mysql -u root moneytree < schema.sql

# 4. 下载前端依赖
curl -sL "https://cdn.jsdelivr.net/npm/markdown-it@14.0.0/dist/markdown-it.min.js" -o frontend/js/markdown-it.min.js
curl -sL "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" -o frontend/js/mermaid.min.js

# 5. 启动
python run.py
# 访问 http://localhost:8000
```

## 知识树状态机

```
locked → unlocked → learned → verified
  🔒        📖         ⏳        ✅
```

- **locked**：前置依赖未完成
- **unlocked**：可以开始学习
- **learned**：教学完成，等待验证
- **verified**：验证通过，解锁下游节点

## 项目结构

```
MoneyTree/
├── backend/
│   ├── app.py              # FastAPI 应用
│   ├── db.py               # 数据库连接
│   ├── llm.py              # LLM 调用封装
│   ├── prompts/            # 三种 LLM prompt
│   │   ├── planner.py      # 知识树规划
│   │   ├── teacher.py      # 教学对话
│   │   └── verifier.py     # 验证评判
│   ├── routers/            # API 路由
│   └── services/           # 业务逻辑
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/                 # 前端交互
├── tests/                  # 单元测试
├── run.py                  # 启动入口
└── requirements.txt
```

## License

MIT

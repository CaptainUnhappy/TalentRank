# TalentRank 开发者评估系统

## 项目简介
TalentRank 是一个基于 GitHub 数据的开发者评估系统，通过分析开发者的项目贡献和影响力，为开发者提供客观的技术能力评分。

## 核心功能
1. TalentRank 评分计算
   - 项目重要度评估
     * Star 数量权重: 40%
     * Fork 数量权重: 30%
     * Watcher 数量权重: 30%
     
   - 开发者贡献度分析
     * 代码提交数量: 30%
     * Issue 解决数量: 25%
     * PR 质量评估: 25%
     * 代码评审参与度: 20%
     
   - 综合评分算法
     * 最终得分 = (项目重要度 * 0.4 + 开发者贡献度 * 0.6) * 活跃度系数

2. 开发者画像
   - Nation 识别与推断
   - 技术领域分类
   - 开发者信息聚合

3. 搜索与筛选
   - 按领域搜索
   - 按地区筛选
   - 评分排序

## 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/talentrank.git
cd talentrank
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件并添加以下配置：

```bash
# GitHub API Token（必需）
GITHUB_TOKEN=your_github_token

# MongoDB 配置（可选，默认使用本地MongoDB）
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=talentrank

# API 服务配置（可选）
API_HOST=0.0.0.0
API_PORT=8000

# 缓存配置（可选）
CACHE_TTL=3600
```

### 5. 初始化数据库
```bash
# 创建必要的数据库索引
python scripts/create_indexes.py
```

### 6. 启动服务
```bash
# 开发模式启动
uvicorn src.api.main:app --reload

# 生产模式启动
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## API 使用说明
API 文档将自动生成在：
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
### 1. 分析开发者
```bash
GET /api/v1/developers/{username}
```

参数：
- `username`: GitHub 用户名
- `force_refresh`: 是否强制刷新缓存（可选，默认false）

### 2. 搜索开发者
```bash
GET /api/v1/search
```

参数：
- `domain`: 技术领域（可选）
- `nation`: 国家/地区（可选）
- `min_rank`: 最低评分（可选）
- `limit`: 返回结果数量（默认20）
- `offset`: 分页偏移量（默认0）

### 3. 获取统计信息
```bash
GET /api/v1/stats
```

## 技术架构
- 后端：Python + FastAPI
- 数据库：MongoDB
- 数据采集：GitHub API + PyGithub
- 数据分析：pandas, numpy
- AI 模型：OpenAI API (用于开发者信息分析)

## 项目结构
```
talentrank/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py           # FastAPI 应用入口
│   ├── data/
│   │   ├── __init__.py
│   │   └── github_collector.py  # GitHub 数据采集
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── domain_classifier.py # 技术领域分类
│   │   └── nation_predictor.py  # 国家/地区推断
│   ├── ranking/
│   │   ├── __init__.py
│   │   └── score_calculator.py  # 评分计算
│   ├── services/
│   │   ├── __init__.py
│   │   └── developer_analyzer.py # 开发者分析服务
│   └── config.py             # 配置文件
├── tests/
│   ├── __init__.py
│   ├── test_score_calculator.py
│   ├── test_nation_predictor.py
│   └── test_domain_classifier.py
├── scripts/
│   ├── create_indexes.py     # 创建数据库索引
│   └── update_cache.py       # 更新缓存数据
├── requirements.txt
├── README.md
└── .env.example
```

## 注意事项

1. GitHub API 限流：
   - 未认证用户：60次/小时
   - 认证用户：5000次/小时

2. 数据缓存：
   - 默认缓存时间：1小时
   - 可通过 force_refresh 参数强制刷新

3. 评分说明：
   - 评分范围：0-100
   - 更新频率：每天
```

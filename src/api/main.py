from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from datetime import datetime, timedelta

from ..services.developer_analyzer import DeveloperAnalyzer, DeveloperAnalysis
from ..config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('talentrank.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TalentRank API",
    description="GitHub开发者评估系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
db = None

@app.on_event("startup")
async def startup_db_client():
    """
    启动时初始化数据库连接
    """
    global db
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    关闭时断开数据库连接
    """
    if db:
        db.client.close()
        logger.info("数据库连接已关闭")

# 依赖注入
def get_analyzer():
    return DeveloperAnalyzer(settings.github_token)

# API 模型
class DeveloperResponse(BaseModel):
    username: str
    talent_rank: float
    nation: str
    nation_confidence: float
    domains: dict
    profile: dict
    last_updated: datetime

class SearchResponse(BaseModel):
    total: int
    developers: List[DeveloperResponse]

class StatsResponse(BaseModel):
    total_developers: int
    nations: List[str]
    domains: List[str]
    avg_rank: float

# API 路由
@app.get("/api/v1/developers/{username}", response_model=DeveloperResponse)
async def analyze_developer(
    username: str,
    force_refresh: bool = False,
    analyzer: DeveloperAnalyzer = Depends(get_analyzer)
):
    """
    分析指定开发者的完整信息
    
    参数:
    - username: GitHub用户名
    - force_refresh: 是否强制刷新缓存数据
    """
    try:
        # 检查缓存
        if not force_refresh:
            cached_data = await db.developers.find_one({"username": username})
            if cached_data and (datetime.now() - cached_data["last_updated"]) < timedelta(seconds=settings.cache_ttl):
                logger.info(f"返回缓存数据: {username}")
                return DeveloperResponse(**cached_data)
        
        # 分析开发者数据
        logger.info(f"开始分析开发者: {username}")
        analysis = await analyzer.analyze_developer(username)
        
        # 转换为可序列化的字典
        developer_data = {
            "username": analysis.username,
            "talent_rank": analysis.talent_rank,
            "nation": analysis.nation,
            "nation_confidence": analysis.nation_confidence,
            "domains": analysis.domains,
            "profile": analysis.profile.__dict__,
            "last_updated": analysis.last_updated
        }
        
        # 更新数据库
        await db.developers.update_one(
            {"username": username},
            {"$set": developer_data},
            upsert=True
        )
        
        logger.info(f"开发者分析完成: {username}")
        return DeveloperResponse(**developer_data)
        
    except Exception as e:
        logger.error(f"分析开发者失败 {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/search", response_model=SearchResponse)
async def search_developers(
    domain: Optional[str] = Query(None, description="技术领域"),
    nation: Optional[str] = Query(None, description="国家/地区"),
    min_rank: Optional[float] = Query(None, ge=0, le=100, description="最低评分"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    offset: int = Query(0, ge=0, description="分页偏移量")
):
    """
    搜索开发者
    支持按领域、国家和最低评分筛选
    """
    try:
        # 构建查询条件
        query = {}
        if domain:
            query[f"domains.{domain}"] = {"$exists": True}
        if nation:
            query["nation"] = nation
        if min_rank is not None:
            query["talent_rank"] = {"$gte": min_rank}
            
        # 执行查询
        total = await db.developers.count_documents(query)
        cursor = db.developers.find(query) \
            .sort("talent_rank", -1) \
            .skip(offset) \
            .limit(limit)
            
        # 收集结果
        developers = []
        async for doc in cursor:
            developers.append(DeveloperResponse(**doc))
            
        logger.info(f"搜索完成: 找到 {total} 个开发者")
        return SearchResponse(
            total=total,
            developers=developers
        )
        
    except Exception as e:
        logger.error(f"搜索开发者失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_statistics():
    """
    获取系统统计信息
    """
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_rank": {"$avg": "$talent_rank"},
                "total": {"$sum": 1}
            }}
        ]
        
        stats = await db.developers.aggregate(pipeline).next()
        nations = await db.developers.distinct("nation")
        domains = await db.developers.distinct("domains")
        
        logger.info("统计信息获取成功")
        return StatsResponse(
            total_developers=stats["total"],
            nations=nations,
            domains=list(domains.keys()),
            avg_rank=stats["avg_rank"]
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局错误: {str(exc)}")
    return {
        "error": str(exc),
        "path": request.url.path,
        "timestamp": datetime.now().isoformat()
    }

# 健康检查
@app.get("/health")
async def health_check():
    """
    系统健康检查
    """
    try:
        await db.command("ping")
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Unavailable") 
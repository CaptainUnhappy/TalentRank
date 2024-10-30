from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..data.github_collector import GitHubDataCollector, DeveloperProfile
from ..ranking.score_calculator import TalentRankCalculator, ProjectMetrics, DeveloperMetrics
from ..analysis.nation_predictor import NationPredictor
from ..analysis.domain_classifier import DomainClassifier

@dataclass
class DeveloperAnalysis:
    username: str
    talent_rank: float
    nation: str
    nation_confidence: float
    domains: Dict[str, float]
    profile: DeveloperProfile
    last_updated: datetime

class DeveloperAnalyzer:
    """
    开发者分析服务
    整合评分计算、国家推断和领域分类功能
    """
    
    def __init__(self, github_token: str):
        self.collector = GitHubDataCollector(github_token)
        self.rank_calculator = TalentRankCalculator()
        self.nation_predictor = NationPredictor()
        self.domain_classifier = DomainClassifier()
    
    async def analyze_developer(self, username: str) -> DeveloperAnalysis:
        """
        分析开发者并生成完整报告
        """
        # 获取开发者基础信息
        profile = await self.collector.get_developer_profile(username)
        
        # 计算 TalentRank
        talent_rank = await self._calculate_talent_rank(username, profile.repositories)
        
        # 推断国家/地区
        network_locations = await self._collect_network_locations(profile)
        nation, confidence = self.nation_predictor.predict_nation(
            profile.location,
            network_locations
        )
        
        # 分析技术领域
        repositories = await self._collect_repository_details(profile.repositories)
        contributions = await self._collect_contributions(username, profile.repositories)
        domains = self.domain_classifier.classify_domains(repositories, contributions)
        
        return DeveloperAnalysis(
            username=username,
            talent_rank=talent_rank,
            nation=nation,
            nation_confidence=confidence,
            domains=domains,
            profile=profile,
            last_updated=datetime.now()
        )
    
    async def _calculate_talent_rank(self, username: str, repositories: List[str]) -> float:
        """
        计算开发者的 TalentRank 分数
        """
        total_project_score = 0
        total_contribution_score = 0
        repo_count = 0
        
        for repo_name in repositories:
            # 获取仓库指标
            metrics = await self.collector.get_repository_metrics(repo_name)
            project_metrics = ProjectMetrics(
                stars=metrics['stars'],
                forks=metrics['forks'],
                watchers=metrics['watchers']
            )
            
            # 获取贡献指标
            contributions = await self.collector.get_developer_contributions(username, repo_name)
            developer_metrics = DeveloperMetrics(
                commits=contributions['commits_count'],
                resolved_issues=contributions['resolved_issues'],
                pull_requests=contributions['pull_requests'],
                code_reviews=contributions['code_reviews']
            )
            
            # 计算得分
            project_score = self.rank_calculator.calculate_project_importance(project_metrics)
            contribution_score = self.rank_calculator.calculate_developer_contribution(developer_metrics)
            
            total_project_score += project_score
            total_contribution_score += contribution_score
            repo_count += 1
        
        if repo_count == 0:
            return 0
            
        # 计算平均分
        avg_project_score = total_project_score / repo_count
        avg_contribution_score = total_contribution_score / repo_count
        
        # 计算活跃度系数
        activity_factor = self._calculate_activity_factor(repositories)
        
        return self.rank_calculator.calculate_final_score(
            avg_project_score,
            avg_contribution_score,
            activity_factor
        )
    
    async def _collect_network_locations(self, profile: DeveloperProfile) -> List[str]:
        """
        收集开发者关系网络中的位置信息
        """
        locations = []
        
        # 收集关注者的位置信息
        for follower in profile.followers:
            follower_profile = await self.collector.get_developer_profile(follower)
            if follower_profile.location:
                locations.append(follower_profile.location)
        
        # 收集正在关注的用户的位置信息
        for following in profile.following:
            following_profile = await self.collector.get_developer_profile(following)
            if following_profile.location:
                locations.append(following_profile.location)
                
        return locations
    
    async def _collect_repository_details(self, repositories: List[str]) -> List[Dict]:
        """
        收集仓库详细信息
        """
        details = []
        for repo_name in repositories:
            metrics = await self.collector.get_repository_metrics(repo_name)
            details.append(metrics)
        return details
    
    async def _collect_contributions(self, username: str, repositories: List[str]) -> List[Dict]:
        """
        收集贡献信息
        """
        contributions = []
        for repo_name in repositories:
            contrib = await self.collector.get_developer_contributions(username, repo_name)
            contributions.append(contrib)
        return contributions
    
    def _calculate_activity_factor(self, repositories: List[str]) -> float:
        """
        计算活跃度系数
        基于最近的活动频率计算
        """
        # 简单实现，可以根据需求调整计算方法
        return 1.0 
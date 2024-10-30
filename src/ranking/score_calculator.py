from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ProjectMetrics:
    stars: int
    forks: int
    watchers: int

@dataclass
class DeveloperMetrics:
    commits: int
    resolved_issues: int
    pull_requests: int
    code_reviews: int

class TalentRankCalculator:
    """
    TalentRank 评分计算器
    """
    
    # 项目重要度权重
    PROJECT_WEIGHTS = {
        'stars': 0.4,
        'forks': 0.3,
        'watchers': 0.3
    }
    
    # 开发者贡献度权重
    DEVELOPER_WEIGHTS = {
        'commits': 0.3,
        'resolved_issues': 0.25,
        'pull_requests': 0.25,
        'code_reviews': 0.2
    }
    
    def calculate_project_importance(self, metrics: ProjectMetrics) -> float:
        """
        计算项目重要度得分
        """
        normalized_stars = self._normalize_value(metrics.stars, 1000)  # 假设1000星为基准
        normalized_forks = self._normalize_value(metrics.forks, 500)   # 假设500 fork为基准
        normalized_watchers = self._normalize_value(metrics.watchers, 200)  # 假设200 watcher为基准
        
        score = (
            normalized_stars * self.PROJECT_WEIGHTS['stars'] +
            normalized_forks * self.PROJECT_WEIGHTS['forks'] +
            normalized_watchers * self.PROJECT_WEIGHTS['watchers']
        )
        
        return min(score, 100)  # 限制最高分为100
    
    def calculate_developer_contribution(self, metrics: DeveloperMetrics) -> float:
        """
        计算开发者贡献度得分
        """
        normalized_commits = self._normalize_value(metrics.commits, 100)  # 假设100次提交为基准
        normalized_issues = self._normalize_value(metrics.resolved_issues, 50)  # 假设50个issue为基准
        normalized_prs = self._normalize_value(metrics.pull_requests, 30)  # 假设30个PR为基准
        normalized_reviews = self._normalize_value(metrics.code_reviews, 40)  # 假设40次评审为基准
        
        score = (
            normalized_commits * self.DEVELOPER_WEIGHTS['commits'] +
            normalized_issues * self.DEVELOPER_WEIGHTS['resolved_issues'] +
            normalized_prs * self.DEVELOPER_WEIGHTS['pull_requests'] +
            normalized_reviews * self.DEVELOPER_WEIGHTS['code_reviews']
        )
        
        return min(score, 100)  # 限制最高分为100
    
    def calculate_final_score(self, project_score: float, contribution_score: float, 
                            activity_factor: float = 1.0) -> float:
        """
        计算最终的 TalentRank 得分
        """
        return (project_score * 0.4 + contribution_score * 0.6) * activity_factor
    
    @staticmethod
    def _normalize_value(value: int, baseline: int) -> float:
        """
        归一化数值，使用对数函数平滑大数值
        """
        import math
        if value <= 0:
            return 0
        return min(100, (math.log(value + 1) / math.log(baseline + 1)) * 100) 
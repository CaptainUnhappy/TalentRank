from typing import Dict, List, Optional
from dataclasses import dataclass
from github import Github
from datetime import datetime, timedelta

@dataclass
class DeveloperProfile:
    username: str
    name: Optional[str]
    location: Optional[str]
    blog: Optional[str]
    bio: Optional[str]
    repositories: List[str]
    followers: List[str]
    following: List[str]

class GitHubDataCollector:
    def __init__(self, access_token: str):
        """
        初始化 GitHub 数据采集器
        """
        self.github = Github(access_token)
        
    def get_developer_profile(self, username: str) -> DeveloperProfile:
        """
        获取开发者基础信息
        """
        user = self.github.get_user(username)
        return DeveloperProfile(
            username=user.login,
            name=user.name,
            location=user.location,
            blog=user.blog,
            bio=user.bio,
            repositories=[repo.full_name for repo in user.get_repos()],
            followers=[follower.login for follower in user.get_followers()],
            following=[following.login for following in user.get_following()]
        )
    
    def get_repository_metrics(self, repo_name: str) -> Dict:
        """
        获取仓库指标数据
        """
        repo = self.github.get_repo(repo_name)
        return {
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'watchers': repo.watchers_count,
            'created_at': repo.created_at,
            'updated_at': repo.updated_at,
            'language': repo.language,
            'topics': repo.get_topics()
        }
    
    def get_developer_contributions(self, username: str, repo_name: str) -> Dict:
        """
        获取开发者在特定仓库的贡献数据
        """
        repo = self.github.get_repo(repo_name)
        user = self.github.get_user(username)
        
        # 获取最近一年的贡献
        one_year_ago = datetime.now() - timedelta(days=365)
        
        commits = repo.get_commits(author=user, since=one_year_ago)
        issues = repo.get_issues(creator=username, state='closed', since=one_year_ago)
        pulls = repo.get_pulls(state='closed', creator=username)
        
        return {
            'commits_count': commits.totalCount,
            'resolved_issues': issues.totalCount,
            'pull_requests': pulls.totalCount,
            'code_reviews': self._get_review_count(repo, username, one_year_ago)
        }
    
    def _get_review_count(self, repo, username: str, since: datetime) -> int:
        """
        获取代码评审次数
        """
        reviews_count = 0
        pulls = repo.get_pulls(state='all')
        for pull in pulls:
            if pull.created_at < since:
                continue
            reviews = pull.get_reviews()
            reviews_count += sum(1 for review in reviews if review.user.login == username)
        return reviews_count 
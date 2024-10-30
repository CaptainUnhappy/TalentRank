from typing import List, Dict, Set
from collections import defaultdict

class DomainClassifier:
    """
    开发者技术领域分类器
    """
    
    def __init__(self):
        self.domain_keywords = self._init_domain_keywords()
        
    def classify_domains(self, 
                        repositories: List[Dict],
                        contributions: List[Dict]) -> Dict[str, float]:
        """
        分析开发者的技术领域分布
        返回：{领域: 权重}
        """
        domain_scores = defaultdict(float)
        total_weight = 0
        
        # 分析仓库信息
        for repo in repositories:
            # 获取仓库权重（基于star数量）
            weight = self._calculate_repo_weight(repo)
            total_weight += weight
            
            # 分析仓库的技术领域
            domains = self._analyze_repo_domains(repo)
            for domain in domains:
                domain_scores[domain] += weight
        
        # 标准化分数
        if total_weight > 0:
            for domain in domain_scores:
                domain_scores[domain] /= total_weight
        
        return dict(domain_scores)
    
    def _analyze_repo_domains(self, repo: Dict) -> Set[str]:
        """
        分析单个仓库的技术领域
        """
        domains = set()
        
        # 基于主要编程语言判断
        if repo.get('language'):
            domains.update(self._classify_by_language(repo['language']))
        
        # 基于仓库主题标签判断
        if repo.get('topics'):
            domains.update(self._classify_by_topics(repo['topics']))
            
        return domains
    
    def _calculate_repo_weight(self, repo: Dict) -> float:
        """
        计算仓库权重
        """
        return min(100, repo.get('stars', 0) / 100)  # 标准化到0-100
    
    def _init_domain_keywords(self) -> Dict[str, List[str]]:
        """
        初始化领域关键词映射
        """
        return {
            "Frontend": ["javascript", "typescript", "react", "vue", "angular", "web"],
            "Backend": ["python", "java", "golang", "nodejs", "django", "spring"],
            "Mobile": ["android", "ios", "flutter", "react-native", "mobile"],
            "DevOps": ["docker", "kubernetes", "aws", "cicd", "jenkins"],
            "AI/ML": ["machine-learning", "deep-learning", "tensorflow", "pytorch"],
            "Security": ["security", "cryptography", "encryption", "penetration"],
            "Database": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch"],
        }
    
    def _classify_by_language(self, language: str) -> Set[str]:
        """
        基于编程语言判断技术领域
        """
        language = language.lower()
        domains = set()
        
        for domain, keywords in self.domain_keywords.items():
            if language in keywords:
                domains.add(domain)
                
        return domains
    
    def _classify_by_topics(self, topics: List[str]) -> Set[str]:
        """
        基于主题标签判断技术领域
        """
        domains = set()
        
        for topic in topics:
            topic = topic.lower()
            for domain, keywords in self.domain_keywords.items():
                if any(keyword in topic for keyword in keywords):
                    domains.add(domain)
                    
        return domains 
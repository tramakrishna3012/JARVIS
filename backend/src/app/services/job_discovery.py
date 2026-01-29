"""
Job Discovery Service - Scraping and Parsing Jobs
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings


class JobDiscoveryService:
    """Service for discovering jobs from various sources"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def discover_jobs(
        self,
        sources: List[str],
        keywords: List[str],
        countries: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Discover jobs from multiple sources"""
        all_jobs = []
        
        for source in sources:
            try:
                if source == "linkedin":
                    jobs = await self._scrape_linkedin(keywords, countries, limit)
                elif source == "naukri":
                    jobs = await self._scrape_naukri(keywords, countries, limit)
                else:
                    continue
                
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error scraping {source}: {e}")
        
        # Deduplicate
        unique_jobs, duplicates = self._deduplicate_jobs(all_jobs)
        
        return {
            "jobs": unique_jobs,
            "total_found": len(all_jobs),
            "unique": len(unique_jobs),
            "duplicates": duplicates
        }
    
    async def _scrape_linkedin(
        self,
        keywords: List[str],
        countries: Optional[List[str]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Scrape LinkedIn job listings (public API)"""
        jobs = []
        
        # LinkedIn has a public job listing API that doesn't require auth
        # This is a placeholder - actual implementation would use their API
        
        search_query = " ".join(keywords)
        location = countries[0] if countries else "India"
        
        # Note: This would need proper implementation with LinkedIn API
        # For now, returning placeholder structure
        
        return jobs
    
    async def _scrape_naukri(
        self,
        keywords: List[str],
        countries: Optional[List[str]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Scrape Naukri job listings"""
        jobs = []
        
        # Build search URL
        search_query = "-".join(keywords)
        url = f"https://www.naukri.com/{search_query}-jobs"
        
        try:
            response = await self.http_client.get(url)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Parse job cards (structure may change)
            job_cards = soup.select('.jobTuple, .cust-job-tuple')
            
            for card in job_cards[:limit]:
                try:
                    job = self._parse_naukri_card(card)
                    if job:
                        jobs.append(job)
                except Exception:
                    continue
            
        except Exception as e:
            print(f"Naukri scraping error: {e}")
        
        return jobs
    
    def _parse_naukri_card(self, card) -> Optional[Dict[str, Any]]:
        """Parse a Naukri job card"""
        try:
            title_elem = card.select_one('.title, .jobTitle')
            company_elem = card.select_one('.companyInfo, .comp-name')
            location_elem = card.select_one('.location, .loc')
            experience_elem = card.select_one('.experience, .exp')
            
            if not title_elem:
                return None
            
            return {
                "title": title_elem.get_text(strip=True),
                "company": company_elem.get_text(strip=True) if company_elem else "Unknown",
                "location": location_elem.get_text(strip=True) if location_elem else "",
                "experience_required": experience_elem.get_text(strip=True) if experience_elem else "",
                "source": "naukri",
                "source_url": title_elem.get('href', ''),
                "discovered_at": datetime.utcnow().isoformat(),
            }
        except Exception:
            return None
    
    def _deduplicate_jobs(
        self, 
        jobs: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        """Remove duplicate job listings"""
        seen = set()
        unique = []
        duplicates = 0
        
        for job in jobs:
            # Create a signature for deduplication
            signature = f"{job['title'].lower()}|{job['company'].lower()}"
            
            if signature not in seen:
                seen.add(signature)
                unique.append(job)
            else:
                duplicates += 1
        
        return unique, duplicates
    
    def extract_skills_from_description(self, description: str) -> Dict[str, List[str]]:
        """Extract skills from job description using NLP"""
        # Common tech skills to look for
        common_skills = [
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "git", "ci/cd", "jenkins", "github actions",
            "machine learning", "deep learning", "nlp", "computer vision",
            "agile", "scrum", "jira"
        ]
        
        description_lower = description.lower()
        required = []
        nice_to_have = []
        
        for skill in common_skills:
            if skill in description_lower:
                # Check if it's in a "nice to have" context
                if any(phrase in description_lower for phrase in ["nice to have", "preferred", "bonus"]):
                    nice_to_have.append(skill)
                else:
                    required.append(skill)
        
        return {
            "required": required,
            "nice_to_have": nice_to_have
        }


# Singleton
job_discovery_service = JobDiscoveryService()

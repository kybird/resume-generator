from dataclasses import dataclass, field
from typing import List, Literal, Dict, Optional
import json

SourceType = Literal["fact", "inferred"]

@dataclass
class FactItem:
    text: str | List[str]
    source: SourceType = "fact"

    def __post_init__(self):
        if self.source not in ["fact", "inferred"]:
            raise ValueError(f"Invalid source: {self.source}. Must be 'fact' or 'inferred'.")

@dataclass
class Project:
    name: str
    problem: FactItem
    action: FactItem
    tech: FactItem
    result: FactItem
    difficulty: FactItem

    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        return cls(
            name=data["name"],
            problem=FactItem(**data["problem"]),
            action=FactItem(**data["action"]),
            tech=FactItem(**data["tech"]),
            result=FactItem(**data["result"]),
            difficulty=FactItem(**data["difficulty"])
        )

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "problem": self.problem.__dict__,
            "action": self.action.__dict__,
            "tech": self.tech.__dict__,
            "result": self.result.__dict__,
            "difficulty": self.difficulty.__dict__
        }

@dataclass
class CompanyMemory:
    period: str
    projects: List[Project] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CompanyMemory':
        return cls(
            period=data["period"],
            projects=[Project.from_dict(p) for p in data.get("projects", [])]
        )

    def to_dict(self) -> Dict:
        return {
            "period": self.period,
            "projects": [p.to_dict() for p in self.projects]
        }

@dataclass
class CareerMemory:
    companies: Dict[str, CompanyMemory] = field(default_factory=dict)

    @classmethod
    def load(cls, filepath: str) -> 'CareerMemory':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            companies = {}
            for company_name, company_data in data.items():
                companies[company_name] = CompanyMemory.from_dict(company_data)
            
            return cls(companies=companies)
        except FileNotFoundError:
            return cls()
        except json.JSONDecodeError:
            return cls()

    def save(self, filepath: str):
        data = {
            name: company.to_dict() 
            for name, company in self.companies.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

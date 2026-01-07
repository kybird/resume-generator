from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal
import json

@dataclass
class Period:
    start: str  # YYYY-MM
    end: str    # YYYY-MM or 'Present'

@dataclass
class Experience:
    id: str
    organization: str
    role: str
    period: Period

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            organization=data["organization"],
            role=data["role"],
            period=Period(**data["period"])
        )

@dataclass
class Person:
    name: str
    title: str

@dataclass
class Baseline:
    person: Person
    experiences: List[Experience]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            person=Person(**data["person"]),
            experiences=[Experience.from_dict(exp) for exp in data.get("experiences", [])]
        )
    
    def to_dict(self):
        return asdict(self)

@dataclass
class FactResult:
    type: str = "none" # qualitative, quantitative, none
    description: str = ""

@dataclass
class Fact:
    experience_id: str
    responsibility: str # What did you do? (The core task)
    direct_work: bool   # Did you do it directly?
    tech: List[str]     # Tech stack used
    problem: str        # Context/Problem
    action: str         # Detailed action (How)
    result: FactResult  # Outcome
    
    # Metadata
    source: str = "interview"

    @classmethod
    def from_dict(cls, data: dict):
        result_data = data.get("result", {})
        # handle simple string legacy or dict
        if isinstance(result_data, str):
            res_obj = FactResult(type="none", description=result_data)
        else:
            res_obj = FactResult(**result_data)

        return cls(
            experience_id=data["experience_id"],
            responsibility=data["responsibility"],
            direct_work=data.get("direct_work", True),
            tech=data.get("tech", []),
            problem=data.get("problem", ""),
            action=data.get("action", ""),
            result=res_obj,
            source=data.get("source", "interview")
        )

    def to_dict(self):
        return asdict(self)

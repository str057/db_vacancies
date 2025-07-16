from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Employer:
    id: int
    name: str
    url: Optional[str] = None
    description: Optional[str] = None

    def clean_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return re.sub(r"[^\x00-\x7F]+", " ", text)


@dataclass
class Vacancy:
    id: int
    name: str
    employer_id: int
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    currency: Optional[str] = None
    url: Optional[str] = None

    def clean_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return re.sub(r"[^\x00-\x7F]+", " ", text)

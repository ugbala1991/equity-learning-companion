backend/app.py

from fastapi import FastAPI, Depends, HTTPException
db.refresh(a)
return a


@app.get("/assignments/{assignment_id}", response_model=AssignmentOut)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
a = db.query(Assignment).get(assignment_id)
if not a:
raise HTTPException(status_code=404, detail="Assignment not found")
return a


# --- Submissions ---
@app.post("/submissions", response_model=SubmissionOut)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
if not db.query(Assignment).get(payload.assignment_id):
raise HTTPException(status_code=404, detail="Assignment not found")
s = Submission(assignment_id=payload.assignment_id, student_id=payload.student_id, answer=payload.answer)
db.add(s)
db.commit()
db.refresh(s)
return s


# --- Feedback ---
@app.post("/feedback", response_model=FeedbackOut)
def generate_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
a = db.query(Assignment).get(req.assignment_id)
if not a:
raise HTTPException(status_code=404, detail="Assignment not found")


fb_service = FeedbackService()
tr_service = TranslationService()


# Generate feedback in source language (assume assignment prompt language)
feedback = fb_service.generate(answer=req.answer, prompt=a.prompt, rubric=a.rubric)


# Optionally translate comment/next_step
target = (req.target_language or "").strip().lower()
if target and target not in {"", "auto", "en"}:
feedback["comment"] = tr_service.translate(text=feedback["comment"], target_language=target)
feedback["next_step"] = tr_service.translate(text=feedback["next_step"], target_language=target)


return feedback


# --- Translation utility ---
@app.post("/translate", response_model=TranslateOut)
def translate_text(req: TranslateRequest):
tr_service = TranslationService()
translated = tr_service.translate(text=req.text, target_language=req.target_language)
return {"text": translated, "target_language": req.target_language}


# --- Analytics ---
@app.get("/analytics/{assignment_id}")
def analytics(assignment_id: int, db: Session = Depends(get_db)):
from backend.services.analysis import cluster_comments, score_distribution
subs = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
comments = [s.auto_feedback for s in subs if s.auto_feedback]
clusters = cluster_comments(comments)
scores = [s.auto_score for s in subs if s.auto_score is not None]
dist = score_distribution(scores)
return {"clusters": clusters, "score_distribution": dist}

backend/db.py


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DB_URL = os.getenv("DB_URL", "sqlite:///./data/app.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
from backend import models # noqa
Base.metadata.create_all(bind=engine)


backend/models.py

from sqlalchemy import Column, Integer, String, Text
from backend.db import Base


class Assignment(Base):
__tablename__ = "assignments"
id = Column(Integer, primary_key=True, index=True)
title = Column(String(255), nullable=False)
prompt = Column(Text, nullable=False)
rubric = Column(Text, nullable=False) # JSON string


class Submission(Base):
__tablename__ = "submissions"
id = Column(Integer, primary_key=True, index=True)
assignment_id = Column(Integer, index=True, nullable=False)
student_id = Column(String(64), index=True, nullable=False)
answer = Column(Text, nullable=False)
auto_score = Column(Integer, nullable=True)
auto_feedback = Column(Text, nullable=True)

backend/schemas.py
from pydantic import BaseModel, Field
from typing import Dict
import json


class AssignmentCreate(BaseModel):
title: str
prompt: str
rubric: Dict[str, str] = Field(
default_factory=lambda: {
"Correctness": "Is the answer factually accurate?",
"Reasoning": "Does the student explain the why/how?",
"Clarity": "Is writing clear and concise?"
}
)
def rubric_json(self) -> str:
return json.dumps(self.rubric)


class AssignmentOut(BaseModel):
id: int
title: str
prompt: str
rubric: str
class Config:
orm_mode = True


class SubmissionCreate(BaseModel):
assignment_id: int
student_id: str
answer: str


class SubmissionOut(BaseModel):
id: int
assignment_id: int
student_id: str
answer: str
class Config:
orm_mode = True


class FeedbackRequest(BaseModel):
assignment_id: int
answer: str
target_language: str | None = None # e.g., "es", "fr", "sw"


class FeedbackOut(BaseModel):
overall_score: int
per_criterion: Dict[str, int]
comment: str
next_step: str


class TranslateRequest(BaseModel):
text: str
target_language: str


class TranslateOut(BaseModel):
text: str
target_language: str

backend/utils/text.py


import re
from collections import Counter


def word_count(s: str) -> int:
return len(re.findall(r"\w+", s or ""))


def keyword_hits(s: str, keywords: list[str]) -> int:
text = (s or "").lower()
return sum(1 for k in keywords if k.lower() in text)


def top_terms(texts: list[str], k: int = 5) -> list[str]:
counts = Counter()
for t in texts:
for w in re.findall(r"[a-zA-Z]{3,}", t.lower()):
counts[w] += 1
return [w for w, _ in counts.most_common(k)]

backend/ai_providers/base.py

from abc import ABC, abstractmethod
from typing import Dict


class FeedbackModel(ABC):
@abstractmethod
def generate(self, *, prompt: str, answer: str, rubric: Dict[str, str]) -> dict:
raise NotImplementedError


class TranslateModel(ABC):
@abstractmethod
def translate(self, *, text: str, target_language: str) -> str:
raise NotImplementedError

backend/ai_providers/rule_based_feedback.py

from typing import Dict
from backend.ai_providers.base import FeedbackModel
from backend.utils.text import word_count, keyword_hits


class RuleBasedFeedback(FeedbackModel):
def generate(self, *, prompt: str, answer: str, rubric: Dict[str, str]) -> dict:
keywords = self._extract_keywords(prompt)
wc = word_count(answer)
coverage = keyword_hits(answer, keywords)


correctness = min(10, 3 + coverage * 2)
reasoning = 3 if wc < 20 else 6 if wc < 60 else 8 if wc < 120 else 10
clarity = 5 if wc <= 15 e

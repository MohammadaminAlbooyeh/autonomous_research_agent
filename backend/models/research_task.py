import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.database import Base


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, nullable=False)
    queries = Column(JSON, default=list)
    depth = Column(String, default="medium")
    status = Column(String, default="pending")
    progress = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sources = relationship("Source", back_populates="task", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="task", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="task", uselist=False, cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("research_tasks.id"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, default="")
    content_snippet = Column(Text, default="")
    relevance_score = Column(Float, default=0.0)
    accessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("ResearchTask", back_populates="sources")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("research_tasks.id"), nullable=False)
    claim = Column(Text, nullable=False)
    evidence = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    source_urls = Column(JSON, default=list)

    task = relationship("ResearchTask", back_populates="findings")

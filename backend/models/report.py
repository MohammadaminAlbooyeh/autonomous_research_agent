import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.models.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("research_tasks.id"), nullable=False)
    title = Column(String, default="")
    executive_summary = Column(Text, default="")
    sections = Column(JSON, default=list)
    citations = Column(JSON, default=list)
    word_count = Column(Integer, nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("ResearchTask", back_populates="report")

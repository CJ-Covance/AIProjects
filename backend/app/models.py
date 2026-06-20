import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    folder_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    domains: Mapped[List["Domain"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    folder_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    source: Mapped["Source"] = relationship(back_populates="domains")
    projects: Mapped[List["Project"]] = relationship(
        back_populates="domain", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    domain_id: Mapped[str] = mapped_column(String(36), ForeignKey("domains.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    folder_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    domain: Mapped["Domain"] = relationship(back_populates="projects")
    web_pages: Mapped[List["WebPage"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class WebPage(Base):
    __tablename__ = "web_pages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source_file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    project: Mapped["Project"] = relationship(back_populates="web_pages")
    chunks: Mapped[List["Chunk"]] = relationship(
        back_populates="web_page", cascade="all, delete-orphan"
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    web_page_id: Mapped[str] = mapped_column(String(36), ForeignKey("web_pages.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    domain_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)

    web_page: Mapped["WebPage"] = relationship(back_populates="chunks")

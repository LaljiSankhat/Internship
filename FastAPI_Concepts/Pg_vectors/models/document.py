from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

from core.db import Base
from pgvector.sqlalchemy import VECTOR


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    chunks: Mapped[list["DocumentChunks"]] = relationship("DocumentChunks", back_populates="document")

    def __repr__(self):
        return (
            f"<Document(id={self.id}, text={self.text})>"
        )


class DocumentChunks(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    chunk_text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    chunk_vector: Mapped[list[float]] = mapped_column(
        VECTOR(384),
        nullable=False
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks"
    )
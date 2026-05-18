from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text,
    ForeignKey, JSON, Enum as SAEnum, func
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session
import enum

from utils.config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


class Base(DeclarativeBase):
    pass


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    FLAGGED = "flagged"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    mime_type = Column(String(50), nullable=False)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.PENDING)

    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    row_index = Column(Integer, default=0)

    date = Column(String(20), nullable=True)
    shift = Column(String(10), nullable=True)
    employee_number = Column(String(50), nullable=True)
    operation_code = Column(String(50), nullable=True)
    machine_number = Column(String(50), nullable=True)
    work_order_number = Column(String(50), nullable=True)
    quantity_produced = Column(String(20), nullable=True)
    time_taken = Column(String(20), nullable=True)

    confidence_scores = Column(JSON, default=dict)
    status = Column(SAEnum(ExtractionStatus), default=ExtractionStatus.PENDING_REVIEW)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="extractions")
    validation_flags = relationship("ValidationFlag", back_populates="extraction", cascade="all, delete-orphan")


class ValidationFlag(Base):
    __tablename__ = "validation_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extraction_id = Column(Integer, ForeignKey("extractions.id"), nullable=False)
    field = Column(String(50), nullable=False)
    issue_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    extraction = relationship("Extraction", back_populates="validation_flags")


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return Session(engine)


def add_document(filename, filepath, mime_type):
    with get_session() as session:
        doc = Document(
            filename=filename,
            filepath=filepath,
            mime_type=mime_type,
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc


def update_document_status(doc_id, status):
    with get_session() as session:
        doc = session.get(Document, doc_id)
        if doc:
            doc.status = status
            session.commit()


def add_extraction(document_id, row_index, data, confidence_scores):
    with get_session() as session:
        ext = Extraction(
            document_id=document_id,
            row_index=row_index,
            date=data.get("date", ""),
            shift=data.get("shift", ""),
            employee_number=data.get("employee_number", ""),
            operation_code=data.get("operation_code", ""),
            machine_number=data.get("machine_number", ""),
            work_order_number=data.get("work_order_number", ""),
            quantity_produced=data.get("quantity_produced", ""),
            time_taken=data.get("time_taken", ""),
            confidence_scores=confidence_scores or {},
            status=ExtractionStatus.PENDING_REVIEW,
        )
        session.add(ext)
        session.commit()
        session.refresh(ext)
        return ext


def update_extraction(extraction_id, data):
    with get_session() as session:
        ext = session.get(Extraction, extraction_id)
        if ext:
            for field in ["date", "shift", "employee_number", "operation_code",
                          "machine_number", "work_order_number",
                          "quantity_produced", "time_taken"]:
                if field in data:
                    setattr(ext, field, data[field])
            ext.status = ExtractionStatus.REVIEWED
            session.commit()
            session.refresh(ext)
            return ext


def add_validation_flag(extraction_id, field, issue_type, message):
    with get_session() as session:
        flag = ValidationFlag(
            extraction_id=extraction_id,
            field=field,
            issue_type=issue_type,
            message=message,
        )
        session.add(flag)
        ext = session.get(Extraction, extraction_id)
        if ext and ext.status != ExtractionStatus.FLAGGED:
            ext.status = ExtractionStatus.FLAGGED
        session.commit()
        return flag


def clear_validation_flags(extraction_id):
    with get_session() as session:
        session.query(ValidationFlag).filter(
            ValidationFlag.extraction_id == extraction_id
        ).delete()
        ext = session.get(Extraction, extraction_id)
        if ext:
            ext.status = ExtractionStatus.PENDING_REVIEW
        session.commit()


def get_all_documents():
    with get_session() as session:
        return session.query(Document).order_by(Document.upload_date.desc()).all()


def get_document(doc_id):
    with get_session() as session:
        return session.get(Document, doc_id)


def get_extractions(document_id=None, status=None, search=None):
    with get_session() as session:
        query = session.query(Extraction)
        if document_id:
            query = query.filter(Extraction.document_id == document_id)
        if status:
            query = query.filter(Extraction.status == status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Extraction.work_order_number.ilike(search_term)
                | Extraction.employee_number.ilike(search_term)
                | Extraction.machine_number.ilike(search_term)
                | Extraction.operation_code.ilike(search_term)
            )
        query = query.order_by(Extraction.created_at.desc())
        return query.all()


def get_extraction(extraction_id):
    with get_session() as session:
        return session.get(Extraction, extraction_id)


def get_validation_flags(extraction_id=None):
    with get_session() as session:
        query = session.query(ValidationFlag)
        if extraction_id:
            query = query.filter(ValidationFlag.extraction_id == extraction_id)
        return query.all()


def get_dashboard_stats():
    with get_session() as session:
        total_docs = session.query(func.count(Document.id)).scalar() or 0
        total_extractions = session.query(func.count(Extraction.id)).scalar() or 0
        flagged_count = session.query(func.count(Extraction.id)).filter(
            Extraction.status == ExtractionStatus.FLAGGED
        ).scalar() or 0
        reviewed_count = session.query(func.count(Extraction.id)).filter(
            Extraction.status == ExtractionStatus.REVIEWED
        ).scalar() or 0
        pending_count = session.query(func.count(Extraction.id)).filter(
            Extraction.status == ExtractionStatus.PENDING_REVIEW
        ).scalar() or 0
        total_flags = session.query(func.count(ValidationFlag.id)).scalar() or 0

        shift_counts = {}
        for shift in ["1", "2", "3"]:
            count = session.query(func.count(Extraction.id)).filter(
                Extraction.shift == shift
            ).scalar() or 0
            shift_counts[shift] = count

        machine_counts_rows = (
            session.query(Extraction.machine_number, func.count(Extraction.id))
            .filter(Extraction.machine_number != "", Extraction.machine_number.isnot(None))
            .group_by(Extraction.machine_number)
            .all()
        )
        machine_counts = {m or "Unknown": c for m, c in machine_counts_rows}

        total_qty = session.query(func.sum(Extraction.quantity_produced)).filter(
            Extraction.quantity_produced != "",
            Extraction.quantity_produced.isnot(None),
            Extraction.quantity_produced.cast(Integer) > 0,
        ).scalar() or 0

        return {
            "total_documents": total_docs,
            "total_extractions": total_extractions,
            "flagged_count": flagged_count,
            "reviewed_count": reviewed_count,
            "pending_count": pending_count,
            "total_validation_flags": total_flags,
            "shift_counts": shift_counts,
            "machine_counts": machine_counts,
            "total_quantity": total_qty,
        }


def bulk_get_extractions_with_flags(search=None):
    with get_session() as session:
        query = (
            session.query(Extraction)
            .outerjoin(ValidationFlag)
        )
        if search:
            term = f"%{search}%"
            query = query.filter(
                Extraction.work_order_number.ilike(term)
                | Extraction.employee_number.ilike(term)
                | Extraction.machine_number.ilike(term)
                | Extraction.operation_code.ilike(term)
            )
        query = query.order_by(Extraction.created_at.desc()).distinct()
        extractions = query.all()

        result = []
        for ext in extractions:
            flags = session.query(ValidationFlag).filter(
                ValidationFlag.extraction_id == ext.id
            ).all()
            doc = session.get(Document, ext.document_id)
            result.append({
                "extraction": ext,
                "flags": flags,
                "document": doc,
            })
        return result

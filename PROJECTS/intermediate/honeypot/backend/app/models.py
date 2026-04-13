import enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from .database import Base


class ServiceType(str, enum.Enum):
    SSH = "ssh"
    HTTP = "http"
    FTP = "ftp"


class HoneypotEvent(Base):
    __tablename__ = "honeypot_events"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(Enum(ServiceType), nullable=False, index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer)
    username = Column(String(255))
    password = Column(String(255))
    command = Column(Text)
    path = Column(Text)
    user_agent = Column(Text)
    country = Column(String(100))
    city = Column(String(100))
    threat_score = Column(Integer, default=0)
    raw_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

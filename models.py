from sqlalchemy import Column, Integer, String, Text
from .database import Base

class UploadedTable(Base):
    __tablename__ = "uploaded_tables"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, unique=True, index=True)
    source_file = Column(String)
    info = Column(Text)  # optional json metadata

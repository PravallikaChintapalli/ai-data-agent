import pandas as pd
from pathlib import Path
import json
from sqlalchemy import MetaData
from .database import engine
from .models import UploadedTable


def _clean_colname(c):
    if isinstance(c, str) and c.strip():
        return c.strip().replace(" ", "_").replace("%", "pct")
    return str(c)


def parse_and_ingest_excel(path: Path, db):
    # Read sheets
    xls = pd.ExcelFile(path)
    sheets = []
    metadata = MetaData(bind=engine)
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name, dtype=object)
        # basic clean: forward-fill header if unnamed, reset columns
        df.columns = [_clean_colname(c) for c in df.columns]
        # convert types where possible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except Exception:
                pass
        # make a table name
        table_name = f"t_{Path(path).stem}_{sheet_name}".replace(' ', '_')
        # write to sql (replace)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        # persist metadata
        ut = UploadedTable(table_name=table_name, source_file=str(path), info=json.dumps({"rows": len(df)}))
        db.add(ut)
        db.commit()
        sheets.append({"sheet": sheet_name, "table": table_name, "rows": len(df), "columns": list(df.columns)})
    return sheets

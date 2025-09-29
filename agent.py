import os
import json
from openai import OpenAI
from sqlalchemy import text
from .database import engine
import matplotlib.pyplot as plt
from pathlib import Path

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

CHARTS_DIR = Path('./charts')
CHARTS_DIR.mkdir(exist_ok=True)


def _call_llm(prompt: str):
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=800,
        temperature=0,
    )
    return resp.choices[0].message.content


def handle_nl_query(question: str, table_name: str | None, db=None):
    # 1) Build prompt with schema info
    with engine.connect() as conn:
        # list tables if no table_name
        if not table_name:
            res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"))
            tables = [r[0] for r in res]
            # limit prompt size
            schema_snippet = []
            for t in tables:
                cols = conn.execute(text(f"PRAGMA table_info('{t}')")).fetchall()
                colnames = [c[1] for c in cols]
                schema_snippet.append(f"{t}: columns = {colnames}")
            schema_text = "\\n".join(schema_snippet)
        else:
            cols = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
            schema_text = f"{table_name}: columns = {[c[1] for c in cols]}"

    prompt = f"You are an expert that translates natural language analytics questions into a single safe SQL query for SQLite.\\nSchema:\\n{schema_text}\\n\\nQuestion: {question}\\n\\nRespond with JSON containing fields: sql, explanation, viz_hint (one-line describing desired chart e.g. 'bar: category vs value'). Only return JSON."

    llm_out = _call_llm(prompt)
    # try parse JSON
    try:
        data = json.loads(llm_out.strip())
    except Exception:
        import re
        m = re.search(r"\\{.*\\}", llm_out, re.S)
        if m:
            data = json.loads(m.group(0))
        else:
            return {"error": "LLM did not return valid JSON", "raw": llm_out}

    sql = data.get('sql')
    explanation = data.get('explanation')
    viz_hint = data.get('viz_hint')

    # run SQL
    with engine.connect() as conn:
        try:
            res = conn.execute(text(sql)).mappings().all()
            rows = [dict(r) for r in res]
        except Exception as e:
            return {"error": f"SQL execution failed: {e}", "suggested_sql": sql}

    # optionally create a chart
    chart_url = None
    if rows and viz_hint:
        try:
            chart_path = create_chart(rows, viz_hint)
            chart_url = f"/chart/{chart_path.name}"
        except Exception as e:
            chart_url = None

    return {"sql": sql, "explanation": explanation, "rows": rows, "chart": chart_url}


def create_chart(rows, viz_hint: str):
    parts = viz_hint.split(':')
    kind = parts[0].strip()
    body = parts[1].strip() if len(parts) > 1 else ''
    cols = [c.strip() for c in body.split('vs')]
    if len(cols) < 2:
        raise ValueError('viz_hint must contain \"vs\" with two columns')
    xcol, ycol = cols[0], cols[1]
    xs = [r.get(xcol) for r in rows]
    ys = [r.get(ycol) for r in rows]
    fig = plt.figure()
    if kind == 'bar':
        plt.bar(xs, ys)
    elif kind == 'line':
        plt.plot(xs, ys)
    elif kind == 'scatter':
        plt.scatter(xs, ys)
    else:
        plt.bar(xs, ys)
    plt.xticks(rotation=45)
    plt.tight_layout()
    fname = f"chart_{abs(hash(str(rows)+viz_hint)) % (10**8)}.png"
    path = CHARTS_DIR / fname
    fig.savefig(path)
    plt.close(fig)
    return path

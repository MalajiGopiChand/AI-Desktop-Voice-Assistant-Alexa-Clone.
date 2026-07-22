"""Data analytics — CSV, Excel, charts, SQL."""
import os
import sqlite3
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL


class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("analytics_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "analyze_csv": self._analyze_csv,
                "create_chart": self._create_chart,
                "sql_query": self._sql_query,
                "describe_data": self._describe_data,
                "predict_trend": self._predict_trend,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _load_df(self, path):
        import pandas as pd
        path = os.path.expanduser(path)
        if path.endswith((".xlsx", ".xls")):
            return pd.read_excel(path)
        return pd.read_csv(path)

    def _analyze_csv(self, params):
        try:
            import pandas as pd
        except ImportError:
            return {"success": False, "message": "Install pandas: pip install pandas", "data": {}}
        df = self._load_df(params.get("path", ""))
        stats = df.describe(include="all").to_string()
        summary = chat(
            [{"role": "system", "content": "Analyze dataset stats and give insights for voice."},
             {"role": "user", "content": stats[:4000]}],
            model=FAST_MODEL, max_tokens=300,
        )
        return {"success": True, "message": summary, "data": {"stats": stats, "summary": summary}}

    def _create_chart(self, params):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        df = self._load_df(params.get("path", ""))
        col_x = params.get("x", df.columns[0])
        col_y = params.get("y", df.columns[1] if len(df.columns) > 1 else df.columns[0])
        chart_type = params.get("type", "bar")

        fig, ax = plt.subplots(figsize=(10, 6))
        if chart_type == "line":
            df.plot(x=col_x, y=col_y, ax=ax, kind="line")
        elif chart_type == "pie":
            df[col_y].value_counts().plot.pie(ax=ax, autopct="%1.1f%%")
        else:
            df.plot(x=col_x, y=col_y, ax=ax, kind="bar")

        from config import CHARTS_DIR
        out = os.path.join(CHARTS_DIR, f"chart_{int(__import__('time').time())}.png")
        plt.tight_layout()
        plt.savefig(out)
        plt.close()
        return {"success": True, "message": f"Chart saved to {out}", "data": {"path": out}}

    def _sql_query(self, params):
        db_path = params.get("db", ":memory:")
        query = params.get("query", "SELECT 1")
        conn = sqlite3.connect(db_path)
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        conn.close()
        result = df.head(20).to_string()
        return {"success": True, "message": result, "data": {"result": result}}

    def _describe_data(self, params):
        df = self._load_df(params.get("path", ""))
        info = f"Rows: {len(df)}, Columns: {list(df.columns)}"
        return {"success": True, "message": info, "data": {"info": info}}

    def _predict_trend(self, params):
        df = self._load_df(params.get("path", ""))
        col = params.get("column", df.columns[-1])
        if len(df) < 3:
            return {"success": False, "message": "Not enough data for trend", "data": {}}
        trend = "increasing" if df[col].iloc[-1] > df[col].iloc[0] else "decreasing"
        return {"success": True, "message": f"Column {col} trend appears {trend}.", "data": {"trend": trend}}

# Sales Summary API (FastAPI)
# Автор: <Ваше Имя>, 2025-11-11
#
# Коротко по-человечески:
# - Не генерирую «случайные» продажи. Беру jsonplaceholder и детерминированно
#   превращаю посты в суммы: len(title)+len(body). Это стабильно и воспроизводимо.
# - Асинхронный HTTP через aiohttp, расчёты — pandas.
# - Дата-валидация и понятные ошибки. Диапазон ограничен 365 днями.

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd
import asyncio
import aiohttp

app = FastAPI(title="Sales Summary API", description="Сводка продаж по дням с 3-дневным скользящим средним")

DATE_FMT = "%Y-%m-%d"

def parse_date(s: str) -> datetime:
    """Парсинг даты YYYY-MM-DD с дружелюбной ошибкой."""
    try:
        return datetime.strptime(s, DATE_FMT)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {s}. Expected YYYY-MM-DD")

async def fetch_posts(session: aiohttp.ClientSession) -> list[dict]:
    """Асинхронно тянем мок-данные. Если апстрим лег — поднимем осмысленный 502."""
    url = "https://jsonplaceholder.typicode.com/posts"
    async with session.get(url, timeout=20) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise HTTPException(status_code=502, detail=f"Upstream error {resp.status}: {text[:200]}")
        return await resp.json()

def synthesize_daily_sales(posts: list[dict], start: datetime, end: datetime) -> pd.DataFrame:
    """Делаем воспроизводимые 'продажи' по дням из постов.
    - список дней = от start до end,
    - сумма по посту = len(title)+len(body),
    - раскладываем посты по дням циклически.
    """
    if end < start:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    days = pd.date_range(start=start.date(), end=end.date(), freq="D")
    if len(days) == 0:
        days = pd.date_range(start=start.date(), end=start.date(), freq="D")

    amounts = [(len(p.get("title", "")) + len(p.get("body", ""))) for p in posts]
    if not amounts:
        return pd.DataFrame({"date": days, "sales": [0] * len(days)})

    sales_by_day = [0] * len(days)
    for i, amt in enumerate(amounts):
        sales_by_day[i % len(days)] += amt

    df = pd.DataFrame({"date": days, "sales": sales_by_day})
    return df

@app.get("/sales/summary")
async def get_sales_summary(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
):
    """Возвращает:
    - daily: продажи по дням и скользящее среднее (окно=3),
    - top5_days: ТОП-5 дней по продажам,
    - summary: агрегаты (итог, дней в диапазоне, среднее).
    """
    start = parse_date(start_date)
    end = parse_date(end_date)

    # Предохранитель на длину диапазона.
    if (end - start).days > 365:
        raise HTTPException(status_code=400, detail="Date range too large. Max 365 days.")

    try:
        async with aiohttp.ClientSession() as session:
            posts = await fetch_posts(session)

        df = synthesize_daily_sales(posts, start, end)
        # min_periods=1 — чтобы первые 1-2 дня не были NaN
        df["rolling_avg_3"] = df["sales"].rolling(window=3, min_periods=1).mean()

        top5 = df.nlargest(5, "sales").copy()
        top5["date"] = top5["date"].dt.strftime(DATE_FMT)

        out = {
            "range": {"start_date": start.strftime(DATE_FMT), "end_date": end.strftime(DATE_FMT)},
            "daily": [
                {"date": d.strftime(DATE_FMT), "sales": float(s), "rolling_avg_3": float(r)}
                for d, s, r in zip(df["date"], df["sales"], df["rolling_avg_3"])
            ],
            "top5_days": top5[["date", "sales"]].to_dict(orient="records"),
            "summary": {
                "total_sales": float(df["sales"].sum()),
                "days": int(len(df)),
                "mean_daily_sales": float(df["sales"].mean()),
            },
        }
        return JSONResponse(out)
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout while fetching upstream data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

"""
抖音数据日增计算脚本
用于计算指定日期的抖音数据增量，并保存到 douyin_aweme_day 表
"""

import argparse
import asyncio
import os
from datetime import datetime
from typing import Tuple

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text

from database.db_session import get_session

load_dotenv()

parser = argparse.ArgumentParser(description="计算抖音增量数据")
parser.add_argument(
    "-t",
    "--target_date",
    type=str,
    default=datetime.today().strftime("%Y-%m-%d"),
    help="目标日期，格式: YYYY-MM-DD，默认为今天",
)
parser.add_argument(
    "-d", "--days", type=int, default=15, help="往前推多少天，默认为 15"
)


def get_mysql_engine():
    """从环境变量创建 MySQL 连接引擎（同步版本）"""
    from dotenv import load_dotenv

    load_dotenv()

    user = os.getenv("MYSQL_DB_USER")
    password = os.getenv("MYSQL_DB_PWD")
    host = os.getenv("MYSQL_DB_HOST")
    port = os.getenv("MYSQL_DB_PORT")
    db_name = os.getenv("MYSQL_DB_NAME")

    if not all([user, password, host, port, db_name]):
        missing = [
            k
            for k, v in {
                "MYSQL_DB_USER": user,
                "MYSQL_DB_PWD": password,
                "MYSQL_DB_HOST": host,
                "MYSQL_DB_PORT": port,
                "MYSQL_DB_NAME": db_name,
            }.items()
            if v is None
        ]
        raise EnvironmentError(f"Missing environment variables: {missing}")

    from sqlalchemy import create_engine

    database_url = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
    )
    return create_engine(database_url, echo=False)


def fetch_douyin_data(target_date: str, days: int = 0) -> pd.DataFrame:
    """从数据库读取指定日期范围的 douyin_aweme_summary 数据"""
    engine = get_mysql_engine()

    target_datetime = pd.to_datetime(target_date)
    tz = "Asia/Shanghai"

    end_dt = (
        pd.to_datetime(target_datetime).tz_localize(tz)
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
    start_dt = pd.to_datetime(target_datetime).tz_localize(tz) - pd.Timedelta(days=days)

    start_us = int(start_dt.timestamp() * 1_000)
    end_us = int(end_dt.timestamp() * 1_000)

    query = f"""
    SELECT 
        aweme_id, sec_uid, nickname, aweme_url, create_time, 
        digg_count, collect_count, share_count, comment_count,
        elastic_title, product_id, product_title, update_ts
    FROM douyin_aweme_summary 
    WHERE elastic_title IS NOT NULL
      AND update_ts >= {start_us}
      AND update_ts <= {end_us}
    ORDER BY aweme_url, update_ts;
    """
    print(f"[查询时间范围] {start_dt} 到 {end_dt}")

    try:
        df = pd.read_sql(query, engine)
        print(
            f"✅ Successfully loaded {len(df)} records from {start_dt.date()} to {end_dt.date()}"
        )
        return df
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise


def calculate_daily_increment(
    group: pd.DataFrame, target_data_date, days: int
) -> pd.DataFrame:
    """计算单个视频在时间段内每天的增量"""
    group = group.sort_values("update_ts").copy()
    group["data_date"] = group["update_ts"].dt.date

    start_date = pd.Timestamp(target_data_date) - pd.Timedelta(days=days)
    all_dates = pd.date_range(start=start_date, end=target_data_date).date.tolist()

    video_create_date = pd.to_datetime(group["create_time"].iloc[0]).date()
    results = []

    for i, stat_date in enumerate(all_dates):
        if stat_date < video_create_date:
            continue

        next_date = all_dates[i + 1] if i + 1 < len(all_dates) else None
        next_cutoff_time = (
            pd.Timestamp(next_date).tz_localize("Asia/Shanghai") + pd.Timedelta(hours=8)
            if next_date
            else None
        )

        day_data = group[group["data_date"] == stat_date]
        if len(day_data) == 0:
            continue

        day_first = day_data.iloc[0]
        day_last = day_data.iloc[-1]

        if stat_date == video_create_date:
            digg_inc = day_last["digg_count"]
            collect_inc = day_last["collect_count"]
            share_inc = day_last["share_count"]
        elif next_date:
            next_day_data = group[group["data_date"] == next_date]
            next_day_data_before_cutoff = (
                next_day_data[next_day_data["update_ts"] < next_cutoff_time]
                if next_cutoff_time
                else pd.DataFrame()
            )

            if len(next_day_data_before_cutoff) > 0:
                next_first = next_day_data_before_cutoff.iloc[0]
                digg_inc = max(0, next_first["digg_count"] - day_first["digg_count"])
                collect_inc = max(
                    0, next_first["collect_count"] - day_first["collect_count"]
                )
                share_inc = max(0, next_first["share_count"] - day_first["share_count"])
            else:
                digg_inc = max(0, day_last["digg_count"] - day_first["digg_count"])
                collect_inc = max(
                    0, day_last["collect_count"] - day_first["collect_count"]
                )
                share_inc = max(0, day_last["share_count"] - day_first["share_count"])
        else:
            digg_inc = max(0, day_last["digg_count"] - day_first["digg_count"])
            collect_inc = max(0, day_last["collect_count"] - day_first["collect_count"])
            share_inc = max(0, day_last["share_count"] - day_first["share_count"])

        results.append(
            {
                "data_date": stat_date,
                "digg_count": digg_inc,
                "collect_count": collect_inc,
                "share_count": share_inc,
                "first_update_ts": day_first["update_ts"],
                "last_update_ts": day_last["update_ts"],
            }
        )

    return pd.DataFrame(results)


def process_douyin_data(
    df: pd.DataFrame, target_date: str, days: int = 0
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """处理数据：计算时间段内每天每个 aweme_url 的增量"""
    if df.empty:
        print("⚠️ No data to process.")
        return pd.DataFrame(), pd.DataFrame()

    target_datetime = pd.to_datetime(target_date)
    target_data_date = target_datetime.date()

    df["update_ts"] = (
        pd.to_datetime(df["update_ts"], unit="ms", errors="coerce")
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Shanghai")
    )
    df["create_time"] = (
        pd.to_datetime(df["create_time"], unit="s", errors="coerce")
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Shanghai")
    )

    all_results = []
    for aweme_url, group in df.groupby("aweme_url"):
        if len(group) == 0:
            continue

        latest = group.iloc[-1].to_dict()
        daily_increments = calculate_daily_increment(group, target_data_date, days)

        for _, inc_row in daily_increments.iterrows():
            result_row = {
                "aweme_id": latest["aweme_id"],
                "sec_uid": latest.get("sec_uid"),
                "nickname": latest["nickname"],
                "aweme_url": aweme_url,
                "create_time": latest["create_time"],
                "digg_count": inc_row["digg_count"],
                "collect_count": inc_row["collect_count"],
                "share_count": inc_row["share_count"],
                "digg_tt": latest["digg_count"],
                "collect_tt": latest["collect_count"],
                "share_tt": latest["share_count"],
                "comment_count": latest.get("comment_count", 0),
                "elastic_title": latest["elastic_title"],
                "product_id": latest.get("product_id"),
                "product_title": latest["product_title"],
                "data_date": inc_row["data_date"],
                "first_update_ts": inc_row["first_update_ts"],
                "last_update_ts": inc_row["last_update_ts"],
            }
            all_results.append(result_row)

    result_df1 = pd.DataFrame(all_results)

    if result_df1.empty:
        return pd.DataFrame(), pd.DataFrame()

    result_df2 = result_df1.groupby(["elastic_title", "data_date"], as_index=False).agg(
        digg_count=("digg_count", "sum"),
        collect_count=("collect_count", "sum"),
        share_count=("share_count", "sum"),
        pub_count=("aweme_url", "nunique"),
    )

    return result_df1, result_df2


async def save_to_database(result_df: pd.DataFrame, target_date: str) -> None:
    """保存日增数据到 douyin_aweme_day 表（upsert）"""
    if result_df.empty:
        print("⚠️ No data to save.")
        return

    save_df = result_df.copy()
    if "data_date" in save_df.columns:
        save_df["data_date"] = pd.to_datetime(save_df["data_date"]).dt.strftime(
            "%Y-%m-%d"
        )
    save_df["add_ts"] = int(datetime.now().timestamp())

    for col in ["create_time", "first_update_ts", "last_update_ts"]:
        if col in save_df.columns:
            save_df[col] = save_df[col].apply(
                lambda x: int(pd.Timestamp(x).timestamp()) if pd.notna(x) else None
            )

    save_df = save_df.fillna(value=0)

    async with get_session() as session:
        columns = save_df.columns.tolist()
        placeholders = ", ".join([f":{col}" for col in columns])
        update_set = ", ".join([f"{col} = VALUES({col})" for col in columns])

        insert_sql = text(
            f"""
            INSERT INTO douyin_aweme_day ({', '.join(columns)})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_set}
        """
        )

        await session.execute(insert_sql, save_df.to_dict(orient="records"))
        print(f"✅ 已保存 {len(save_df)} 条日增数据到 douyin_aweme_day 表（upsert）")


async def cal_day_incr(
    target_date: str, days: int = 0
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """计算指定时间段内每天的日增数据，并保存到 douyin_aweme_day 表"""
    df = fetch_douyin_data(target_date, days)
    result1, result2 = process_douyin_data(df, target_date, days)
    await save_to_database(result1, target_date)
    return result1, result2


if __name__ == "__main__":
    args = parser.parse_args()
    result1, result2 = asyncio.run(cal_day_incr(args.target_date, args.days))

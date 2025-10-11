import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime, date

# 加载 .env 文件
load_dotenv()

def get_mysql_engine():
    """
    从环境变量创建 MySQL 连接引擎
    """
    user = os.getenv("MYSQL_DB_USER")
    password = os.getenv("MYSQL_DB_PWD")
    host = os.getenv("MYSQL_DB_HOST")
    port = os.getenv("MYSQL_DB_PORT")
    db_name = os.getenv("MYSQL_DB_NAME")

    if not all([user, password, host, port, db_name]):
        missing = [k for k, v in {
            'MYSQL_DB_USER': user,
            'MYSQL_DB_PWD': password,
            'MYSQL_DB_HOST': host,
            'MYSQL_DB_PORT': port,
            'MYSQL_DB_NAME': db_name
        }.items() if v is None]
        raise EnvironmentError(f"Missing environment variables: {missing}")

    # 使用 pymysql 作为驱动
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
    engine = create_engine(database_url, echo=False)  # 可设 echo=True 查看 SQL
    return engine

def fetch_douyin_data(target_date):
    """
    从数据库读取指定日期的 douyin_aweme_summary 数据

    Parameters:
        target_date (str): 格式 '2025-10-08'

    Returns:
        pd.DataFrame
    """
    engine = get_mysql_engine()

    # 将目标日期转为微秒时间戳范围（仅用于 SQL 查询）
    target_datetime = pd.to_datetime(target_date)
    # 2. 构造上海时区的 datetime（自动处理夏令时等问题）
    tz = 'Asia/Shanghai'
    
    # 创建当天 00:00:00 上海时间
    start_dt = pd.to_datetime(target_datetime).tz_localize(tz)
    
    # 创建第二天 00:00:00 上海时间，然后减 1 微秒 得到当天最后一刻
    end_dt = start_dt + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    
    # 3. 转为毫秒级时间戳（JavaScript 可用）
    start_us = int(start_dt.timestamp() * 1_000)
    end_us = int(end_dt.timestamp() * 1_000)

    query = f"""
    SELECT 
        nickname, aweme_url, create_time, 
        digg_count, collect_count, share_count,
        elastic_title, product_title, update_ts
    FROM douyin_aweme_summary 
    WHERE elastic_title IS NOT NULL
      AND update_ts >= {start_us}
      AND update_ts <= {end_us}
    ORDER BY aweme_url, update_ts;
    """
    print(query)
    try:
        df = pd.read_sql(query, engine)
        print(f"✅ Successfully loaded {len(df)} records for date {target_date}")
        return df
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

def process_douyin_data(df, target_date):
    """
    处理数据：计算每个 aweme_url 的增量，并按 elastic_title 聚合
    特别处理：如果 aweme_url 当天只有一条数据，且 create_time 是当天，则使用原始值作为增量
    """
    if df.empty:
        print("⚠️  No data to process.")
        return pd.DataFrame(), pd.DataFrame()

    target_datetime = pd.to_datetime(target_date)
    target_data_date = target_datetime.date()

    # 确保时间字段为 datetime 类型
    df['update_ts'] = pd.to_datetime(df['update_ts'], unit='ms', errors='coerce').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    # 筛选目标日期的数据
    daily_data = df[df['update_ts'].dt.date == target_data_date].copy()

    if daily_data.empty:
        print(f"⚠️ No data found for {target_date}")
        return pd.DataFrame(), pd.DataFrame()

    # 按 aweme_url 分组
    grouped = daily_data.groupby('aweme_url')

    result_rows = []

    for aweme_url, group in grouped:
        n_records = len(group)
        # 获取最后一条记录（最新数据）
        latest = group.iloc[-1].to_dict()
        # 获取 first 和 last update_ts（用于记录）
        first_update_ts = group['update_ts'].iloc[0]
        last_update_ts = group['update_ts'].iloc[-1]

        if n_records == 1:
            # 只有一条记录
            create_date = pd.to_datetime(latest['create_time']).date()
            if create_date == target_data_date:
                # 是当天新发布的视频，使用当前值作为增量
                digg_inc = latest['digg_count']
                collect_inc = latest['collect_count']
                share_inc = latest['share_count']
            else:
                # 不是当天发布的，且只抓到一次 → 可能是抓取不完整，保守设为 0
                continue
                # digg_inc = 0
                # collect_inc = 0
                # share_inc = 0
        else:
            # 多条记录，使用首尾差值
            first_digg = group['digg_count'].iloc[0]
            first_collect = group['collect_count'].iloc[0]
            first_share = group['share_count'].iloc[0]

            last_digg = group['digg_count'].iloc[-1]
            last_collect = group['collect_count'].iloc[-1]
            last_share = group['share_count'].iloc[-1]

            digg_inc = max(0, last_digg - first_digg)
            collect_inc = max(0, last_collect - first_collect)
            share_inc = max(0, last_share - first_share)

        # 构造结果行
        result_row = {
            'nickname': latest['nickname'],
            'aweme_url': aweme_url,
            'create_time': latest['create_time'],
            'digg_count': digg_inc,
            'collect_count': collect_inc,
            'share_count': share_inc,
            'digg_tt': latest['digg_count'],
            'collect_tt': latest['collect_count'],
            'share_tt': latest['share_count'],
            'elastic_title': latest['elastic_title'],
            'product_title': latest['product_title'],
            'data_date': target_data_date,
            'first_update_ts': first_update_ts,   # 📌 首次抓取时间
            'last_update_ts': last_update_ts      # 📌 最后一次抓取时间
        }
        result_rows.append(result_row)

    # 转为 DataFrame
    result_df1 = pd.DataFrame(result_rows)

    # 步骤 2: 按 elastic_title 聚合
    result_df2 = result_df1.groupby('elastic_title', as_index=False).agg(
        digg_count=('digg_count', 'sum'),
        collect_count=('collect_count', 'sum'),
        share_count=('share_count', 'sum'),
        pub_count=('aweme_url', 'count')  # 统计视频数量
    )

    result_df2 = result_df2[[
        'elastic_title', 'digg_count', 'collect_count', 'share_count', 'pub_count'
    ]]

    return result_df1, result_df2


def cal_day_incr(target_date):
    # 1. 从数据库读取数据
    df = fetch_douyin_data(target_date)

    # 2. 处理数据
    result1, result2 = process_douyin_data(df, target_date)
    return result1, result2

# ==================== 使用示例 ====================

if __name__ == "__main__":
    target_date = "2025-10-08"  # 可改为传参或 datetime.today().strftime('%Y-%m-%d')

    # 1. 从数据库读取数据
    df = fetch_douyin_data(target_date)

    # 2. 处理数据
    result1, result2 = process_douyin_data(df, target_date)

    # 3. 输出结果
    print("\n--- 每个 aweme_url 的增量数据 (result1) ---")
    print(result1.columns)

    print("\n--- 按 elastic_title 聚合结果 (result2) ---")
    print(result2.columns)

    # 可选：导出到 CSV
    result1.to_csv(f"aweme_daily_increment_{target_date}.csv", index=False, encoding='utf-8-sig')
    result2.to_csv(f"elastic_title_summary_{target_date}.csv", index=False, encoding='utf-8-sig')
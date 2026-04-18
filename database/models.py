from sqlalchemy import create_engine, Column, Integer, Text, String, BigInteger
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BilibiliVideo(Base):
    __tablename__ = "bilibili_video"
    id = Column(Integer, primary_key=True)
    video_id = Column(BigInteger, nullable=False, index=True, unique=True)
    video_url = Column(Text, nullable=False)
    user_id = Column(BigInteger, index=True)
    nickname = Column(Text)
    avatar = Column(Text)
    liked_count = Column(Integer)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    video_type = Column(Text)
    title = Column(Text)
    desc = Column(Text)
    create_time = Column(BigInteger, index=True)
    disliked_count = Column(Text)
    video_play_count = Column(Text)
    video_favorite_count = Column(Text)
    video_share_count = Column(Text)
    video_coin_count = Column(Text)
    video_danmaku = Column(Text)
    video_comment = Column(Text)
    video_cover_url = Column(Text)
    source_keyword = Column(Text, default="")


class BilibiliVideoComment(Base):
    __tablename__ = "bilibili_video_comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    sex = Column(Text)
    sign = Column(Text)
    avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(BigInteger, index=True)
    video_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger)
    sub_comment_count = Column(Text)
    parent_comment_id = Column(String(255))
    like_count = Column(Text, default="0")


class BilibiliUpInfo(Base):
    __tablename__ = "bilibili_up_info"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    nickname = Column(Text)
    sex = Column(Text)
    sign = Column(Text)
    avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    total_fans = Column(Integer)
    total_liked = Column(Integer)
    user_rank = Column(Integer)
    is_official = Column(Integer)


class BilibiliContactInfo(Base):
    __tablename__ = "bilibili_contact_info"
    id = Column(Integer, primary_key=True)
    up_id = Column(BigInteger, index=True)
    fan_id = Column(BigInteger, index=True)
    up_name = Column(Text)
    fan_name = Column(Text)
    up_sign = Column(Text)
    fan_sign = Column(Text)
    up_avatar = Column(Text)
    fan_avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)


class BilibiliUpDynamic(Base):
    __tablename__ = "bilibili_up_dynamic"
    id = Column(Integer, primary_key=True)
    dynamic_id = Column(BigInteger, index=True)
    user_id = Column(String(255))
    user_name = Column(Text)
    text = Column(Text)
    type = Column(Text)
    pub_ts = Column(BigInteger)
    total_comments = Column(Integer)
    total_forwards = Column(Integer)
    total_liked = Column(Integer)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)


class DouyinAweme(Base):
    __tablename__ = "douyin_aweme"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    sec_uid = Column(String(255))
    short_user_id = Column(String(255))
    user_unique_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    user_signature = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    aweme_id = Column(BigInteger, index=True)
    aweme_type = Column(Text)
    title = Column(Text)
    desc = Column(Text)
    create_time = Column(BigInteger, index=True)
    liked_count = Column(Text)
    comment_count = Column(Text)
    share_count = Column(Text)
    collected_count = Column(Text)
    aweme_url = Column(Text)
    cover_url = Column(Text)
    video_download_url = Column(Text)
    music_download_url = Column(Text)
    note_download_url = Column(Text)
    source_keyword = Column(Text, default="")


class DouyinAwemeSummary(Base):
    """
    抖音视频信息及关联商品信息模型。
    对应 JSON 数据结构，主键为 aweme_id 和 update_ts。
    """

    __tablename__ = "douyin_aweme_summary"

    # --- 主键字段 ---
    aweme_id = Column(BigInteger, nullable=False, comment="视频ID")
    update_ts = Column(BigInteger, nullable=False, comment="更新时间戳（毫秒）")

    # --- 用户信息 ---
    sec_uid = Column(String(255), nullable=True, comment="用户加密ID")
    nickname = Column(Text, nullable=True, comment="用户昵称")
    avatar = Column(Text, nullable=True, comment="用户头像URL")

    # --- 视频信息 ---
    aweme_type = Column(String(50), nullable=True, comment="视频类型")
    title = Column(Text, nullable=True, comment="视频标题")
    desc = Column(Text, nullable=True, comment="视频描述")
    create_time = Column(BigInteger, nullable=True, comment="创建时间（秒级时间戳）")

    # --- 统计信息 ---
    recommend_count = Column(Integer, nullable=False, default=0, comment="推荐数")
    comment_count = Column(Integer, nullable=False, default=0, comment="评论数")
    digg_count = Column(Integer, nullable=False, default=0, comment="点赞数")
    admire_count = Column(Integer, nullable=False, default=0, comment="喜欢数")
    play_count = Column(Integer, nullable=False, default=0, comment="播放数")
    share_count = Column(Integer, nullable=False, default=0, comment="分享数")
    collect_count = Column(Integer, nullable=False, default=0, comment="收藏数")

    # --- URL 信息 ---
    aweme_url = Column(Text, nullable=True, comment="视频页面URL")
    cover_url = Column(Text, nullable=True, comment="封面图URL")
    video_download_url = Column(Text, nullable=True, comment="视频下载URL")
    music_download_url = Column(Text, nullable=True, comment="音乐下载URL")
    note_download_url = Column(Text, nullable=True, comment="图文下载URL")

    # --- 商品信息 ---
    promotion_id = Column(String(255), nullable=True, comment="推广ID")
    product_id = Column(String(255), nullable=True, comment="商品ID")
    product_title = Column(Text, nullable=True, comment="商品标题")
    price = Column(Integer, nullable=False, default=0, comment="商品价格（单位：分）")
    sales = Column(Integer, nullable=False, default=0, comment="销量")
    elastic_title = Column(Text, nullable=True, comment="商品弹性标题")
    first_cname = Column(String(255), nullable=True, default="", comment="商品一级分类")
    second_cname = Column(String(255), nullable=True, default="", comment="商品二级分类")
    third_cname = Column(String(255), nullable=True, default="", comment="商品三级分类")

    # --- 定义联合主键 ---
    __table_args__ = (
        PrimaryKeyConstraint("aweme_id", "update_ts"),
        # 可以在这里添加其他索引或约束
        # 例如: Index('idx_create_time', 'create_time'),
    )


class DouyinAwemeComment(Base):
    __tablename__ = "douyin_aweme_comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    sec_uid = Column(String(255))
    short_user_id = Column(String(255))
    user_unique_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    user_signature = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(BigInteger, index=True)
    aweme_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger)
    sub_comment_count = Column(Text)
    parent_comment_id = Column(String(255))
    like_count = Column(Text, default="0")
    pictures = Column(Text, default="")


class DyCreator(Base):
    __tablename__ = "dy_creator"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    desc = Column(Text)
    gender = Column(Text)
    follows = Column(Text)
    fans = Column(Text)
    interaction = Column(Text)
    videos_count = Column(String(255))


class DyCrawlerCreator(Base):
    """用于存储待抓取的抖音创作者ID列表"""

    __tablename__ = "dy_crawler_creator"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True, unique=True)
    nickname = Column(Text)
    add_ts = Column(BigInteger)
    is_enabled = Column(Integer, default=1)  # 1: 启用, 0: 禁用


class KuaishouVideo(Base):
    __tablename__ = "kuaishou_video"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(64))
    nickname = Column(Text)
    avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    video_id = Column(String(255), index=True)
    video_type = Column(Text)
    title = Column(Text)
    desc = Column(Text)
    create_time = Column(BigInteger, index=True)
    liked_count = Column(Text)
    viewd_count = Column(Text)
    video_url = Column(Text)
    video_cover_url = Column(Text)
    video_play_url = Column(Text)
    source_keyword = Column(Text, default="")


class KuaishouVideoComment(Base):
    __tablename__ = "kuaishou_video_comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(Text)
    nickname = Column(Text)
    avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(BigInteger, index=True)
    video_id = Column(String(255), index=True)
    content = Column(Text)
    create_time = Column(BigInteger)
    sub_comment_count = Column(Text)


class WeiboNote(Base):
    __tablename__ = "weibo_note"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    gender = Column(Text)
    profile_url = Column(Text)
    ip_location = Column(Text, default="")
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    note_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger, index=True)
    create_date_time = Column(String(255), index=True)
    liked_count = Column(Text)
    comments_count = Column(Text)
    shared_count = Column(Text)
    note_url = Column(Text)
    source_keyword = Column(Text, default="")


class WeiboNoteComment(Base):
    __tablename__ = "weibo_note_comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    gender = Column(Text)
    profile_url = Column(Text)
    ip_location = Column(Text, default="")
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(BigInteger, index=True)
    note_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger)
    create_date_time = Column(String(255), index=True)
    comment_like_count = Column(Text)
    sub_comment_count = Column(Text)
    parent_comment_id = Column(String(255))


class WeiboCreator(Base):
    __tablename__ = "weibo_creator"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    desc = Column(Text)
    gender = Column(Text)
    follows = Column(Text)
    fans = Column(Text)
    tag_list = Column(Text)


class XhsCreator(Base):
    __tablename__ = "xhs_creator"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    desc = Column(Text)
    gender = Column(Text)
    follows = Column(Text)
    fans = Column(Text)
    interaction = Column(Text)
    tag_list = Column(Text)


class XhsNote(Base):
    __tablename__ = "xhs_note"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    note_id = Column(String(255), index=True)
    type = Column(Text)
    title = Column(Text)
    desc = Column(Text)
    video_url = Column(Text)
    time = Column(BigInteger, index=True)
    last_update_time = Column(BigInteger)
    liked_count = Column(Text)
    collected_count = Column(Text)
    comment_count = Column(Text)
    share_count = Column(Text)
    image_list = Column(Text)
    tag_list = Column(Text)
    note_url = Column(Text)
    source_keyword = Column(Text, default="")
    xsec_token = Column(Text)


class XhsNoteComment(Base):
    __tablename__ = "xhs_note_comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(String(255), index=True)
    create_time = Column(BigInteger, index=True)
    note_id = Column(String(255))
    content = Column(Text)
    sub_comment_count = Column(Integer)
    pictures = Column(Text)
    parent_comment_id = Column(String(255))
    like_count = Column(Text)


class TiebaNote(Base):
    __tablename__ = "tieba_note"
    id = Column(Integer, primary_key=True)
    note_id = Column(String(644), index=True)
    title = Column(Text)
    desc = Column(Text)
    note_url = Column(Text)
    publish_time = Column(String(255), index=True)
    user_link = Column(Text, default="")
    user_nickname = Column(Text, default="")
    user_avatar = Column(Text, default="")
    tieba_id = Column(String(255), default="")
    tieba_name = Column(Text)
    tieba_link = Column(Text)
    total_replay_num = Column(Integer, default=0)
    total_replay_page = Column(Integer, default=0)
    ip_location = Column(Text, default="")
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    source_keyword = Column(Text, default="")


class TiebaComment(Base):
    __tablename__ = "tieba_comment"
    id = Column(Integer, primary_key=True)
    comment_id = Column(String(255), index=True)
    parent_comment_id = Column(String(255), default="")
    content = Column(Text)
    user_link = Column(Text, default="")
    user_nickname = Column(Text, default="")
    user_avatar = Column(Text, default="")
    tieba_id = Column(String(255), default="")
    tieba_name = Column(Text)
    tieba_link = Column(Text)
    publish_time = Column(String(255), index=True)
    ip_location = Column(Text, default="")
    sub_comment_count = Column(Integer, default=0)
    note_id = Column(String(255), index=True)
    note_url = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)


class TiebaCreator(Base):
    __tablename__ = "tieba_creator"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(64))
    user_name = Column(Text)
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    gender = Column(Text)
    follows = Column(Text)
    fans = Column(Text)
    registration_duration = Column(Text)


class ZhihuContent(Base):
    __tablename__ = "zhihu_content"
    id = Column(Integer, primary_key=True)
    content_id = Column(String(64), index=True)
    content_type = Column(Text)
    content_text = Column(Text)
    content_url = Column(Text)
    question_id = Column(String(255))
    title = Column(Text)
    desc = Column(Text)
    created_time = Column(String(32), index=True)
    updated_time = Column(Text)
    voteup_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    source_keyword = Column(Text)
    user_id = Column(String(255))
    user_link = Column(Text)
    user_nickname = Column(Text)
    user_avatar = Column(Text)
    user_url_token = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)

    # persist-1<persist1@126.com>
    # 原因：修复 ORM 模型定义错误，确保与数据库表结构一致。
    # 副作用：无
    # 回滚策略：还原此行


class ZhihuComment(Base):
    __tablename__ = "zhihu_comment"
    id = Column(Integer, primary_key=True)
    comment_id = Column(String(64), index=True)
    parent_comment_id = Column(String(64))
    content = Column(Text)
    publish_time = Column(String(32), index=True)
    ip_location = Column(Text)
    sub_comment_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    content_id = Column(String(64), index=True)
    content_type = Column(Text)
    user_id = Column(String(64))
    user_link = Column(Text)
    user_nickname = Column(Text)
    user_avatar = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)


class ZhihuCreator(Base):
    __tablename__ = "zhihu_creator"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), unique=True, index=True)
    user_link = Column(Text)
    user_nickname = Column(Text)
    user_avatar = Column(Text)
    url_token = Column(Text)
    gender = Column(Text)
    ip_location = Column(Text)
    follows = Column(Integer, default=0)
    fans = Column(Integer, default=0)
    anwser_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    article_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    get_voteup_count = Column(Integer, default=0)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)


class DouyinAwemeDay(Base):
    __tablename__ = "douyin_aweme_day"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aweme_id = Column(String(64), nullable=False, index=True, comment="视频ID")
    data_date = Column(String(10), nullable=False, comment="数据日期，格式YYYY-MM-DD")
    sec_uid = Column(String(255), nullable=True, comment="用户sec_uid")
    nickname = Column(Text, nullable=True, comment="用户昵称")
    aweme_url = Column(Text, nullable=True, comment="视频URL")
    create_time = Column(BigInteger, nullable=True, comment="视频创建时间")
    elastic_title = Column(Text, nullable=True, comment="视频标题（用于聚合）")
    product_id = Column(String(255), nullable=True, comment="商品ID")
    product_title = Column(Text, nullable=True, comment="商品标题")
    first_cname = Column(String(255), nullable=True, default="", comment="商品一级分类")
    second_cname = Column(String(255), nullable=True, default="", comment="商品二级分类")
    third_cname = Column(String(255), nullable=True, default="", comment="商品三级分类")
    digg_count = Column(Integer, nullable=False, default=0, comment="日增点赞")
    collect_count = Column(Integer, nullable=False, default=0, comment="日增收藏")
    share_count = Column(Integer, nullable=False, default=0, comment="日增转发")
    digg_tt = Column(Integer, nullable=False, default=0, comment="当前总点赞")
    collect_tt = Column(Integer, nullable=False, default=0, comment="当前总收藏")
    share_tt = Column(Integer, nullable=False, default=0, comment="当前总转发")
    comment_count = Column(Integer, nullable=False, default=0, comment="当前总评论")
    first_update_ts = Column(BigInteger, nullable=True, comment="首次抓取时间")
    last_update_ts = Column(BigInteger, nullable=True, comment="最后一次抓取时间")
    add_ts = Column(BigInteger, nullable=True, comment="记录添加时间")
    # 联合唯一索引，防止重复插入同一天的数据
    __table_args__ = (
        UniqueConstraint("aweme_id", "data_date", name="uq_aweme_id_data_date"),
        Index("idx_data_date", "data_date"),
        Index("idx_sec_uid", "sec_uid"),
    )

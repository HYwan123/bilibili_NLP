import json
import uuid
from typing import Optional
from fastapi import Depends, status, APIRouter, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
import logging

from app.database.redis_client import RedisClient
from app.database import mysql_database as database
from app.api.user import get_current_user
from app.database.mysql_exceptions import create_error_response, log_error
from app.utils.bilibili import (
    get_video_comments,
    get_cookies_from_user,
    video_recommendation,
    analyze_user_profiles,
    get_user_comments,
    analyze_user_profiles,
)
from app.schemas.api import CookieData, ChatRequest
from app.utils.agent.openai_client import OpenaiClient
from app.schemas.user import User
import app.utils.bilibili.analyze_video_comments as comment_analysis

# Configure logging
logger = logging.getLogger(__name__)


router = APIRouter()
global_redis = RedisClient()


@router.get("/select/{BV}")
async def select_BV(BV: str, current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Select BV request by user {current_user.username} for BV: {BV}")
        result = await get_video_comments.select_by_BV(BV)
        global_redis.redis_value_add("leiji")
        if result:
            comment_texts = [
                comment.get("comment_text", "")
                for comment in result
                if comment.get("comment_text")
            ]
            if comment_texts:
                summary = f"爬取到 {len(comment_texts)} 条评论，前3条: " + " | ".join(
                    comment_texts[:3]
                )
                if len(comment_texts) > 3:
                    summary += f" ... (还有 {len(comment_texts) - 3} 条)"
            else:
                summary = "未获取到评论内容"
        else:
            summary = "查询失败，未获取到数据"
        database.add_bv_history(BV, current_user.username, summary)

        if result:
            logger.info(f"Successfully retrieved comments for BV: {BV}")
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": result},
            )
        else:
            logger.warning(f"No data found for BV: {BV}")
            return create_error_response(404, "Not Found")
    except Exception as e:
        logger.error(f"Error retrieving BV {BV}: {e}")
        log_error(e, "select_BV")
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@router.get("/history_data")
async def history_data():
    history_data = {
        "leiji": int(global_redis.redis_select_by_key("leiji")),  # type: ignore
        "chuli": int(global_redis.redis_select_by_key("chuli")),  # type: ignore
        "huaxiang": int(global_redis.redis_select_by_key("huaxiang")),  # type: ignore
    }
    return JSONResponse(
        status_code=200,
        content={"code": 200, "message": "success", "data": history_data},
    )


@router.get("/get_cookies")
async def get_cookies():
    cookies = {
        "cookie": str(global_redis.redis_select_by_key("cookie")),  # type: ignore
        "video_select_cookie": str(
            global_redis.redis_select_by_key("video_select_cookie")
        ),  # type: ignore
    }
    return JSONResponse(
        status_code=200, content={"code": 200, "message": "success", "data": cookies}
    )


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: str = Query(
        "all", pattern="^(all|bv|uuid)$", description="历史类型: all/bv/uuid"
    ),
    current_user: User = Depends(get_current_user),
):
    history_data = await database.get_history_by_user(
        user_id=current_user.id, page=page, page_size=page_size, history_type=type
    )
    return JSONResponse(
        status_code=200,
        content={"code": 200, "message": "success", "data": history_data},
    )


@router.get("/get_uids")
async def get_uids(current_user: User = Depends(get_current_user)):
    data = database.get_user_report()
    return {"code": 200, "data": data, "message": "成功"}


@router.post("/change_cookie_user")
async def change_user_cookie(data: CookieData):
    global_redis.redis_set_by_key("cookie", data.cookie)
    return {"code": 200, "message": "修改成功"}


@router.post("/user/comments/{uid}")
async def get_user_comments_resp(
    uid: str, current_user: User = Depends(get_current_user)
):
    global_redis.redis_value_add("leiji")

    """
    直接获取用户评论并保存到数据库
    """
    try:
        logger.info(f"用户 {current_user.username} 请求获取用户 {uid} 的评论")

        # 直接调用评论获取函数
        comments = get_user_comments.get_user_comments_simple(uid)

        if comments:
            logger.info(f"成功获取 {len(comments)} 条评论，准备保存到数据库")
            # 保存到数据库
            success = database.save_user_comments(uid, current_user.username, comments)
            # Restore UID history saving
            try:
                database.add_uuid_history(uid, current_user.username, "none", f"获取到 {len(comments)} 条评论")
            except Exception as e:
                logger.error(f"Failed to add UID history: {e}")
            
            if success:
                logger.info(f"评论数据已成功保存到数据库")
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 200,
                        "message": "success",
                        "data": {
                            "uid": uid,
                            "comment_count": len(comments),
                            "comments": comments,
                        },
                    },
                )
            else:
                logger.error(f"保存到数据库失败 for user {uid}")
                return create_error_response(500, "保存到数据库失败")
        else:
            logger.warning(f"未获取到用户 {uid} 的评论数据")
            return create_error_response(
                404, "未找到该用户的评论数据，可能是API访问限制或用户无评论"
            )

    except Exception as e:
        logger.error(f"获取用户评论失败: {e}")
        log_error(e, "get_user_comments")
        return create_error_response(500, f"获取评论失败: {str(e)}")


@router.get("/user/comments/{uid}")
async def get_saved_user_comments(
    uid: str, current_user: User = Depends(get_current_user)
):
    """
    获取用户评论数据
    优先从数据库获取，如果没有则自动从B站实时获取并保存
    """
    try:
        # 首先尝试从数据库获取
        comments = database.get_user_comments(uid)

        if comments:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": comments},
            )

        # 数据库中没有，尝试从B站实时获取
        logger.info(f"数据库中未找到用户 {uid} 的评论，尝试实时获取")
        comments = get_user_comments.get_user_comments_simple(uid)

        if comments and len(comments) > 0:
            # 保存到数据库
            success = database.save_user_comments(uid, current_user.username, comments)
            if success:
                logger.info(f"成功获取并保存用户 {uid} 的 {len(comments)} 条评论")
            return JSONResponse(
                status_code=200,
                content={
                    "code": 200,
                    "message": "success",
                    "data": comments,
                    "source": "bilibili",  # 标识数据来源
                },
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "message": "未找到该用户的评论数据",
                    "data": None,
                },
            )

    except Exception as e:
        logger.error(f"获取用户 {uid} 评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"获取评论失败: {str(e)}", "data": None},
        )


@router.get("/user/comments/redis/{uid}")
async def get_user_comments_redis(
    uid: str, current_user: User = Depends(get_current_user)
):
    global_redis.redis_value_add("leiji")
    """
    从Redis获取已保存的用户评论数据
    """
    try:
        comments = analyze_user_profiles.get_user_comments_from_redis(uid)
        if comments:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": comments},
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "message": "未找到该用户的评论数据",
                    "data": None,
                },
            )
    except Exception as e:
        print(f"获取Redis评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"获取评论失败: {str(e)}", "data": None},
        )


from typing import Optional


@router.post("/user/analyze/{uid}")
async def analyze_user_portrait_resp(
    uid: str,
    current_user: User = Depends(get_current_user),
):
    """
    分析用户评论，生成用户画像
    """
    global_redis.redis_value_add("huaxiang")

    try:
        logger.info(f"用户画像分析请求 by user {current_user.username} for uid: {uid}")

        result = await analyze_user_profiles.analyze_user_comments(uid)

        if "error" in result:
            logger.warning(f"用户画像分析错误 for uid {uid}: {result['error']}")
            return create_error_response(400, result["error"])
            
        # Add to history
        try:
            summary = "用户画像分析完成"
            if "comment_count" in result:
                summary = f"用户画像分析完成 ({result['comment_count']} 条评论)"
            database.add_uuid_history(uid, current_user.username, "none", summary)
        except Exception as e:
            logger.error(f"Failed to save UID history: {e}")
            
        if "msg" in result:
            logger.info(f"用户画像分析完成 for uid {uid}")
            return JSONResponse(
                status_code=200,
                content={
                    "code": 200,
                    "message": result["msg"],
                    "data": global_redis.redis_select(f"analysis_{uid}"),
                },
            )
        logger.info(f"用户画像分析成功 for uid {uid}")
        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "分析完成", "data": result},
        )

    except Exception as e:
        logger.error(f"用户画像分析失败: {e}")
        log_error(e, "analyze_user_portrait")
        return create_error_response(500, f"分析失败: {str(e)}")


@router.get("/user/analysis/{uid}")
async def get_user_analysis(uid: str, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add("huaxiang")
    """
    获取用户画像分析结果
    """
    try:
        result = analyze_user_profiles.get_user_analysis_from_redis(uid)

        if result:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": result},
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"code": 404, "message": "未找到分析结果", "data": None},
            )

    except Exception as e:
        print(f"获取分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"获取失败: {str(e)}", "data": None},
        )


# --- Background Task for Comment Analysis ---
async def run_comment_analysis_task(bv_id: str, job_id: str, username: str):
    """
    The actual analysis function that runs in the background.
    """
    redis_handler = global_redis
    try:
        logger.info(
            f"Starting comment analysis task for BV: {bv_id}, job_id: {job_id}, user: {username}"
        )
        # 1. Update status: Fetching comments
        status_update = {
            "status": "Processing",
            "progress": 20,
            "details": f"正在获取视频 {bv_id} 的评论...",
        }
        redis_handler.set_job_status(job_id, status_update)

        comments = await get_video_comments.select_by_BV(bv_id)
        if not comments:
            raise ValueError(
                f"未找到视频 {bv_id} 的评论数据，请检查BV号是否正确或稍后再试。"
            )

        # 2. Update status: Analyzing comments
        status_update = {
            "status": "Processing",
            "progress": 60,
            "details": f"已获取 {len(comments)} 条评论，正在进行智能分析...",
        }
        redis_handler.set_job_status(job_id, status_update)

        analysis_result = await comment_analysis.analyze_bv_comments(bv_id, comments)

        if "error" in analysis_result:
            raise Exception(analysis_result["error"])

        # 3. Update status: Completed
        status_update = {
            "status": "Completed",
            "progress": 100,
            "details": f"视频 {bv_id} 评论分析完成",
            "result": analysis_result,
        }
        redis_handler.set_job_status(job_id, status_update)
        logger.info(f"Comment analysis completed successfully for BV: {bv_id}")

        # 4. Save to history
        try:
            summary = f"智能分析完成: 处理了 {len(comments)} 条评论"
            if "basic_stats" in analysis_result:
                stats = analysis_result["basic_stats"]
                total = stats.get("total_comments", len(comments))
                sentiment = analysis_result.get("sentiment_analysis", {})
                pos = sentiment.get("positive", 0)
                neg = sentiment.get("negative", 0)
                neu = sentiment.get("neutral", 0)
                total_s = pos + neg + neu
                if total_s > 0:
                    pos_rate = (pos / total_s) * 100
                    summary = f"智能分析完成: {total}条评论, 正向率 {pos_rate:.1f}%"
                else:
                    summary = f"智能分析完成: {total}条评论"

            database.add_bv_history(bv_id, username, summary)
            logger.info(f"Saved analysis history for BV: {bv_id}, user: {username}")
        except Exception as history_error:
            logger.error(f"Failed to save analysis history: {history_error}")

    except Exception as e:
        error_message = f"评论分析任务失败: {e}"
        logger.error(error_message)
        log_error(e, "run_comment_analysis_task")
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
    finally:
        # Task finished, always release the lock
        lock_key = f"lock:analyze_bv:{bv_id}"
        # 直接使用全局redis客户端强制删除锁，避免比较value导致失败
        global_redis.get_client().delete(lock_key)
        logger.info(f"Released lock for BV: {bv_id}")


# --- 评论分析相关API ---
@router.post("/comments/analyze/submit/{bv_id}")
async def submit_comment_analysis_job(
    bv_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """
    Submits a comment analysis job. Checks for cached results first.
    If no cache, runs the job in the background and prevents duplicates with a lock.
    """
    # 1. Check for a cached result first
    global_redis.redis_value_add("chuli")
    cached_result = await comment_analysis.get_bv_analysis(bv_id)
    if cached_result:
        print(f"Cache hit for analysis of BV: {bv_id}. Returning cached result.")
        # Even if cached, we might want to update history timestamp
        try:
            summary = "从缓存获取分析结果"
            if "basic_stats" in cached_result:
                total = cached_result["basic_stats"].get("total_comments", "未知")
                summary = f"智能分析: 处理了 {total} 条评论"
            database.add_bv_history(bv_id, current_user.username, summary)
        except Exception as e:
            logger.error(f"Failed to update history for cached result: {e}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 200,
                "message": "已从缓存获取分析结果",
                "data": cached_result,
            },
        )

    # 2. If no cache, proceed with locking and job submission
    redis_handler = RedisClient()
    lock_key = f"lock:analyze_bv:{bv_id}"
    job_id = f"analyze_bv_{bv_id}_{uuid.uuid4().hex[:8]}"

    if not redis_handler.acquire_lock(lock_key, job_id, timeout=300):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": 409,
                "message": "该视频的分析任务已在进行中，请稍后再试。",
                "data": None,
            },
        )

    background_tasks.add_task(
        run_comment_analysis_task, bv_id, job_id, current_user.username
    )

    return JSONResponse(
        status_code=202,  # HTTP 202 Accepted
        content={
            "code": 202,
            "message": "分析任务已提交，将在后台进行处理。",
            "data": {"job_id": job_id},
        },
    )


@router.get("/comments/analysis/{bv_id}")
async def get_comment_analysis(
    bv_id: str, current_user: User = Depends(get_current_user)
):
    global_redis.redis_value_add("chuli")
    """
    获取指定BV视频的评论分析结果
    """
    try:
        result = await comment_analysis.get_bv_analysis(bv_id)

        if result:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": result},
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"code": 404, "message": "未找到评论分析结果", "data": None},
            )

    except Exception as e:
        print(f"获取评论分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"获取失败: {str(e)}", "data": None},
        )


# --- 内容推荐相关API(V2) ---
@router.post("/start_tuijian/{uid}")
async def video_by_user(uid: str, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add("chuli")

    result = await video_recommendation.get_tuijian_bvs(uid)
    print(result)
    if result is not None:
        global_redis.redis_set_by_key(f"{uid}_videos", result)
        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "推荐生成成功", "data": result},
        )

    else:
        return JSONResponse(
            status_code=404, content={"code": 404, "message": "推荐生成失败"}
        )


@router.get("/get_tuijian_video_info/{uid}")
async def get_video_by_user(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add("chuli")

    try:
        # 从Redis获取存储的BV列表
        bv_data = global_redis.redis_select_by_key(f"{uid}_videos")
        if not bv_data:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "message": "未找到该用户的推荐视频数据，请先生成推荐",
                },
            )

        # 解析JSON数据
        bvs = json.loads(bv_data)
        bv_dict = {}

        # 获取每个BV号的视频信息
        for bv in bvs:
            video_info = await video_recommendation.get_video_info(bv)
            if video_info:
                bv_dict[bv] = video_info

        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "获取成功", "data": bv_dict},
        )

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "数据格式错误，无法解析推荐视频数据"},
        )
    except Exception as e:
        print(f"获取视频详情失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"获取视频详情失败: {str(e)}"},
        )


@router.post("/insert_vector/{bv_id}")
async def insert_vector_by_bv(
    bv_id: str, current_user: User = Depends(get_current_user)
):
    """
    将指定BV号的视频标签向量插入到向量数据库
    """
    try:
        await video_recommendation.insert_vector_by_BV(bv_id)
        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "向量插入成功", "data": {"bv_id": bv_id}},
        )
    except Exception as e:
        print(f"插入向量失败: {e}")
        return JSONResponse(
            status_code=500, content={"code": 500, "message": f"插入向量失败: {str(e)}"}
        )


@router.get("/video/info/{bv_id}")
async def get_video_info(bv_id: str, current_user: User = Depends(get_current_user)):
    """
    获取单个视频的详细信息
    """
    try:
        video_info = await video_recommendation.get_video_info(bv_id)
        print(video_info)
        if video_info.get("msg") == "OK":
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "success", "data": video_info},
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"code": 404, "message": "获取视频信息失败", "data": None},
            )
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"获取视频信息失败: {str(e)}",
                "data": None,
            },
        )


# --- Bilibili QR Code Login Endpoints ---
@router.post("/bilibili/qrcode/generate")
async def generate_bilibili_qrcode_endpoint(
    current_user: User = Depends(get_current_user),
):
    """
    生成Bilibili登录二维码
    """
    try:
        logger.info(f"用户 {current_user.username} 请求生成Bilibili登录二维码")
        qrcode_data = await get_cookies_from_user.generate_bilibili_qrcode()

        # Store qrcode_key in Redis with user ID for later polling
        global_redis.redis_set_by_key(
            f"qrcode_key_{current_user.id}", qrcode_data["qrcode_key"]
        )

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "二维码生成成功",
                "data": {
                    "qrcode_key": qrcode_data["qrcode_key"],
                    "url": qrcode_data["url"],
                },
            },
        )
    except Exception as e:
        logger.error(f"生成Bilibili二维码失败: {e}")
        log_error(e, "generate_bilibili_qrcode_endpoint")
        return create_error_response(500, f"生成二维码失败: {str(e)}")


@router.post("/bilibili/qrcode/poll")
async def poll_bilibili_login_endpoint(current_user: User = Depends(get_current_user)):
    """
    轮询Bilibili登录状态
    """
    try:
        logger.info(f"用户 {current_user.username} 请求轮询Bilibili登录状态")

        # Get qrcode_key from Redis using user ID
        qrcode_key_raw = global_redis.redis_select_by_key(
            f"qrcode_key_{current_user.id}"
        )
        if isinstance(qrcode_key_raw, bytes):
            qrcode_key = qrcode_key_raw.decode("utf-8")
        else:
            qrcode_key = qrcode_key_raw
        logger.info(qrcode_key)
        if not qrcode_key:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "message": "未找到二维码密钥，请先生成二维码",
                    "data": None,
                },
            )

        # Poll login status
        login_result = await get_cookies_from_user.poll_bilibili_login(qrcode_key)

        # Check if login was successful (code 0 in data)
        if login_result["data"].get("code") == 0 and login_result["data"].get("url"):
            # Extract SESSDATA and bili_jct from the login URL
            url = login_result["data"]["url"]
            session_data = get_cookies_from_user.extract_sessdata_from_url(url)

            if session_data:
                # Update the cookie in Redis with the new SESSDATA and bili_jct
                # Get existing cookie and update it
                existing_cookie = global_redis.redis_select_by_key("cookie") or ""
                if isinstance(existing_cookie, bytes):
                    existing_cookie = existing_cookie.decode("utf-8")

                # Create new cookie string with updated SESSDATA and bili_jct
                if existing_cookie:
                    # Parse existing cookie and update SESSDATA and bili_jct
                    cookie_pairs = existing_cookie.split("; ")
                    updated_pairs = []
                    sessdata_updated = False
                    bili_jct_updated = False

                    for pair in cookie_pairs:
                        if pair.startswith("SESSDATA="):
                            updated_pairs.append(f"SESSDATA={session_data['sessdata']}")
                            sessdata_updated = True
                        elif pair.startswith("bili_jct="):
                            updated_pairs.append(f"bili_jct={session_data['bili_jct']}")
                            bili_jct_updated = True
                        else:
                            updated_pairs.append(pair)

                    # Add SESSDATA and bili_jct if they weren't in the existing cookie
                    if not sessdata_updated:
                        updated_pairs.append(f"SESSDATA={session_data['sessdata']}")
                    if not bili_jct_updated:
                        updated_pairs.append(f"bili_jct={session_data['bili_jct']}")

                    new_cookie = "; ".join(updated_pairs)
                else:
                    # Create new cookie with just SESSDATA and bili_jct
                    new_cookie = f"SESSDATA={session_data['sessdata']}; bili_jct={session_data['bili_jct']}"

                # Save the updated cookie to Redis
                global_redis.redis_set_by_key("cookie", new_cookie)

                logger.info(
                    f"用户 {current_user.username} Bilibili登录成功，已更新cookie"
                )

                # Return success response with session data
                login_result["data"]["session_data"] = session_data
                login_result["data"]["cookie_updated"] = True

        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "轮询成功", "data": login_result["data"]},
        )
    except Exception as e:
        logger.error(f"轮询Bilibili登录状态失败: {e}")
        log_error(e, "poll_bilibili_login_endpoint")
        return create_error_response(500, f"轮询登录状态失败: {str(e)}")


# --- 默认AI系统提示词 ---
DEFAULT_SYSTEM_PROMPT = """# 角色
你是一个专门针对 B 站（Bilibili）数据分析的资深 NLP 专家助手。你拥有深厚的内容理解、用户画像构建、情感分析以及推荐系统领域的知识。

# 核心功能背景
本系统名为 bilibili-nlp，旨在通过数据科学手段挖掘 B 站视频背后的价值。主要功能包括：
1. **视频评论分析**：提取关键词、进行细粒度的情感极性分类（积极、消极、中性），并总结用户核心观点。
2. **用户画像分析**：基于互动行为（评论、点赞、投币、收藏等）构建粉丝群体特征，识别用户偏好、活跃时段和粉丝粘性。
3. **内容推荐**：通过标签关联和语义分析，为用户提供精准的内容推荐建议。
4. **趋势洞察**：分析弹幕热度和热门话题，帮助创作者把握流量趋势。

# 交互准则
1. **专业性**：在回答相关领域问题时，应使用诸如“分词”、“词频分析”、“LDA 主题模型”、“情感分值”、“用户留存”等专业术语，但要确保解释易懂。
2. **场景化建议**：不仅仅是回答问题，还要能根据 B 站特有的社区氛围（梗文化、弹幕礼仪等）给出运营或分析建议。
3. **简洁高效**：回答应直击要点，避免冗余，除非用户要求深入分析，否则通常控制在 300 字以内。
4. **准确性**：基于已知功能回答。若涉及系统未实现的功能，应礼貌说明。
5. **代码示例**：如果用户询问技术实现细节，请提供简洁的 Python (FastAPI/Request) 或 Vue.js 代码示例。"""


# --- AI 问答相关API ---
@router.post("/chat")
async def chat_with_ai(
    chat_request: ChatRequest, current_user: User = Depends(get_current_user)
):
    """
    AI问答接口 - 使用OpenAI客户端进行对话
    """
    try:
        logger.info(f"用户 {current_user.username} 发起AI问答请求")

        # 初始化OpenAI客户端
        client = OpenaiClient()

        # 转换消息格式
        messages = [
            {"role": msg.role, "content": msg.content} for msg in chat_request.messages
        ]

        # 获取系统提示词
        system_prompt = chat_request.system_prompt or DEFAULT_SYSTEM_PROMPT

        # 调用AI接口
        response = await client.chat(
            messages=messages,
            model="glm-4.7-flash",  # 锁定使用GLM模型，不使用前端传入的模型
            system_prompt=system_prompt
        )

        # 提取AI回复内容
        try:
            ai_message = client.get_message(response)
            ai_content = client.get_message_content(response)
        except TypeError:
            # 如果响应格式不正确，返回错误
            logger.error("AI响应格式错误")
            return create_error_response(500, "AI响应格式错误")

        logger.info(f"AI问答成功，用户: {current_user.username}")

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success",
                "data": {
                    "message": ai_message,
                    "content": ai_content,
                    "model": chat_request.model or "glm-4.7-flash",
                },
            },
        )

    except Exception as e:
        logger.error(f"AI问答失败: {e}")
        log_error(e, "chat_with_ai")
        return create_error_response(500, f"AI问答失败: {str(e)}")


@router.post("/chat/simple")
async def chat_with_ai_simple(
    text: str, current_user: User = Depends(get_current_user)
):
    """
    AI简单问答接口 - 单条消息快速回复
    """
    try:
        logger.info(f"用户 {current_user.username} 发起简单AI问答: {text[:50]}...")

        # 初始化OpenAI客户端
        client = OpenaiClient()

        # 调用AI接口
        response = await client.one_chat(
            text=text,
            system_prompt=DEFAULT_SYSTEM_PROMPT
        )

        # 提取AI回复内容
        ai_content = client.get_message_content(response)

        logger.info(f"简单AI问答成功，用户: {current_user.username}")

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success",
                "data": {"content": ai_content, "role": "assistant"},
            },
        )

    except Exception as e:
        logger.error(f"简单AI问答失败: {e}")
        log_error(e, "chat_with_ai_simple")
        return create_error_response(500, f"AI问答失败: {str(e)}")


@router.post("/chat/stream")
async def chat_with_ai_stream(
    chat_request: ChatRequest, current_user: User = Depends(get_current_user)
):
    """
    AI问答接口 - 流式输出
    """

    async def generate_stream():
        try:
            logger.info(f"用户 {current_user.username} 发起AI流式问答请求")

            # 初始化OpenAI客户端
            client = OpenaiClient()

            # 转换消息格式
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_request.messages
            ]

            # 获取系统提示词，如果没有提供则使用默认提示词
            system_prompt = chat_request.system_prompt or DEFAULT_SYSTEM_PROMPT

            logger.info(f"准备调用AI流式接口，消息数: {len(messages)}")

            # 流式调用AI接口
            chunk_count = 0
            try:
                # 使用 OpenAI 客户端的流式方法
                # 注意：由于 zai-sdk 可能阻塞，我们在这里添加日志
                async for content in client.chat_stream(
                    messages=messages,
                    model="glm-4.7-flash",
                    system_prompt=system_prompt
                ):
                    if content is not None:
                        chunk_count += 1
                        data = json.dumps({"content": content}, ensure_ascii=False)
                        if chunk_count % 20 == 0:
                            logger.info(f"发送 chunk {chunk_count} 给用户 {current_user.username}")
                        yield f"data: {data}\n\n"
                        # 发送注释行以刷新缓冲区
                        yield f": flush\n\n"
            except Exception as stream_err:
                logger.error(f"流式生成过程中出错: {stream_err}")
                error_data = json.dumps({"error": str(stream_err)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"

            logger.info(f"AI流式输出完成，共 {chunk_count} 个chunks")
            yield "data: [DONE]\n\n"
            logger.info(f"AI流式问答完成，用户: {current_user.username}")

        except Exception as e:
            logger.error(f"AI流式问答失败: {e}")
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "X-Content-Type-Options": "nosniff",  # 防止MIME嗅探
            "Content-Type": "text/event-stream; charset=utf-8",
        },
    )

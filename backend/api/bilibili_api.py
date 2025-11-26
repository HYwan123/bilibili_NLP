import asyncio
import json
import uuid
from typing import Optional
from fastapi import Depends, status, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from api.user import get_current_user
from core import bilibili, comment_analysis, database, recommendation_model, sql_use, bge_base_use, bilibili_video_info
from core.exceptions import create_error_response, log_error
from schemas.api import CookieData
from schemas.user import User

# Configure logging
logger = logging.getLogger(__name__)


router = APIRouter()
global_redis = sql_use.SQL_redis()

@router.get("/select/{BV}")
async def select_BV(BV: str, current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Select BV request by user {current_user.username} for BV: {BV}")
        result = bilibili.select_by_BV(BV)
        global_redis.redis_value_add('leiji')
        if result:
            comment_texts = [comment.get('comment_text', '') for comment in result if comment.get('comment_text')]
            if comment_texts:
                summary = f"爬取到 {len(comment_texts)} 条评论，前3条: " + " | ".join(comment_texts[:3])
                if len(comment_texts) > 3:
                    summary += f" ... (还有 {len(comment_texts) - 3} 条)"
            else:
                summary = "未获取到评论内容"
        else:
            summary = "查询失败，未获取到数据"
        database.add_bv_history(BV, current_user.username, summary)

        if result:
            logger.info(f"Successfully retrieved comments for BV: {BV}")
            return JSONResponse(status_code=200, content={'code': 200, 'message': 'success', 'data': result})
        else:
            logger.warning(f"No data found for BV: {BV}")
            return create_error_response(
                404,
                'Not Found'
            )
    except Exception as e:
        logger.error(f"Error retrieving BV {BV}: {e}")
        log_error(e, "select_BV")
        return create_error_response(
            500,
            f'服务器内部错误: {str(e)}'
        )

@router.get("/history_data")
async def history_data():


    history_data = {
        "leiji": int(global_redis.redis_select_by_key('leiji')), # type: ignore
        "chuli": int(global_redis.redis_select_by_key('chuli')), # type: ignore
        "huaxiang": int(global_redis.redis_select_by_key('huaxiang')) # type: ignore
    }
    return JSONResponse(
        status_code=200,
        content={'code': 200, 'message': 'success', 'data': history_data}
    )

@router.get("/get_cookies")
async def get_cookies():


    cookies = {
        "cookie": str(global_redis.redis_select_by_key('cookie')), # type: ignore
        "video_select_cookie": str(global_redis.redis_select_by_key('video_select_cookie')), # type: ignore

    }
    return JSONResponse(
        status_code=200,
        content={'code': 200, 'message': 'success', 'data': cookies}
    )

@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user)):
    history_data = database.get_history_by_user(current_user.id)
    return JSONResponse(
        status_code=200,
        content={'code': 200, 'message': 'success', 'data': history_data}
    )

@router.get("/get_uids")
async def get_uids(current_user: User = Depends(get_current_user)):
    data = database.get_user_report()
    return {"code": 200, "data": data, "message": "成功"}


@router.post("/change_cookie_user")
async def change_user_cookie(data: CookieData):
    global_redis.redis_set_by_key('cookie', data.cookie)
    return {"code": 200, "message": "修改成功"}

@router.post("/user/comments/{uid}")
async def get_user_comments(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('leiji')

    """
    直接获取用户评论并保存到数据库
    """
    try:
        logger.info(f"用户 {current_user.username} 请求获取用户 {uid} 的评论")

        # 直接调用评论获取函数
        comments = bilibili.get_user_comments_simple(uid)

        if comments:
            logger.info(f"成功获取 {len(comments)} 条评论，准备保存到数据库")
            # 保存到数据库
            success = database.save_user_comments(uid, current_user.username, comments)
            database.add_report_history(uid)
            if success:
                logger.info(f"评论数据已成功保存到数据库")
                return JSONResponse(
                    status_code=200,
                    content={
                        'code': 200,
                        'message': 'success',
                        'data': {
                            'uid': uid,
                            'comment_count': len(comments),
                            'comments': comments
                        }
                    }
                )
            else:
                logger.error(f"保存到数据库失败 for user {uid}")
                return create_error_response(
                    500,
                    '保存到数据库失败'
                )
        else:
            logger.warning(f"未获取到用户 {uid} 的评论数据")
            return create_error_response(
                404,
                '未找到该用户的评论数据，可能是API访问限制或用户无评论'
            )

    except Exception as e:
        logger.error(f"获取用户评论失败: {e}")
        log_error(e, "get_user_comments")
        return create_error_response(
            500,
            f'获取评论失败: {str(e)}'
        )

@router.get("/user/comments/{uid}")
async def get_saved_user_comments(uid: int, current_user: User = Depends(get_current_user)):
    """
    从数据库获取已保存的用户评论数据
    """
    try:
        comments = database.get_user_comments(uid)
        
        if comments:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': comments}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据', 'data': None}
            )
            
    except Exception as e:
        print(f"获取保存的评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
        )

@router.get("/user/comments/redis/{uid}")
async def get_user_comments_redis(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('leiji')
    """
    从Redis获取已保存的用户评论数据
    """
    try:
        from core.bilibili import get_user_comments_from_redis
        comments = get_user_comments_from_redis(uid)
        if comments:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': comments}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据', 'data': None}
            )
    except Exception as e:
        print(f"获取Redis评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
        )

from typing import Optional

@router.post("/user/analyze/{uid}")
async def analyze_user_portrait(uid: int, api_key: Optional[str] = None, api_url: Optional[str] = None, model_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """
    分析用户评论，生成用户画像
    """
    global_redis.redis_value_add('huaxiang')

    try:
        logger.info(f"用户画像分析请求 by user {current_user.username} for uid: {uid}")
        from core.bilibili import analyze_user_comments
        result = await analyze_user_comments(uid, api_key, api_url, model_id)

        if "error" in result:
            logger.warning(f"用户画像分析错误 for uid {uid}: {result['error']}")
            return create_error_response(
                400,
                result["error"]
            )
        if "msg" in result:
            logger.info(f"用户画像分析完成 for uid {uid}")
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': result["msg"], 'data': global_redis.redis_select(f"analysis_{uid}")}
            )
        logger.info(f"用户画像分析成功 for uid {uid}")
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '分析完成', 'data': result}
        )

    except Exception as e:
        logger.error(f"用户画像分析失败: {e}")
        log_error(e, "analyze_user_portrait")
        return create_error_response(
            500,
            f'分析失败: {str(e)}'
        )
@router.get("/user/analysis/{uid}")
async def get_user_analysis(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('huaxiang')
    """
    获取用户画像分析结果
    """
    try:
        from core.bilibili import get_user_analysis_from_redis
        result = get_user_analysis_from_redis(uid)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': result}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到分析结果', 'data': None}
            )
            
    except Exception as e:
        print(f"获取分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取失败: {str(e)}', 'data': None}
        )

# --- Background Task for Comment Analysis ---
async def run_comment_analysis_task(bv_id: str, job_id: str):
    """
    The actual analysis function that runs in the background.
    """
    redis_handler = sql_use.SQL_redis()
    try:
        logger.info(f"Starting comment analysis task for BV: {bv_id}, job_id: {job_id}")
        # 1. Update status: Fetching comments
        status_update = {"status": "Processing", "progress": 20, "details": f"正在获取视频 {bv_id} 的评论..."}
        redis_handler.set_job_status(job_id, status_update)

        comments = bilibili.select_by_BV(bv_id)
        if not comments:
            raise ValueError(f"未找到视频 {bv_id} 的评论数据，请检查BV号是否正确或稍后再试。")

        # 2. Update status: Analyzing comments
        status_update = {"status": "Processing", "progress": 60, "details": f"已获取 {len(comments)} 条评论，正在进行AI分析..."}
        redis_handler.set_job_status(job_id, status_update)

        analysis_result = await comment_analysis.analyze_bv_comments(bv_id, comments)

        if "error" in analysis_result:
             raise Exception(analysis_result["error"])

        # 3. Update status: Completed
        status_update = {
            "status": "Completed",
            "progress": 100,
            "details": f"视频 {bv_id} 评论分析完成",
            "result": analysis_result
        }
        redis_handler.set_job_status(job_id, status_update)
        logger.info(f"Comment analysis completed successfully for BV: {bv_id}")

    except Exception as e:
        error_message = f"评论分析任务失败: {e}"
        logger.error(error_message)
        log_error(e, "run_comment_analysis_task")
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
    finally:
        # Task finished, always release the lock
        lock_key = f"lock:analyze_bv:{bv_id}"
        redis_handler.release_lock(lock_key)
        logger.info(f"Released lock for BV: {bv_id}")

# --- 评论分析相关API ---
@router.post("/comments/analyze/submit/{bv_id}")
async def submit_comment_analysis_job(bv_id: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Submits a comment analysis job. Checks for cached results first.
    If no cache, runs the job in the background and prevents duplicates with a lock.
    """
    # 1. Check for a cached result first
    global_redis.redis_value_add('chuli')
    cached_result = comment_analysis.get_bv_analysis(bv_id)
    if cached_result:
        print(f"Cache hit for analysis of BV: {bv_id}. Returning cached result.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'code': 200, 'message': '已从缓存获取分析结果', 'data': cached_result}
        )
        
    # 2. If no cache, proceed with locking and job submission
    redis_handler = sql_use.SQL_redis()
    lock_key = f"lock:analyze_bv:{bv_id}"
    job_id = f"analyze_bv_{bv_id}_{uuid.uuid4().hex[:8]}"
    
    if not redis_handler.acquire_lock(lock_key, job_id, timeout=300):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={'code': 409, 'message': '该视频的分析任务已在进行中，请稍后再试。', 'data': None}
        )

    background_tasks.add_task(run_comment_analysis_task, bv_id, job_id)
    
    return JSONResponse(
        status_code=202, # HTTP 202 Accepted
        content={'code': 202, 'message': '分析任务已提交，将在后台进行处理。', 'data': {'job_id': job_id}}
    )

@router.get("/comments/analysis/{bv_id}")
async def get_comment_analysis(bv_id: str, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('chuli')
    """
    获取指定BV视频的评论分析结果
    """
    try:
        from core.comment_analysis import get_bv_analysis
        result = get_bv_analysis(bv_id)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': result}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到评论分析结果', 'data': None}
            )
            
    except Exception as e:
        print(f"获取评论分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取失败: {str(e)}', 'data': None}
        )

# --- 内容推荐相关API ---
@router.post("/recommendations/generate/{uid}")
async def generate_user_recommendations(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('chuli')
    """
    为指定用户生成内容推荐
    """
    try:
        # 获取用户评论数据
        comments = database.get_user_comments(uid)
        
        if not comments:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据，请先获取用户评论', 'data': None}
            )
        
        # 生成推荐
        result = recommendation_model.recommend_for_user(uid, comments)
        
        # 记录推荐历史
        database.add_uuid_history(uid, current_user.username, f"rec_{uid}", f"为用户 {uid} 生成了 {result['total_recommendations']} 个推荐")
        
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '推荐生成成功', 'data': result}
        )
        
    except Exception as e:
        print(f"生成推荐失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'生成推荐失败: {str(e)}', 'data': None}
        )

@router.get("/recommendations/{uid}")
async def get_user_recommendations(uid: int, current_user: User = Depends(get_current_user)):
    """
    获取用户的推荐结果
    """
    try:
        model = recommendation_model.ContentRecommendationModel()
        recommendations = model.get_recommendations_from_redis(uid)
        
        if recommendations:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': recommendations}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到推荐结果，请先生成推荐', 'data': None}
            )
            
    except Exception as e:
        print(f"获取推荐失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取推荐失败: {str(e)}', 'data': None}
        )

@router.get("/recommendations/preferences/{uid}")
async def get_user_preferences(uid: int, current_user: User = Depends(get_current_user)):
    """
    获取用户偏好分析结果
    """
    try:
        # 获取用户评论数据
        comments = database.get_user_comments(uid)
        
        if not comments:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据', 'data': None}
            )
        
        # 分析用户偏好
        model = recommendation_model.ContentRecommendationModel()
        preferences = model.analyze_user_preferences(comments)
        
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': 'success', 'data': preferences}
        )
        
    except Exception as e:
        print(f"获取用户偏好失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取用户偏好失败: {str(e)}', 'data': None}
        )

@router.get("/recommendations/sample-videos")
async def get_sample_videos(current_user: User = Depends(get_current_user)):
    """
    获取示例视频数据
    """
    try:
        sample_videos = recommendation_model.get_sample_video_data()
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': 'success', 'data': sample_videos}
        )
    except Exception as e:
        print(f"获取示例视频失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取示例视频失败: {str(e)}', 'data': None}
        )
# --- 内容推荐相关API(V2) ---
@router.post("/start_tuijian/{uid}")
async def video_by_user(uid: str, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('chuli')
 
    result = bge_base_use.get_tuijian_bvs(uid)
    print(result)
    if result is not None:
        
        global_redis.redis_set_by_key(f'{uid}_videos', result)
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '推荐生成成功', 'data': result}
        )
          
    else:
        return JSONResponse(
            status_code=404,
            content={'code': 404, 'message': '推荐生成失败'}
        )

@router.get("/get_tuijian_video_info/{uid}")
async def get_video_by_user(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('chuli')

    try:
        # 从Redis获取存储的BV列表
        bv_data = global_redis.redis_select_by_key(f'{uid}_videos')
        if not bv_data:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的推荐视频数据，请先生成推荐'}
            )
        
        # 解析JSON数据
        bvs = json.loads(bv_data)
        bv_dict = {}
        
        # 获取每个BV号的视频信息
        for bv in bvs:
            video_info = bilibili_video_info.get_video_info(bv)
            if video_info:
                bv_dict[bv] = video_info
        
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '获取成功', 'data': bv_dict}
        )
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': '数据格式错误，无法解析推荐视频数据'}
        )
    except Exception as e:
        print(f"获取视频详情失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取视频详情失败: {str(e)}'}
        )

@router.post("/insert_vector/{bv_id}")
async def insert_vector_by_bv(bv_id: str, current_user: User = Depends(get_current_user)):
    """
    将指定BV号的视频标签向量插入到向量数据库
    """
    try:
        bge_base_use.insert_vector_by_BV(bv_id)
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '向量插入成功', 'data': {'bv_id': bv_id}}
        )
    except Exception as e:
        print(f"插入向量失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'插入向量失败: {str(e)}'}
        )

@router.get("/video/info/{bv_id}")
async def get_video_info(bv_id: str, current_user: User = Depends(get_current_user)):
    """
    获取单个视频的详细信息
    """
    try:
        video_info = bilibili_video_info.get_video_info(bv_id)
        print(video_info)
        if video_info.get('msg') == 'OK':
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': video_info}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '获取视频信息失败', 'data': None}
            )
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取视频信息失败: {str(e)}', 'data': None}
        )

# --- Bilibili QR Code Login Endpoints ---
@router.post("/bilibili/qrcode/generate")
async def generate_bilibili_qrcode_endpoint(current_user: User = Depends(get_current_user)):
    """
    生成Bilibili登录二维码
    """
    try:
        logger.info(f"用户 {current_user.username} 请求生成Bilibili登录二维码")
        qrcode_data = bilibili.generate_bilibili_qrcode()

        # Store qrcode_key in Redis with user ID for later polling
        global_redis.redis_set_by_key(f"qrcode_key_{current_user.id}", qrcode_data['qrcode_key'])

        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '二维码生成成功',
                'data': {
                    'qrcode_key': qrcode_data['qrcode_key'],
                    'url': qrcode_data['url']
                }
            }
        )
    except Exception as e:
        logger.error(f"生成Bilibili二维码失败: {e}")
        log_error(e, "generate_bilibili_qrcode_endpoint")
        return create_error_response(
            500,
            f'生成二维码失败: {str(e)}'
        )

@router.post("/bilibili/qrcode/poll")
async def poll_bilibili_login_endpoint(current_user: User = Depends(get_current_user)):
    """
    轮询Bilibili登录状态
    """
    try:
        logger.info(f"用户 {current_user.username} 请求轮询Bilibili登录状态")

        # Get qrcode_key from Redis using user ID
        qrcode_key = global_redis.redis_select_by_key(f"qrcode_key_{current_user.id}").decode("utf-8")
        logger.info(qrcode_key)
        if not qrcode_key:
            return JSONResponse(
                status_code=400,
                content={
                    'code': 400,
                    'message': '未找到二维码密钥，请先生成二维码',
                    'data': None
                }
            )

        # Poll login status
        login_result = bilibili.poll_bilibili_login(qrcode_key)

        # Check if login was successful (code 0 in data)
        if login_result['data'].get('code') == 0 and login_result['data'].get('url'):
            # Extract SESSDATA and bili_jct from the login URL
            url = login_result['data']['url']
            session_data = bilibili.extract_sessdata_from_url(url)

            if session_data:
                # Update the cookie in Redis with the new SESSDATA and bili_jct
                # Get existing cookie and update it
                existing_cookie = global_redis.redis_select_by_key('cookie') or ""
                if isinstance(existing_cookie, bytes):
                    existing_cookie = existing_cookie.decode('utf-8')

                # Create new cookie string with updated SESSDATA and bili_jct
                if existing_cookie:
                    # Parse existing cookie and update SESSDATA and bili_jct
                    cookie_pairs = existing_cookie.split('; ')
                    updated_pairs = []
                    sessdata_updated = False
                    bili_jct_updated = False

                    for pair in cookie_pairs:
                        if pair.startswith('SESSDATA='):
                            updated_pairs.append(f"SESSDATA={session_data['sessdata']}")
                            sessdata_updated = True
                        elif pair.startswith('bili_jct='):
                            updated_pairs.append(f"bili_jct={session_data['bili_jct']}")
                            bili_jct_updated = True
                        else:
                            updated_pairs.append(pair)

                    # Add SESSDATA and bili_jct if they weren't in the existing cookie
                    if not sessdata_updated:
                        updated_pairs.append(f"SESSDATA={session_data['sessdata']}")
                    if not bili_jct_updated:
                        updated_pairs.append(f"bili_jct={session_data['bili_jct']}")

                    new_cookie = '; '.join(updated_pairs)
                else:
                    # Create new cookie with just SESSDATA and bili_jct
                    new_cookie = f"SESSDATA={session_data['sessdata']}; bili_jct={session_data['bili_jct']}"

                # Save the updated cookie to Redis
                global_redis.redis_set_by_key('cookie', new_cookie)

                logger.info(f"用户 {current_user.username} Bilibili登录成功，已更新cookie")

                # Return success response with session data
                login_result['data']['session_data'] = session_data
                login_result['data']['cookie_updated'] = True

        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '轮询成功',
                'data': login_result['data']
            }
        )
    except Exception as e:
        logger.error(f"轮询Bilibili登录状态失败: {e}")
        log_error(e, "poll_bilibili_login_endpoint")
        return create_error_response(
            500,
            f'轮询登录状态失败: {str(e)}'
        )

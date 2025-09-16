import asyncio
import uuid
from fastapi import Depends, status, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from api.user import get_current_user
from core import bilibili, comment_analysis, database, recommendation_model, sql_use, bge_base_use, bilibili_video_info
from schemas.api import CookieData
from schemas.user import User


router = APIRouter()
global_redis = sql_use.SQL_redis()

@router.get("/select/{BV}")
async def select_BV(BV: str, current_user: User = Depends(get_current_user)):
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
        return JSONResponse(status_code=200, content={'code': 200, 'message': 'success', 'data': result})
    else:
        return JSONResponse(status_code=404, content={'code': 404, 'message': 'Not Found', 'data': None})

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
        print(f"用户 {current_user.username} 请求获取用户 {uid} 的评论")
        
        # 直接调用评论获取函数
        comments = bilibili.get_user_comments_simple(uid)
        
        if comments:
            print(f"成功获取 {len(comments)} 条评论，准备保存到数据库")
            # 保存到数据库
            success = database.save_user_comments(uid, current_user.username, comments)
            database.add_report_history(uid)
            if success:
                print(f"评论数据已成功保存到数据库")
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
                print(f"保存到数据库失败")
                return JSONResponse(
                    status_code=500,
                    content={'code': 500, 'message': '保存到数据库失败', 'data': None}
                )
        else:
            print(f"未获取到用户 {uid} 的评论数据")
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据，可能是API访问限制或用户无评论', 'data': None}
            )
            
    except Exception as e:
        print(f"获取用户评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
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

@router.post("/user/analyze/{uid}")
async def analyze_user_portrait(uid: int, current_user: User = Depends(get_current_user)):
    """
    分析用户评论，生成用户画像
    """
    global_redis.redis_value_add('huaxiang')
    
    try:
        from core.bilibili import analyze_user_comments
        result = await analyze_user_comments(uid)
        
        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={'code': 400, 'message': result["error"], 'data': None}
            )
        if "msg" in result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': result["msg"], 'data': global_redis.redis_select(f"analysis_{uid}")}
            )
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '分析完成', 'data': result}
        )
        
    except Exception as e:
        print(f"用户画像分析失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'分析失败: {str(e)}', 'data': None}
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

    except Exception as e:
        error_message = f"评论分析任务失败: {e}"
        print(error_message)
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
    finally:
        # Task finished, always release the lock
        lock_key = f"lock:analyze_bv:{bv_id}"
        redis_handler.release_lock(lock_key)
        print(f"Released lock for BV: {bv_id}")

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

@router.get("/get_tuijian_video_info/{BVid}")
async def get_video_by_user(uid: int, current_user: User = Depends(get_current_user)):
    global_redis.redis_value_add('chuli')

    bv_dict = {}
    bvs = global_redis.redis_select_by_key(f'{uid}_videos')
    for bv in bvs:
        bv_dict[bv] = bilibili_video_info.get_video_info(bv)
    return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '获取成功', 'data': bv_dict}
        )


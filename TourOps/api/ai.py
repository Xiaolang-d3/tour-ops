from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import json
import httpx
from sqlalchemy.orm import Session
from TourOps.core.config import settings
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user
from TourOps.models.user import User
from TourOps.models.chat_history import ChatHistory

router = APIRouter()


class TripDemand(BaseModel):
    """行程需求"""
    trip_type: str
    start_date: date
    end_date: date
    participants: int
    budget_min: int
    budget_max: int
    interests: List[str] = []
    special_needs: Optional[str] = None
    destination: Optional[str] = None


class ActivitySuggestion(BaseModel):
    """活动建议"""
    day: int
    time: str
    type: str
    name: str
    duration: str
    location: Optional[str] = None
    estimated_cost: Optional[int] = None
    notes: Optional[str] = None


class TripSuggestion(BaseModel):
    """行程建议"""
    title: str
    summary: str
    total_days: int
    estimated_budget: int
    activities: List[ActivitySuggestion]
    tips: List[str] = []


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    """AI对话请求"""
    message: str
    history: List[ChatMessage] = []
    context: Optional[str] = None


# ======================== 千问AI核心调用 ========================


async def call_qwen_api(messages: list, stream: bool = False, timeout: float = 180.0) -> dict | httpx.Response:
    """
    调用通义千问API（DashScope OpenAI兼容接口）
    文档: https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen
    支持自动重试（非流式模式下最多重试2次）
    """
    api_key = settings.AI_API_KEY
    base_url = settings.AI_BASE_URL
    model = settings.AI_MODEL

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI 服务未配置。请在 config.yaml 中设置 ai.api_key（从 https://bailian.console.aliyun.com/#/api-key 获取）"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    # 分别设置连接/读取/写入超时
    timeouts = httpx.Timeout(timeout, connect=30.0)

    if stream:
        payload["stream"] = True
        client = httpx.AsyncClient(timeout=timeouts)
        response = await client.send(
            client.build_request(
                "POST",
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            ),
            stream=True,
        )
        if response.status_code != 200:
            body = await response.aread()
            await client.aclose()
            raise HTTPException(status_code=502, detail=f"AI API 调用失败: {body.decode()}")
        return response, client

    # 非流式：支持重试（指数退避，最多4次重试）
    max_retries = 4
    last_error = None
    import asyncio
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeouts) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if response.status_code != 200:
                    # 5xx 服务端错误也走重试
                    if response.status_code >= 500 and attempt < max_retries:
                        print(f"[AI call_qwen_api] 第{attempt + 1}次请求收到 HTTP {response.status_code}，正在重试...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise HTTPException(
                        status_code=502,
                        detail=f"AI API 调用失败 (HTTP {response.status_code}): {response.text}"
                    )

                return response.json()
        except HTTPException:
            raise
        except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ReadError, httpx.WriteError, ConnectionError, OSError) as e:
            last_error = e
            if attempt < max_retries:
                delay = 2 ** attempt  # 1s, 2s, 4s, 8s
                print(f"[AI call_qwen_api] 第{attempt + 1}次请求失败({type(e).__name__}: {e})，{delay}秒后重试...")
                await asyncio.sleep(delay)
            else:
                print(f"[AI call_qwen_api] 重试{max_retries}次后仍失败: {type(e).__name__}: {e}")
                raise

    raise last_error




def extract_json_from_content(content: str) -> dict | None:
    """从AI响应内容中提取JSON，增强容错"""
    import re

    if not content or not content.strip():
        return None

    text = content.strip()

    # 去除可能的 BOM 和不可见字符
    text = text.lstrip('\ufeff\u200b')

    # 先尝试直接解析
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # 尝试提取 ```json ... ``` 代码块
    json_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if json_block:
        try:
            return json.loads(json_block.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 尝试提取最外层 { ... } 块（处理嵌套大括号）
    start = text.find("{")
    if start >= 0:
        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > start:
            json_str = text[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # 尝试修复常见问题：尾部多余逗号
                fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

    return None



# ======================== 数据清洗工具 ========================

import re as _re

def _normalize_time(t: str) -> str:
    """将各种时间格式统一为 HH:MM"""
    if not t:
        return "09:00"
    t = t.strip()
    # 已经是 HH:MM
    m = _re.match(r'^(\d{1,2}):(\d{2})', t)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    # 纯数字当小时
    m = _re.match(r'^(\d{1,2})$', t)
    if m:
        return f"{int(m.group(1)):02d}:00"
    # 中文格式如 "上午9:00" "下午2:30"
    m = _re.search(r'(\d{1,2}):?(\d{2})?', t)
    if m:
        h = int(m.group(1))
        mi = m.group(2) or "00"
        if '下午' in t or '晚' in t:
            if h < 12:
                h += 12
        return f"{h:02d}:{mi}"
    return "09:00"

def _normalize_type(t: str) -> str:
    """将活动类型统一为 transport/attraction/meal/hotel/free"""
    if not t:
        return "free"
    t = t.strip().lower()
    valid = {"transport", "attraction", "meal", "hotel", "free"}
    if t in valid:
        return t
    # 中文/别名映射
    mapping = {
        "交通": "transport", "出行": "transport", "飞机": "transport", "火车": "transport",
        "景点": "attraction", "游览": "attraction", "参观": "attraction", "观光": "attraction", "sightseeing": "attraction",
        "餐饮": "meal", "用餐": "meal", "早餐": "meal", "午餐": "meal", "晚餐": "meal", "dining": "meal", "food": "meal", "breakfast": "meal", "lunch": "meal", "dinner": "meal",
        "住宿": "hotel", "酒店": "hotel", "入住": "hotel", "accommodation": "hotel", "lodging": "hotel",
        "自由": "free", "休息": "free", "休闲": "free", "leisure": "free", "rest": "free", "shopping": "free", "购物": "free",
    }
    for k, v in mapping.items():
        if k in t:
            return v
    return "free"

def _safe_int(v) -> int:
    """安全转换为整数"""
    if v is None:
        return 0
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0


# ======================== API 接口 ========================

@router.post("/generate", response_model=TripSuggestion)
async def generate_trip(demand: TripDemand, current_user: User = Depends(get_current_user)):
    """根据需求AI生成行程建议"""
    prompt = build_trip_prompt(demand)
    messages = [
        {"role": "system", "content": TRIP_PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        result = await call_qwen_api(messages, timeout=180.0)
        content = result["choices"][0]["message"]["content"]
        data = extract_json_from_content(content)

        if data:
            cleaned = _clean_trip_data(data, demand)
            return TripSuggestion(**cleaned)
        else:
            print(f"[AI generate_trip] AI返回内容无法解析为JSON: {content[:300]}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI generate_trip] 调用失败: {type(e).__name__}: {e}")

    return generate_fallback(demand)


def _clean_trip_data(data: dict, demand: TripDemand) -> dict:
    """清洗AI返回的行程数据"""
    days = (demand.end_date - demand.start_date).days + 1
    data.setdefault("title", f"{days}天行程方案")
    data.setdefault("summary", "AI生成的行程建议")
    data.setdefault("total_days", days)
    data.setdefault("estimated_budget", (demand.budget_min + demand.budget_max) // 2)
    data.setdefault("tips", [])

    raw_acts = data.get("activities") or data.get("itinerary") or data.get("schedule") or []
    cleaned = []
    for act in raw_acts:
        if not isinstance(act, dict):
            continue
        cleaned.append({
            "day": act.get("day", 1),
            "time": _normalize_time(act.get("time") or act.get("start_time") or "09:00"),
            "type": _normalize_type(act.get("type") or act.get("activity_type") or act.get("category") or "free"),
            "name": act.get("name") or act.get("activity_name") or act.get("title") or "未命名活动",
            "duration": str(act.get("duration") or "1小时"),
            "location": act.get("location") or act.get("place") or act.get("venue") or None,
            "estimated_cost": _safe_int(act.get("estimated_cost") or act.get("cost") or act.get("price") or 0),
            "notes": act.get("notes") or act.get("description") or act.get("remark") or None,
        })
    data["activities"] = cleaned
    return data


@router.post("/generate/stream")
async def generate_trip_stream(demand: TripDemand, current_user: User = Depends(get_current_user)):
    """流式生成行程 — 用 SSE 逐步返回内容，避免长时间等待被断连"""
    prompt = build_trip_prompt(demand)
    messages = [
        {"role": "system", "content": TRIP_PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        response, client = await call_qwen_api(messages, stream=True, timeout=180.0)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI generate_trip_stream] 流式连接失败: {type(e).__name__}: {e}")
        # 返回 fallback
        fallback = generate_fallback(demand)
        async def fallback_gen():
            yield f"data: {json.dumps({'type': 'result', 'data': fallback.model_dump()}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(fallback_gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    async def event_generator():
        full_content = []
        try:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content.append(content)
                            # 把每个 chunk 转发给前端，让前端知道还在工作
                            yield f"data: {json.dumps({'type': 'chunk', 'content': content}, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        continue

            # 流结束，解析完整内容
            text = "".join(full_content)
            parsed = extract_json_from_content(text)
            if parsed:
                cleaned = _clean_trip_data(parsed, demand)
                yield f"data: {json.dumps({'type': 'result', 'data': cleaned}, ensure_ascii=False)}\n\n"
            else:
                print(f"[AI generate_trip_stream] 流式内容无法解析JSON: {text[:300]}")
                fallback = generate_fallback(demand)
                yield f"data: {json.dumps({'type': 'result', 'data': fallback.model_dump()}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[AI generate_trip_stream] 流式读取异常: {type(e).__name__}: {e}")
            fallback = generate_fallback(demand)
            yield f"data: {json.dumps({'type': 'result', 'data': fallback.model_dump()}, ensure_ascii=False)}\n\n"
        finally:
            await response.aclose()
            await client.aclose()
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat")
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI智能对话（旅行助手）- 自动保存对话记录到数据库"""
    messages = [
        {"role": "system", "content": TRAVEL_ASSISTANT_SYSTEM_PROMPT}
    ]

    # 如果有上下文信息（如当前行程信息），添加到系统提示中
    if request.context:
        messages[0]["content"] += f"\n\n当前行程上下文信息：\n{request.context}"

    # 如果前端没有传历史，从数据库加载最近10条
    if request.history:
        for msg in request.history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
    else:
        db_history = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user.id)
            .order_by(ChatHistory.created_at.desc())
            .limit(10)
            .all()
        )
        for h in reversed(db_history):
            messages.append({"role": h.role, "content": h.content})

    # 添加当前消息
    messages.append({"role": "user", "content": request.message})

    # 保存用户消息到数据库
    user_msg = ChatHistory(user_id=current_user.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    try:
        result = await call_qwen_api(messages)
        content = result["choices"][0]["message"]["content"]

        # 保存 AI 回复到数据库
        ai_msg = ChatHistory(user_id=current_user.id, role="assistant", content=content)
        db.add(ai_msg)
        db.commit()

        return {"reply": content}
    except HTTPException:
        raise
    except Exception as e:
        error_reply = f"抱歉，AI暂时无法响应，请稍后再试。错误信息：{str(e)}"
        # 保存错误回复
        ai_msg = ChatHistory(user_id=current_user.id, role="assistant", content=error_reply)
        db.add(ai_msg)
        db.commit()
        return {"reply": error_reply}


@router.get("/chat/history")
def get_chat_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的对话历史"""
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    # 按时间正序返回
    records.reverse()
    return [
        {
            "id": r.id,
            "role": r.role,
            "content": r.content,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.delete("/chat/history")
def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空当前用户的对话历史"""
    count = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "对话记录已清空", "deleted": count}


@router.post("/chat/stream")
async def ai_chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI智能对话 - 流式响应（SSE），自动保存对话记录"""
    messages = [
        {"role": "system", "content": TRAVEL_ASSISTANT_SYSTEM_PROMPT}
    ]

    if request.context:
        messages[0]["content"] += f"\n\n当前行程上下文信息：\n{request.context}"

    for msg in request.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    # 保存用户消息
    user_msg = ChatHistory(user_id=current_user.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    try:
        response, client = await call_qwen_api(messages, stream=True)
    except HTTPException:
        raise

    user_id = current_user.id

    async def event_generator():
        full_content = []
        try:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content.append(content)
                            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        continue
        finally:
            await response.aclose()
            await client.aclose()
            # 保存 AI 回复到数据库
            if full_content:
                from TourOps.core.database import SessionLocal
                save_db = SessionLocal()
                try:
                    ai_msg = ChatHistory(user_id=user_id, role="assistant", content="".join(full_content))
                    save_db.add(ai_msg)
                    save_db.commit()
                except Exception:
                    save_db.rollback()
                finally:
                    save_db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

class SaveTripFromAI(BaseModel):
    """将AI生成的行程保存为真实行程"""
    title: str
    start_date: date
    end_date: date
    participants: int = 1
    budget: int | None = None
    activities: List[ActivitySuggestion]


@router.post("/save-trip")
async def save_trip_from_ai(
    data: SaveTripFromAI,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将AI生成的行程建议保存为真实行程（含活动）"""
    from TourOps.models.trip import Trip, TripStatus
    from TourOps.models.activity import Activity, ActivityType
    from datetime import datetime, timedelta
    import secrets

    # 创建行程
    trip = Trip(
        name=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        guest_count=data.participants,
        budget=data.budget,
        status=TripStatus.DRAFT,
        share_code=secrets.token_hex(16),
        created_by=current_user.id,
    )
    db.add(trip)
    db.flush()

    # 类型映射
    type_map = {
        "transport": ActivityType.TRANSPORT,
        "attraction": ActivityType.ATTRACTION,
        "meal": ActivityType.MEAL,
        "hotel": ActivityType.HOTEL,
        "free": ActivityType.FREE,
    }

    # 解析时长字符串为分钟
    def parse_duration_minutes(dur: str) -> int:
        import re
        total = 0
        h = re.search(r'(\d+)\s*[小时hH]', dur)
        m = re.search(r'(\d+)\s*[分钟mM]', dur)
        if h:
            total += int(h.group(1)) * 60
        if m:
            total += int(m.group(1))
        if total == 0:
            # 尝试纯数字（当作小时）
            nums = re.findall(r'[\d.]+', dur)
            if nums:
                total = int(float(nums[0]) * 60)
        return total or 60  # 默认1小时

    for idx, act in enumerate(data.activities):
        # 计算活动日期
        act_date = data.start_date + timedelta(days=act.day - 1)
        # 解析时间 HH:MM
        try:
            parts = act.time.split(":")
            hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            hour, minute = 9, 0

        start_dt = datetime(act_date.year, act_date.month, act_date.day, hour, minute)
        duration_min = parse_duration_minutes(act.duration)
        end_dt = start_dt + timedelta(minutes=duration_min)

        activity = Activity(
            trip_id=trip.id,
            type=type_map.get(act.type, ActivityType.FREE),
            name=act.name,
            start_time=start_dt,
            end_time=end_dt,
            location=act.location,
            cost=act.estimated_cost,
            notes=act.notes,
            sort_order=idx,
        )
        db.add(activity)

    db.commit()
    db.refresh(trip)
    return {"message": "行程已保存", "trip_id": trip.id}


# ======================== AI 活动推荐（已有行程） ========================


class RecommendRequest(BaseModel):
    """为已有行程推荐活动"""
    trip_id: int
    day: int | None = None  # 指定某天，None 则推荐所有天


class ChatToTripRequest(BaseModel):
    """从对话历史生成行程"""
    history: List[ChatMessage]


@router.post("/chat/generate-trip")
async def chat_generate_trip(
    request: ChatToTripRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据聊天对话历史，AI 提取需求并生成结构化行程"""
    if not request.history:
        raise HTTPException(status_code=400, detail="对话历史为空")

    messages = [
        {"role": "system", "content": CHAT_TO_TRIP_SYSTEM_PROMPT},
    ]

    # 把对话历史作为上下文
    for msg in request.history[-20:]:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({
        "role": "user",
        "content": "请根据以上对话内容，提取旅行需求并生成完整的行程安排。直接返回JSON，不要包含```json```标记。"
    })

    try:
        result = await call_qwen_api(messages, timeout=120.0)
        content = result["choices"][0]["message"]["content"]
        data = extract_json_from_content(content)

        if not data:
            return {"success": False, "message": "AI 未能生成有效行程，请继续补充需求后重试"}

        # 清洗数据
        data.setdefault("title", "AI 生成行程")
        data.setdefault("summary", "根据对话需求生成的行程方案")
        data.setdefault("total_days", len(set(a.get("day", 1) for a in (data.get("activities") or []))) or 3)
        data.setdefault("estimated_budget", 3000)
        data.setdefault("tips", [])

        raw_acts = data.get("activities") or data.get("itinerary") or data.get("schedule") or []
        cleaned = []
        for act in raw_acts:
            if not isinstance(act, dict):
                continue
            cleaned.append({
                "day": _safe_int(act.get("day", 1)),
                "time": _normalize_time(act.get("time") or act.get("start_time") or "09:00"),
                "type": _normalize_type(act.get("type") or act.get("activity_type") or "free"),
                "name": act.get("name") or act.get("title") or "未命名活动",
                "duration": str(act.get("duration") or "1小时"),
                "location": act.get("location") or None,
                "estimated_cost": _safe_int(act.get("estimated_cost") or act.get("cost") or 0),
                "notes": act.get("notes") or None,
            })
        data["activities"] = cleaned

        return {"success": True, "trip": data}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI chat_generate_trip] 失败: {type(e).__name__}: {e}")
        return {"success": False, "message": "AI 服务暂时不可用，请稍后重试"}


@router.post("/recommend-activities")
async def recommend_activities(
    req: RecommendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据已有行程信息，AI推荐活动"""
    from TourOps.models.trip import Trip
    from TourOps.models.activity import Activity

    trip = db.query(Trip).filter(Trip.id == req.trip_id, Trip.created_by == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    existing = db.query(Activity).filter(Activity.trip_id == trip.id).order_by(Activity.start_time).all()
    total_days = (trip.end_date - trip.start_date).days + 1

    # 构建已有活动描述
    existing_desc = ""
    if existing:
        existing_desc = "\n已有活动：\n"
        for act in existing:
            day_num = (act.start_time.date() - trip.start_date).days + 1
            existing_desc += f"  第{day_num}天 {act.start_time.strftime('%H:%M')} {act.name}（{act.type}）\n"

    day_hint = f"请只推荐第{req.day}天的活动。" if req.day else "请为每天推荐活动。"

    prompt = f"""请根据以下行程信息推荐合适的活动安排：

行程名称：{trip.name}
出行日期：{trip.start_date} 至 {trip.end_date}（共{total_days}天）
出行人数：{trip.guest_count}人
预算：{trip.budget or '未设定'}
{existing_desc}
{day_hint}
请补充推荐缺少的活动（如景点、餐饮、交通、住宿等），避免与已有活动时间冲突。
请直接返回JSON数组，不要包含```json```标记。

JSON格式：
[
  {{"day": 1, "time": "09:00", "type": "attraction", "name": "活动名称", "duration": "2小时", "location": "地点", "estimated_cost": 100, "notes": "备注"}}
]

type只能是：transport/attraction/meal/hotel/free 五选一。"""

    messages = [
        {"role": "system", "content": "你是一个专业的旅行规划师。请根据已有行程信息推荐合适的活动，以纯JSON数组格式返回。"},
        {"role": "user", "content": prompt},
    ]

    try:
        result = await call_qwen_api(messages, stream=False, timeout=60.0)
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        data = extract_json_from_content(content)

        if data is None:
            return {"activities": [], "message": "AI未返回有效数据，请重试"}

        # data 可能是 list 或 dict 包含 activities
        acts = data if isinstance(data, list) else data.get("activities", [])

        # 标准化
        suggestions = []
        for a in acts:
            if not isinstance(a, dict):
                continue
            suggestions.append({
                "day": _safe_int(a.get("day", 1)),
                "time": _normalize_time(a.get("time", "09:00")),
                "type": _normalize_type(a.get("type", "free")),
                "name": a.get("name", "活动"),
                "duration": a.get("duration", "1小时"),
                "location": a.get("location"),
                "estimated_cost": _safe_int(a.get("estimated_cost", 0)),
                "notes": a.get("notes"),
            })

        return {"activities": suggestions}

    except HTTPException:
        raise
    except Exception:
        return {"activities": [], "message": "AI服务暂时不可用，请稍后重试"}




# ======================== 提示词模板 ========================

TRIP_PLANNER_SYSTEM_PROMPT = """你是一个专业的旅行规划师AI助手。你需要根据用户需求生成详细、合理的行程安排。

要求：
1. 活动安排要合理，考虑时间、距离、体力等因素
2. 餐饮安排要包含早中晚餐
3. 需要包含交通安排
4. 费用估算要合理
5. 以纯JSON格式返回结果，不要包含任何markdown标记

JSON格式要求：
{
    "title": "行程标题",
    "summary": "行程概述（100字以内）",
    "estimated_budget": 人均预算（整数），
    "activities": [
        {
            "day": 天数（从1开始），
            "time": "HH:MM格式时间",
            "type": "类型（transport/attraction/meal/hotel/free五选一）",
            "name": "活动名称",
            "duration": "时长描述",
            "location": "地点",
            "estimated_cost": 费用（整数，可为0）,
            "notes": "备注说明"
        }
    ],
    "tips": ["注意事项1", "注意事项2"]
}"""

TRAVEL_ASSISTANT_SYSTEM_PROMPT = """你是TourOps旅行编排系统的AI助手，你的核心职责是通过对话帮助用户梳理旅行需求，最终生成满意的行程方案。

你的工作流程：
1. 主动了解用户需求：目的地、出行日期/天数、人数、预算、出行类型（亲子/商务/休闲等）、兴趣偏好、特殊需求
2. 针对用户提到的信息给出专业建议和推荐（景点、美食、住宿、注意事项等）
3. 当关键信息（至少目的地和大致天数）基本明确后，主动总结已收集的需求，并询问用户："需求已经比较清楚了，是否要为您生成详细的行程方案？还是还有其他想法需要补充？"
4. 如果用户说可以生成/确认了，告诉用户点击输入框旁边的「✨ 生成行程」按钮即可一键生成

对话风格：
- 友好、专业、简洁，不要长篇大论
- 每次回复聚焦一两个问题，不要一次问太多
- 适时给出推荐和建议，展现专业性
- 如果用户的问题与旅行无关，礼貌地引导回旅行话题

注意：不要在回复中直接输出结构化的行程表格或JSON数据。你的职责是对话和建议，正式的行程方案由系统的生成功能来完成。"""


CHAT_TO_TRIP_SYSTEM_PROMPT = """你是一个专业的旅行规划师。请根据用户的对话历史，提取旅行需求并生成详细的行程安排。

请仔细分析对话中提到的：目的地、出行日期/天数、人数、预算、兴趣偏好、特殊需求等信息。
如果某些信息对话中未明确提及，请根据上下文合理推断。

以纯JSON格式返回结果，不要包含任何markdown标记或```json```代码块。

JSON格式要求：
{
    "title": "行程标题",
    "summary": "行程概述（100字以内）",
    "total_days": 天数整数,
    "estimated_budget": 人均预算整数,
    "activities": [
        {
            "day": 天数（从1开始），
            "time": "HH:MM格式时间",
            "type": "类型（transport/attraction/meal/hotel/free五选一）",
            "name": "活动名称",
            "duration": "时长描述",
            "location": "地点",
            "estimated_cost": 费用整数,
            "notes": "备注说明"
        }
    ],
    "tips": ["注意事项1", "注意事项2"]
}

要求：
1. 活动安排要合理，考虑时间、距离、体力等因素
2. 每天包含早中晚餐安排
3. 需要包含交通和住宿安排
4. 费用估算要合理"""


def build_trip_prompt(demand: TripDemand) -> str:
    days = (demand.end_date - demand.start_date).days + 1
    interests_str = "、".join(demand.interests) if demand.interests else "无特殊偏好"

    type_names = {
        "team_building": "团队建设",
        "study_tour": "研学旅行",
        "regular_tour": "常规旅游",
        "family": "亲子游",
        "business": "商务考察",
        "adventure": "探险游",
        "leisure": "休闲度假",
    }
    trip_type_name = type_names.get(demand.trip_type, "常规旅游")

    return f"""请根据以下需求生成详细的行程安排：

行程类型：{trip_type_name}
出行日期：{demand.start_date} 至 {demand.end_date}（共{days}天）
出行人数：{demand.participants}人
预算范围：{demand.budget_min}-{demand.budget_max}元/人
兴趣偏好：{interests_str}
目的地：{demand.destination or "待定（请推荐合适的目的地）"}
特殊需求：{demand.special_needs or "无"}

请为每天安排合理的活动，包括早餐、上午活动、午餐、下午活动、晚餐和住宿。
请直接返回JSON，不要包含```json```标记。"""


def generate_fallback(demand: TripDemand) -> TripSuggestion:
    """AI调用失败时的兜底方案"""
    days = (demand.end_date - demand.start_date).days + 1
    type_names = {
        "team_building": "团队建设",
        "family": "亲子游",
        "business": "商务考察",
        "adventure": "探险游",
        "leisure": "休闲度假",
    }
    trip_type_name = type_names.get(demand.trip_type, "常规旅游")

    activities = []
    for day in range(1, days + 1):
        activities.extend([
            ActivitySuggestion(day=day, time="07:30", type="meal", name="酒店早餐", duration="1小时", estimated_cost=0),
            ActivitySuggestion(day=day, time="09:00", type="attraction", name=f"第{day}天上午景点游览", duration="3小时", location="待定", estimated_cost=100),
            ActivitySuggestion(day=day, time="12:00", type="meal", name="午餐", duration="1.5小时", estimated_cost=80),
            ActivitySuggestion(day=day, time="14:00", type="attraction", name=f"第{day}天下午活动", duration="3小时", location="待定", estimated_cost=80),
            ActivitySuggestion(day=day, time="18:00", type="meal", name="晚餐", duration="1.5小时", estimated_cost=100),
        ])
        if day < days:
            activities.append(ActivitySuggestion(day=day, time="20:00", type="hotel", name="入住酒店", duration="12小时", estimated_cost=300))

    return TripSuggestion(
        title=f"{demand.destination or ''}{'·' if demand.destination else ''}{days}天{trip_type_name}行程",
        summary=f"为{demand.participants}人定制的{days}天{trip_type_name}行程方案（AI未响应，已生成默认方案）",
        total_days=days,
        estimated_budget=(demand.budget_min + demand.budget_max) // 2,
        activities=activities,
        tips=["请提前预订酒店和门票", "注意天气变化，携带合适衣物", "保管好个人贵重物品", "此为默认方案，建议配置AI API Key后重新生成"]
    )

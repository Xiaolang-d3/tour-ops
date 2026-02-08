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

async def call_qwen_api(messages: list, stream: bool = False) -> dict | httpx.Response:
    """
    调用通义千问API（DashScope OpenAI兼容接口）
    文档: https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen
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

    if stream:
        payload["stream"] = True
        client = httpx.AsyncClient(timeout=120.0)
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

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"AI API 调用失败 (HTTP {response.status_code}): {response.text}"
            )

        return response.json()


def extract_json_from_content(content: str) -> dict | None:
    """从AI响应内容中提取JSON"""
    # 先尝试直接解析
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        pass

    # 尝试提取 ```json ... ``` 代码块
    import re
    json_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', content, re.DOTALL)
    if json_block:
        try:
            return json.loads(json_block.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 尝试提取 { ... } 块
    start = content.find("{")
    end = content.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

    return None


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
        result = await call_qwen_api(messages)
        content = result["choices"][0]["message"]["content"]
        data = extract_json_from_content(content)

        if data:
            days = (demand.end_date - demand.start_date).days + 1
            # 确保字段存在
            data.setdefault("title", f"{days}天行程方案")
            data.setdefault("summary", "AI生成的行程建议")
            data.setdefault("total_days", days)
            data.setdefault("estimated_budget", (demand.budget_min + demand.budget_max) // 2)
            data.setdefault("activities", [])
            data.setdefault("tips", [])
            return TripSuggestion(**data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI generate_trip] 解析失败: {e}")

    # 解析失败时返回兜底方案
    return generate_fallback(demand)


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
async def ai_chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """AI智能对话 - 流式响应（SSE）"""
    messages = [
        {"role": "system", "content": TRAVEL_ASSISTANT_SYSTEM_PROMPT}
    ]

    if request.context:
        messages[0]["content"] += f"\n\n当前行程上下文信息：\n{request.context}"

    for msg in request.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    try:
        response, client = await call_qwen_api(messages, stream=True)
    except HTTPException:
        raise

    async def event_generator():
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
                            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        continue
        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


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

TRAVEL_ASSISTANT_SYSTEM_PROMPT = """你是TourOps旅行编排系统的AI助手。你擅长：
1. 旅行行程规划和优化建议
2. 目的地推荐和旅行攻略
3. 预算分析和费用估算
4. 景点、美食、住宿推荐
5. 旅行注意事项和安全提示

请用友好、专业的语气回复。回复要简洁实用，避免过长的文字。
如果用户的问题与旅行无关，礼貌地引导话题回到旅行相关内容。"""


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

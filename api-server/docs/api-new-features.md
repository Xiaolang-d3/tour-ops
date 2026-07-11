# TourOps 新增 API 文档

## 概述

本文档描述后端新增的 API 接口，供前端开发对接使用。

**Base URL**: `http://localhost:8000/api`  
**认证方式**: Bearer Token (JWT)

---

## 1. 导出功能

### 1.1 导出 PDF 行程单

```
GET /trips/{trip_id}/export/pdf
```

**描述**: 导出行程的 PDF 文件，包含按日期分组的活动列表和费用汇总。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trip_id | path | 是 | 行程 ID |

**响应**: 
- Content-Type: `application/pdf`
- 直接返回 PDF 文件流

**前端调用示例**:
```javascript
const downloadPDF = async (tripId) => {
  const response = await fetch(`/api/trips/${tripId}/export/pdf`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `trip_${tripId}.pdf`;
  a.click();
};
```

---

### 1.2 导出 Excel 明细表

```
GET /trips/{trip_id}/export/excel
```

**描述**: 导出行程的 Excel 文件，包含活动明细和费用统计。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trip_id | path | 是 | 行程 ID |

**响应**: 
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 直接返回 Excel 文件流

---

## 2. 分享功能

### 2.1 生成分享二维码

```
GET /trips/{trip_id}/qrcode?base_url={base_url}
```

**描述**: 生成行程分享链接的二维码图片。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trip_id | path | 是 | 行程 ID |
| base_url | query | 否 | 前端基础 URL，默认 `http://localhost:3000` |

**响应**: 
- Content-Type: `image/png`
- 返回二维码 PNG 图片

**前端调用示例**:
```javascript
// 直接用 img 标签显示
<img src={`/api/trips/${tripId}/qrcode?base_url=${window.location.origin}`} />
```

---

### 2.2 获取分享信息

```
GET /trips/{trip_id}/share-info
```

**描述**: 获取行程的分享码和分享链接。

**响应**:
```json
{
  "trip_id": 1,
  "trip_name": "云南7日游",
  "share_code": "abc123def456",
  "share_url": "/share/abc123def456"
}
```

---

## 3. 行程操作

### 3.1 复制行程

```
POST /trips/{trip_id}/copy
```

**描述**: 复制整个行程，包括所有活动。新行程名称会加上 "(副本)" 后缀。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trip_id | path | 是 | 要复制的行程 ID |

**响应**: 返回新创建的行程对象
```json
{
  "id": 2,
  "name": "云南7日游 (副本)",
  "start_date": "2026-03-01",
  "end_date": "2026-03-07",
  ...
}
```

---

## 4. 活动管理

### 4.1 批量更新活动排序

```
PUT /trips/{trip_id}/activities/reorder
```

**描述**: 批量更新活动的排序顺序，用于拖拽排序功能。

**请求体**:
```json
{
  "items": [
    { "id": 1, "sort_order": 0 },
    { "id": 2, "sort_order": 1 },
    { "id": 3, "sort_order": 2 }
  ]
}
```

**响应**:
```json
{
  "message": "排序更新成功",
  "count": 3
}
```

**前端调用示例** (使用 dnd-kit):
```javascript
const handleDragEnd = async (event) => {
  const { active, over } = event;
  if (active.id !== over.id) {
    const newItems = arrayMove(items, oldIndex, newIndex);
    const reorderData = newItems.map((item, index) => ({
      id: item.id,
      sort_order: index
    }));
    await fetch(`/api/trips/${tripId}/activities/reorder`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ items: reorderData })
    });
  }
};
```

---

### 4.2 检测时间冲突

```
POST /trips/{trip_id}/activities/check-conflict
```

**描述**: 检测指定时间段是否与已有活动冲突。

**请求体**:
```json
{
  "start_time": "2026-03-01T09:00:00",
  "end_time": "2026-03-01T12:00:00",
  "exclude_activity_id": 5  // 可选，编辑时排除自身
}
```

**响应**:
```json
{
  "has_conflict": true,
  "conflicts": [
    {
      "id": 3,
      "name": "石林景区游览",
      "start_time": "2026-03-01T10:00:00",
      "end_time": "2026-03-01T14:00:00"
    }
  ]
}
```

**使用场景**: 在添加/编辑活动时，选择时间后调用此接口检测冲突，有冲突时显示警告。

---

## 5. 资源可用性查询

### 5.1 查询可用导游

```
GET /resources/guides/available?start={start}&end={end}
```

**描述**: 查询指定时间段内没有被占用的导游。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start | query | 是 | 开始时间 (ISO 格式) |
| end | query | 是 | 结束时间 (ISO 格式) |

**响应**:
```json
[
  { "id": 1, "name": "张导游", "contact_phone": "13800138001" },
  { "id": 3, "name": "王导游", "contact_phone": "13800138003" }
]
```

---

### 5.2 查询可用车辆

```
GET /resources/vehicles/available?start={start}&end={end}
```

**描述**: 查询指定时间段内没有被占用的车辆。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start | query | 是 | 开始时间 (ISO 格式) |
| end | query | 是 | 结束时间 (ISO 格式) |

**响应**:
```json
[
  { "id": 1, "name": "商务车A", "plate_number": "云A12345", "seats": 7 },
  { "id": 2, "name": "大巴B", "plate_number": "云A67890", "seats": 45 }
]
```

---

### 5.3 查询资源占用情况

```
GET /resources/{resource_type}/{resource_id}/schedule?start={start}&end={end}
```

**描述**: 查询某个资源在指定时间段内的占用情况。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resource_type | path | 是 | 资源类型: `guide`, `vehicle`, `hotel`, `restaurant` |
| resource_id | path | 是 | 资源 ID |
| start | query | 是 | 开始时间 (ISO 格式) |
| end | query | 是 | 结束时间 (ISO 格式) |

**响应**:
```json
{
  "resource_type": "guide",
  "resource_id": 1,
  "schedule": [
    {
      "activity_id": 5,
      "activity_name": "丽江古城导览",
      "trip_id": 1,
      "trip_name": "云南7日游",
      "start_time": "2026-03-02T09:00:00",
      "end_time": "2026-03-02T17:00:00"
    }
  ]
}
```

---

## 6. 模板功能

### 6.1 从行程创建模板

```
POST /templates/from-trip/{trip_id}
```

**描述**: 将现有行程保存为模板，方便复用。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trip_id | path | 是 | 行程 ID |

**请求体**:
```json
{
  "name": "经典云南7日模板",
  "category": "family"  // 可选值: family, honeymoon, business, adventure
}
```

**响应**: 返回创建的模板对象
```json
{
  "id": 1,
  "name": "经典云南7日模板",
  "category": "family",
  "duration_days": 7,
  "content": {
    "activities": [...],
    "preferences": "...",
    "special_requirements": "..."
  },
  "created_at": "2026-02-01T12:00:00"
}
```

---

## 错误响应格式

所有接口错误统一返回:
```json
{
  "detail": "错误信息"
}
```

常见 HTTP 状态码:
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误

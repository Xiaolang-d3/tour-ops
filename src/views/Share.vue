<template>
  <div class="share-page">
    <!-- 顶部品牌条 -->
    <div class="share-brand">
      <span class="brand-logo">✈️ TourOps</span>
      <span class="brand-hint">行程预览</span>
    </div>

    <div v-if="trip" class="share-container">
      <!-- 行程信息卡片 -->
      <div class="trip-hero">
        <h1 class="trip-title">{{ trip.name }}</h1>
        <div class="trip-meta">
          <span class="meta-item">📅 {{ trip.start_date }} ~ {{ trip.end_date }}</span>
          <span class="meta-item">👥 {{ trip.guest_count }}人</span>
          <span class="meta-item" v-if="trip.activities?.length">📋 {{ trip.activities.length }}项活动</span>
        </div>
      </div>

      <!-- 活动时间线 -->
      <div class="timeline-section" v-if="trip.activities?.length">
        <div v-for="(dayActs, dayLabel) in groupedActivities" :key="dayLabel" class="day-block">
          <div class="day-label">
            <span class="day-dot"></span>
            <span>{{ dayLabel }}</span>
          </div>
          <div class="day-cards">
            <div v-for="act in dayActs" :key="act.id" class="act-card">
              <div class="act-icon" :class="act.type">{{ typeIcon(act.type) }}</div>
              <div class="act-info">
                <div class="act-top">
                  <span class="act-name">{{ act.name }}</span>
                  <span class="act-time">{{ fmtTime(act.start_time) }} - {{ fmtTime(act.end_time) }}</span>
                </div>
                <div class="act-bottom">
                  <span v-if="act.location" class="act-loc">📍 {{ act.location }}</span>
                  <span v-if="act.notes" class="act-note">{{ act.notes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-acts">
        <p>暂无活动安排</p>
      </div>

      <!-- ========== 评价区域 ========== -->
      <div class="review-zone">
        <div class="zone-title">
          <span class="zone-icon">📊</span>
          <span>行程评价</span>
        </div>

        <!-- 评价概览（有评价时显示） -->
        <div v-if="reviews.length" class="review-summary">
          <div class="summary-score">
            <div class="big-score">{{ avgRating.toFixed(1) }}</div>
            <div class="score-stars">
              <span v-for="s in 5" :key="s" class="s-star" :class="{ on: s <= Math.round(avgRating) }">★</span>
            </div>
            <div class="score-count">{{ reviews.length }} 条评价</div>
          </div>
          <div class="summary-bars">
            <div v-for="i in [5,4,3,2,1]" :key="i" class="bar-row">
              <span class="bar-label">{{ i }}星</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: getPercent(i) + '%' }"></div>
              </div>
              <span class="bar-num">{{ getCount(i) }}</span>
            </div>
          </div>
          <div class="summary-tags" v-if="topTags.length">
            <span v-for="t in topTags" :key="t.tag" class="sum-tag">
              {{ t.tag }}
              <span class="sum-tag-n">{{ t.count }}</span>
            </span>
          </div>
        </div>

        <!-- 提交评价表单 -->
        <div v-if="!submitted" class="review-form-card">
          <div class="form-header">
            <span class="form-title">✍️ 写评价</span>
            <span class="form-hint">您的真实反馈将帮助我们持续改进</span>
          </div>

          <!-- 星级 -->
          <div class="form-field">
            <div class="rating-row">
              <span
                v-for="s in 5" :key="s"
                class="rate-star" :class="{ active: s <= (hoverRating || reviewForm.rating), hover: hoverRating > 0 }"
                @mouseenter="hoverRating = s" @mouseleave="hoverRating = 0"
                @click="reviewForm.rating = s"
              >★</span>
              <span class="rate-label" v-if="reviewForm.rating || hoverRating">
                {{ ratingLabels[(hoverRating || reviewForm.rating) - 1] }}
              </span>
              <span class="rate-placeholder" v-else>点击评分</span>
            </div>
          </div>

          <!-- 标签 -->
          <div class="form-field">
            <label class="field-label">选择标签</label>
            <div class="tag-group">
              <div class="tag-row positive">
                <span
                  v-for="tag in positiveTags" :key="tag.value"
                  class="ftag" :class="{ active: reviewForm.tags.includes(tag.value) }"
                  @click="toggleTag(tag.value)"
                >{{ tag.label }}</span>
              </div>
              <div class="tag-row negative">
                <span
                  v-for="tag in negativeTags" :key="tag.value"
                  class="ftag neg" :class="{ active: reviewForm.tags.includes(tag.value) }"
                  @click="toggleTag(tag.value)"
                >{{ tag.label }}</span>
              </div>
            </div>
          </div>

          <!-- 文字评价 -->
          <div class="form-field">
            <label class="field-label">补充评价 <span class="opt">(选填)</span></label>
            <el-input v-model="reviewForm.comment" type="textarea" :rows="3" placeholder="分享您的真实体验和感受..." maxlength="500" show-word-limit />
          </div>

          <!-- 称呼 + 提交 -->
          <div class="form-footer">
            <el-input v-model="reviewForm.reviewer_name" placeholder="您的称呼（选填）" maxlength="20" class="name-input" />
            <el-button type="primary" round :loading="submitting" :disabled="!reviewForm.rating" @click="handleSubmit">
              提交评价
            </el-button>
          </div>
        </div>

        <!-- 提交成功 -->
        <div v-else class="submit-success">
          <div class="success-emoji">🎉</div>
          <h3>感谢您的评价</h3>
          <p>您的反馈对我们非常重要</p>
        </div>

        <!-- 评价列表 -->
        <div v-if="reviews.length" class="review-list">
          <div class="list-header">💬 全部评价</div>
          <div v-for="r in reviews" :key="r.id" class="rv-item">
            <div class="rv-avatar">{{ (r.reviewer_name || '匿')[0] }}</div>
            <div class="rv-body">
              <div class="rv-top">
                <span class="rv-name">{{ r.reviewer_name || '匿名用户' }}</span>
                <span class="rv-stars">{{ '★'.repeat(r.rating) }}<span class="rv-stars-off">{{ '★'.repeat(5 - r.rating) }}</span></span>
                <span class="rv-date">{{ fmtDate(r.created_at) }}</span>
              </div>
              <div class="rv-tags" v-if="r.tags?.length">
                <span v-for="t in r.tags" :key="t" class="rv-tag">{{ t }}</span>
              </div>
              <p v-if="r.comment" class="rv-comment">{{ r.comment }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" style="text-align:center;margin-top:100px">
      <el-result icon="warning" title="行程不存在" sub-title="链接可能已失效" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { getSharedTrip } from '@/api/public'
import { submitPublicReview, getPublicReviews } from '@/api/reviews'
import { ElMessage } from 'element-plus'

const route = useRoute()
const trip = ref(null)
const error = ref(false)
const reviews = ref([])
const submitted = ref(false)
const submitting = ref(false)
const hoverRating = ref(0)

const positiveTags = [
  { label: '👍 行程合理', value: '行程合理' },
  { label: '💯 服务周到', value: '服务周到' },
  { label: '🏨 住宿满意', value: '住宿满意' },
  { label: '🍜 餐饮不错', value: '餐饮不错' },
  { label: '🎤 导游专业', value: '导游专业' },
  { label: '🚌 交通便利', value: '交通便利' },
  { label: '💰 性价比高', value: '性价比高' },
  { label: '🎯 体验丰富', value: '体验丰富' },
]
const negativeTags = [
  { label: '⏰ 时间紧凑', value: '时间紧凑' },
  { label: '🍽️ 餐饮一般', value: '餐饮一般' },
  { label: '😐 体验一般', value: '体验一般' },
  { label: '💸 价格偏高', value: '价格偏高' },
]
const ratingLabels = ['很差', '较差', '一般', '满意', '非常满意']

const reviewForm = reactive({ rating: 0, tags: [], comment: '', reviewer_name: '' })

const avgRating = computed(() => {
  if (!reviews.value.length) return 0
  return reviews.value.reduce((s, r) => s + r.rating, 0) / reviews.value.length
})

const topTags = computed(() => {
  const map = {}
  reviews.value.forEach(r => (r.tags || []).forEach(t => { map[t] = (map[t] || 0) + 1 }))
  return Object.entries(map).map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count).slice(0, 8)
})

function getCount(star) {
  return reviews.value.filter(r => r.rating === star).length
}
function getPercent(star) {
  if (!reviews.value.length) return 0
  return (getCount(star) / reviews.value.length) * 100
}

const groupedActivities = computed(() => {
  if (!trip.value?.activities?.length) return {}
  const groups = {}
  const sorted = [...trip.value.activities].sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  for (const act of sorted) {
    const d = dayjs(act.start_time).format('MM月DD日')
    if (!groups[d]) groups[d] = []
    groups[d].push(act)
  }
  return groups
})

const typeIcon = (t) => ({ transport: '🚌', attraction: '🏛️', meal: '🍽️', hotel: '🏨', free: '🎯' }[t] || '📌')
const fmtTime = (t) => t ? dayjs(t).format('HH:mm') : ''
const fmtDate = (t) => t ? dayjs(t).format('MM-DD HH:mm') : ''

function toggleTag(tag) {
  const idx = reviewForm.tags.indexOf(tag)
  if (idx >= 0) reviewForm.tags.splice(idx, 1)
  else reviewForm.tags.push(tag)
}

async function handleSubmit() {
  if (!reviewForm.rating) return
  submitting.value = true
  try {
    await submitPublicReview(route.params.code, {
      rating: reviewForm.rating, tags: reviewForm.tags,
      comment: reviewForm.comment || null, reviewer_name: reviewForm.reviewer_name || null,
    })
    submitted.value = true
    ElMessage.success('评价提交成功')
    await loadReviews()
  } catch { ElMessage.error('提交失败，请重试') }
  finally { submitting.value = false }
}

async function loadReviews() {
  try { reviews.value = await getPublicReviews(route.params.code) } catch {}
}

onMounted(async () => {
  try {
    trip.value = await getSharedTrip(route.params.code)
    await loadReviews()
  } catch { error.value = true }
})
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  background: #f5f6fa;
}

/* 品牌条 */
.share-brand {
  background: #fff;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #eef0f4;
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand-logo { font-size: 16px; font-weight: 800; color: #7c3aed; }
.brand-hint { font-size: 13px; color: #a8abb2; }

.share-container { max-width: 780px; margin: 0 auto; padding: 24px 16px 60px; }

/* 行程头部 */
.trip-hero {
  background: linear-gradient(135deg, #7c3aed, #6366f1);
  border-radius: 18px;
  padding: 32px 28px;
  color: #fff;
  margin-bottom: 24px;
}
.trip-title { font-size: 24px; font-weight: 800; margin: 0 0 12px; }
.trip-meta { display: flex; flex-wrap: wrap; gap: 16px; font-size: 14px; opacity: 0.9; }

/* 时间线 */
.timeline-section { margin-bottom: 32px; }
.day-block { margin-bottom: 24px; }
.day-label {
  display: flex; align-items: center; gap: 10px;
  font-size: 15px; font-weight: 700; color: #7c3aed;
  margin-bottom: 12px;
}
.day-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  box-shadow: 0 0 0 3px rgba(139,92,246,0.15);
}
.day-cards { display: flex; flex-direction: column; gap: 8px; margin-left: 4px; padding-left: 18px; border-left: 2px solid #ede9fe; }
.act-card {
  display: flex; gap: 12px; padding: 14px 16px;
  background: #fff; border-radius: 12px;
  border: 1px solid #f0f2f5;
  transition: all 0.2s;
}
.act-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.act-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.act-icon.transport { background: #fff7ed; }
.act-icon.attraction { background: #ecfdf5; }
.act-icon.meal { background: #fef2f2; }
.act-icon.hotel { background: #ede9fe; }
.act-icon.free { background: #eff6ff; }
.act-info { flex: 1; min-width: 0; }
.act-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.act-name { font-size: 14px; font-weight: 600; color: #1a1a2e; }
.act-time { font-size: 12px; color: #a8abb2; flex-shrink: 0; }
.act-bottom { display: flex; flex-wrap: wrap; gap: 12px; }
.act-loc, .act-note { font-size: 12px; color: #909399; }
.empty-acts { text-align: center; padding: 40px 0; color: #c0c4cc; }

/* ========== 评价区域 ========== */
.review-zone {
  background: #fff;
  border-radius: 18px;
  padding: 28px;
  border: 1px solid #eef0f4;
}
.zone-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 18px; font-weight: 800; color: #1a1a2e;
  margin-bottom: 24px;
}
.zone-icon { font-size: 22px; }

/* 评价概览 */
.review-summary {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #faf8ff, #f5f3ff);
  border-radius: 14px;
  margin-bottom: 24px;
  border: 1px solid #ede9fe;
}
.summary-score { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; }
.big-score { font-size: 40px; font-weight: 900; color: #7c3aed; line-height: 1; }
.score-stars { display: flex; gap: 1px; }
.s-star { font-size: 14px; color: #dcdfe6; }
.s-star.on { color: #f59e0b; }
.score-count { font-size: 12px; color: #909399; }

.summary-bars { display: flex; flex-direction: column; gap: 5px; justify-content: center; }
.bar-row { display: flex; align-items: center; gap: 8px; }
.bar-label { font-size: 12px; color: #909399; width: 28px; text-align: right; }
.bar-track { flex: 1; height: 8px; background: #f0f0f5; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #8b5cf6, #a78bfa); border-radius: 4px; transition: width 0.5s; }
.bar-num { font-size: 11px; color: #c0c4cc; width: 18px; }

.summary-tags {
  grid-column: 1 / -1;
  display: flex; flex-wrap: wrap; gap: 8px;
  padding-top: 12px; border-top: 1px solid #e9e5f5;
}
.sum-tag {
  padding: 5px 14px; border-radius: 14px; font-size: 13px; font-weight: 500;
  background: #fff; color: #6d28d9; border: 1px solid #ddd6fe;
  display: flex; align-items: center; gap: 6px;
}
.sum-tag-n {
  font-size: 11px; font-weight: 800; color: #fff;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  padding: 1px 7px; border-radius: 10px;
}

/* 评价表单 */
.review-form-card {
  background: #fafbfd;
  border-radius: 14px;
  padding: 24px;
  border: 1px solid #eef0f4;
  margin-bottom: 24px;
}
.form-header { margin-bottom: 20px; }
.form-title { font-size: 16px; font-weight: 700; color: #1a1a2e; }
.form-hint { display: block; font-size: 12px; color: #a8abb2; margin-top: 4px; }

.form-field { margin-bottom: 20px; }
.field-label { font-size: 14px; font-weight: 600; color: #303133; display: block; margin-bottom: 10px; }
.opt { font-weight: 400; color: #c0c4cc; font-size: 12px; }

/* 星级 */
.rating-row { display: flex; align-items: center; gap: 6px; }
.rate-star {
  font-size: 36px; color: #e0e0e8; cursor: pointer;
  transition: all 0.15s ease; user-select: none;
}
.rate-star.active { color: #f59e0b; }
.rate-star.hover { transform: scale(1.15); }
.rate-label { margin-left: 12px; font-size: 15px; font-weight: 600; color: #f59e0b; }
.rate-placeholder { margin-left: 12px; font-size: 14px; color: #c0c4cc; }

/* 标签 */
.tag-group { display: flex; flex-direction: column; gap: 10px; }
.tag-row { display: flex; flex-wrap: wrap; gap: 8px; }
.ftag {
  padding: 7px 16px; border-radius: 20px; font-size: 13px; font-weight: 500;
  background: #fff; color: #606266; cursor: pointer;
  border: 1.5px solid #e8e8ed; transition: all 0.2s ease; user-select: none;
}
.ftag:hover { border-color: #c4b5fd; background: #faf8ff; }
.ftag.active {
  background: linear-gradient(135deg, #ede9fe, #e0e7ff); color: #6d28d9;
  border-color: #a78bfa; font-weight: 600;
  box-shadow: 0 2px 8px rgba(139,92,246,0.15);
}
.ftag.neg { border-color: #fde8e8; }
.ftag.neg:hover { border-color: #fca5a5; background: #fff5f5; }
.ftag.neg.active {
  background: linear-gradient(135deg, #fef2f2, #fee2e2); color: #dc2626;
  border-color: #fca5a5;
  box-shadow: 0 2px 8px rgba(239,68,68,0.12);
}

.form-footer {
  display: flex; align-items: center; gap: 12px; margin-top: 4px;
}
.name-input { max-width: 200px; }

/* 提交成功 */
.submit-success {
  text-align: center; padding: 32px 0; margin-bottom: 24px;
  background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
  border-radius: 14px; border: 1px solid #d1fae5;
}
.success-emoji { font-size: 48px; margin-bottom: 8px; }
.submit-success h3 { font-size: 18px; font-weight: 700; color: #059669; margin: 0 0 4px; }
.submit-success p { font-size: 13px; color: #6ee7b7; margin: 0; }

/* 评价列表 */
.review-list { border-top: 1px solid #f0f2f5; padding-top: 20px; }
.list-header { font-size: 15px; font-weight: 700; color: #303133; margin-bottom: 16px; }

.rv-item {
  display: flex; gap: 12px;
  padding: 16px 0; border-bottom: 1px solid #f8f9fc;
}
.rv-item:last-child { border-bottom: none; }
.rv-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
  color: #7c3aed; font-size: 14px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.rv-body { flex: 1; min-width: 0; }
.rv-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.rv-name { font-size: 14px; font-weight: 600; color: #303133; }
.rv-stars { color: #f59e0b; font-size: 13px; }
.rv-stars-off { color: #e0e0e8; }
.rv-date { font-size: 11px; color: #c0c4cc; margin-left: auto; }
.rv-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 6px; }
.rv-tag {
  padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: 500;
  background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #6d28d9;
  border: 1px solid #e9e5f5;
}
.rv-comment { font-size: 13px; color: #606266; line-height: 1.6; margin: 0; }

@media (max-width: 768px) {
  .share-container { padding: 16px 12px 40px; }
  .trip-hero { padding: 24px 20px; border-radius: 14px; }
  .trip-title { font-size: 20px; }
  .review-zone { padding: 20px 16px; border-radius: 14px; }
  .review-summary { grid-template-columns: 1fr; text-align: center; }
  .summary-score { flex-direction: row; gap: 12px; }
  .big-score { font-size: 32px; }
  .form-footer { flex-direction: column; align-items: stretch; }
  .name-input { max-width: 100%; }
  .rate-star { font-size: 30px; }
}
@media (max-width: 480px) {
  .trip-hero { padding: 20px 16px; }
  .trip-title { font-size: 18px; }
  .trip-meta { gap: 10px; font-size: 13px; }
  .rate-star { font-size: 26px; }
}
</style>

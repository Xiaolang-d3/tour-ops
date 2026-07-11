<template>
  <div class="admin-reviews" v-loading="loading">
    <!-- 概览卡片 -->
    <div class="overview-grid">
      <div class="overview-card score-card">
        <div class="score-ring">
          <svg viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#f0f2f5" stroke-width="10" />
            <circle cx="60" cy="60" r="50" fill="none" stroke="url(#scoreGrad)" stroke-width="10"
              :stroke-dasharray="`${scoreArc} 314`" stroke-linecap="round"
              transform="rotate(-90 60 60)" style="transition: stroke-dasharray 0.8s ease" />
            <defs><linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#f59e0b" /><stop offset="1" stop-color="#f97316" />
            </linearGradient></defs>
          </svg>
          <div class="score-center">
            <span class="score-num">{{ stats.avg_rating }}</span>
            <span class="score-label">平均评分</span>
          </div>
        </div>
        <div class="score-stars">
          <span v-for="s in 5" :key="s" class="star" :class="{ on: s <= Math.round(stats.avg_rating) }">★</span>
        </div>
        <div class="score-total">共 {{ stats.total }} 条评价</div>
      </div>

      <div class="overview-card dist-card">
        <div class="card-title">评分分布</div>
        <div class="dist-bars">
          <div v-for="i in [5,4,3,2,1]" :key="i" class="dist-row">
            <span class="dist-star">{{ i }}★</span>
            <div class="dist-track">
              <div class="dist-fill" :style="{ width: getDistPct(i) + '%', background: distColor(i) }"></div>
            </div>
            <span class="dist-count">{{ stats.rating_dist[String(i)] || 0 }}</span>
            <span class="dist-pct">{{ getDistPct(i) }}%</span>
          </div>
        </div>
      </div>

      <div class="overview-card tags-card">
        <div class="card-title">热门标签</div>
        <div class="tags-cloud" v-if="sortedTags.length">
          <div v-for="t in sortedTags" :key="t.tag" class="cloud-tag" :style="{ fontSize: getTagSize(t.count) + 'px' }">
            {{ t.tag }}
            <span class="tag-badge">{{ t.count }}</span>
          </div>
        </div>
        <div v-else class="empty-tags">暂无标签数据</div>
      </div>
    </div>

    <!-- 最近评价列表 -->
    <div class="recent-section">
      <div class="section-header">
        <div class="section-title">
          <span class="title-icon">💬</span> 最近评价
        </div>
      </div>

      <div v-if="stats.recent?.length" class="review-list">
        <div v-for="r in stats.recent" :key="r.id" class="review-item">
          <div class="review-left">
            <div class="reviewer-avatar">{{ (r.reviewer_name || '匿')[0] }}</div>
          </div>
          <div class="review-body">
            <div class="review-top">
              <span class="reviewer-name">{{ r.reviewer_name || '匿名用户' }}</span>
              <span class="review-stars">
                <span v-for="s in 5" :key="s" class="sm-star" :class="{ on: s <= r.rating }">★</span>
              </span>
              <span class="review-trip">
                <el-icon size="12"><Suitcase /></el-icon> {{ r.trip_name }}
              </span>
              <span class="review-date">{{ formatDate(r.created_at) }}</span>
            </div>
            <div class="review-tags" v-if="r.tags?.length">
              <span v-for="t in r.tags" :key="t" class="rv-tag">{{ t }}</span>
            </div>
            <p v-if="r.comment" class="review-comment">{{ r.comment }}</p>
          </div>
        </div>
      </div>
      <div v-else class="empty-reviews">
        <div class="empty-icon">📊</div>
        <p>暂无评价数据</p>
        <p class="empty-sub">客户通过分享链接提交评价后，数据将在此展示</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminReviewStats } from '@/api/reviews'
import dayjs from 'dayjs'

const loading = ref(false)
const stats = ref({ total: 0, avg_rating: 0, rating_dist: {}, tag_stats: {}, recent: [] })

const scoreArc = computed(() => (stats.value.avg_rating / 5) * 314)

const sortedTags = computed(() => {
  const ts = stats.value.tag_stats || {}
  return Object.entries(ts).map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count)
})

const maxTagCount = computed(() => sortedTags.value.length ? sortedTags.value[0].count : 1)

function getDistPct(star) {
  if (!stats.value.total) return 0
  return Math.round(((stats.value.rating_dist[String(star)] || 0) / stats.value.total) * 100)
}

function distColor(star) {
  const colors = { 5: '#10b981', 4: '#34d399', 3: '#f59e0b', 2: '#f97316', 1: '#ef4444' }
  return colors[star] || '#909399'
}

function getTagSize(count) {
  const min = 13, max = 20
  return min + ((count / maxTagCount.value) * (max - min))
}

function formatDate(dt) {
  if (!dt) return ''
  return dayjs(dt).format('M月D日 HH:mm')
}

onMounted(async () => {
  loading.value = true
  try { stats.value = await getAdminReviewStats() }
  catch { stats.value = { total: 0, avg_rating: 0, rating_dist: {}, tag_stats: {}, recent: [] } }
  finally { loading.value = false }
})
</script>

<style scoped>
.admin-reviews { max-width: 1200px; }

/* 概览网格 */
.overview-grid {
  display: grid;
  grid-template-columns: 240px 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.overview-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f0f0f0;
}
.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #1e1b4b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 评分卡片 */
.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.score-ring { position: relative; width: 120px; height: 120px; }
.score-ring svg { width: 100%; height: 100%; }
.score-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.score-num { font-size: 32px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.score-label { font-size: 11px; color: #9ca3af; margin-top: 2px; }
.score-stars { display: flex; gap: 2px; }
.star { font-size: 18px; color: #e5e7eb; }
.star.on { color: #f59e0b; }
.score-total { font-size: 13px; color: #9ca3af; }

/* 分布卡片 */
.dist-bars { display: flex; flex-direction: column; gap: 10px; }
.dist-row { display: flex; align-items: center; gap: 10px; }
.dist-star { font-size: 13px; color: #6b7280; width: 28px; text-align: right; flex-shrink: 0; font-weight: 600; }
.dist-track { flex: 1; height: 10px; background: #f3f4f6; border-radius: 5px; overflow: hidden; }
.dist-fill { height: 100%; border-radius: 5px; transition: width 0.6s ease; }
.dist-count { font-size: 13px; font-weight: 700; color: #1e1b4b; width: 24px; text-align: right; }
.dist-pct { font-size: 11px; color: #9ca3af; width: 36px; text-align: right; }

/* 标签云 */
.tags-cloud { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.cloud-tag {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 20px;
  background: linear-gradient(135deg, #faf8ff, #f5f3ff);
  color: #6d28d9; border: 1px solid #e9e5f5;
  font-weight: 500; cursor: default;
  transition: all 0.2s;
}
.cloud-tag:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(139,92,246,0.12); }
.tag-badge {
  font-size: 11px; font-weight: 800; color: #fff;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  padding: 1px 7px; border-radius: 10px; min-width: 20px; text-align: center;
}
.empty-tags { color: #c0c4cc; font-size: 13px; text-align: center; padding: 20px 0; }

/* 最近评价 */
.recent-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f0f0f0;
}
.section-header { margin-bottom: 20px; }
.section-title {
  font-size: 16px; font-weight: 700; color: #1e1b4b;
  display: flex; align-items: center; gap: 8px;
}
.title-icon { font-size: 20px; }

.review-list { display: flex; flex-direction: column; gap: 4px; }
.review-item {
  display: flex; gap: 14px;
  padding: 16px 12px;
  border-radius: 12px;
  transition: background 0.2s;
}
.review-item:hover { background: #fafbfd; }
.reviewer-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
  color: #7c3aed; font-size: 15px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.review-body { flex: 1; min-width: 0; }
.review-top {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 6px; flex-wrap: wrap;
}
.reviewer-name { font-size: 14px; font-weight: 600; color: #1e1b4b; }
.review-stars { display: flex; gap: 1px; }
.sm-star { font-size: 13px; color: #e5e7eb; }
.sm-star.on { color: #f59e0b; }
.review-trip {
  display: flex; align-items: center; gap: 3px;
  font-size: 12px; color: #8b5cf6;
  background: #f5f3ff; padding: 2px 8px; border-radius: 6px;
}
.review-date { font-size: 11px; color: #c0c4cc; margin-left: auto; }
.review-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 6px; }
.rv-tag {
  padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: 500;
  background: #fffbeb; color: #d97706; border: 1px solid #fef3c7;
}
.review-comment { font-size: 13px; color: #4b5563; line-height: 1.6; margin: 0; }

.empty-reviews { text-align: center; padding: 48px 0; color: #9ca3af; }
.empty-icon { font-size: 48px; margin-bottom: 8px; }
.empty-reviews p { margin: 0 0 4px; font-size: 14px; }
.empty-sub { font-size: 12px; color: #c0c4cc; }

@media (max-width: 1024px) {
  .overview-grid { grid-template-columns: 1fr 1fr; }
  .score-card { grid-column: 1 / -1; flex-direction: row; gap: 24px; }
  .score-ring { width: 100px; height: 100px; }
  .score-num { font-size: 28px; }
}
@media (max-width: 768px) {
  .overview-grid { grid-template-columns: 1fr; }
  .score-card { flex-direction: column; }
  .review-top { flex-direction: column; align-items: flex-start; gap: 4px; }
  .review-date { margin-left: 0; }
}
</style>

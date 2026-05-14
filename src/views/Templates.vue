<template>
  <div class="templates-page" :class="{ 'admin-template-page': isAdminView }">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">{{ isAdminView ? '模板管理' : '📚 模板库' }}</h2>
        <span class="page-subtitle">{{ isAdminView ? '维护可复用的行程模板' : '选择模板快速创建行程' }}</span>
      </div>
      <div class="page-header-right">
        <el-button v-if="isAdminView" type="primary" round @click="openCreateTemplate">
          <el-icon><Plus /></el-icon> 新建模板
        </el-button>
        <el-input v-model="searchText" placeholder="搜索模板..." prefix-icon="Search" clearable class="search-input" @input="onSearch" />
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-chips">
        <div class="filter-chip" :class="{ active: !filterCategory }" @click="filterCategory = ''; loadTemplates()">
          <span class="chip-icon">📋</span>
          <span>全部</span>
          <span class="chip-count">{{ allCount }}</span>
        </div>
        <div class="filter-chip" :class="{ active: filterCategory === 'family' }" @click="filterCategory = 'family'; loadTemplates()">
          <span class="chip-icon">👨‍👩‍👧‍👦</span>
          <span>亲子游</span>
        </div>
        <div class="filter-chip" :class="{ active: filterCategory === 'business' }" @click="filterCategory = 'business'; loadTemplates()">
          <span class="chip-icon">💼</span>
          <span>商务</span>
        </div>
        <div class="filter-chip" :class="{ active: filterCategory === 'team_building' }" @click="filterCategory = 'team_building'; loadTemplates()">
          <span class="chip-icon">🤝</span>
          <span>团建</span>
        </div>
        <div class="filter-chip" :class="{ active: filterCategory === 'adventure' }" @click="filterCategory = 'adventure'; loadTemplates()">
          <span class="chip-icon">⛰️</span>
          <span>探险</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="tpl-grid">
      <div v-for="i in 6" :key="i" class="tpl-grid-item">
        <div class="tpl-card"><el-skeleton :rows="5" animated /></div>
      </div>
    </div>

    <transition-group v-else-if="filteredTemplates.length" name="card-list" tag="div" class="tpl-grid">
      <div v-for="tpl in filteredTemplates" :key="tpl.id" class="tpl-grid-item">
        <div class="tpl-card" @click="openDetail(tpl)">
          <div class="tpl-hero" :class="tpl.category">
            <div class="tpl-hero-deco"></div>
            <div class="tpl-hero-deco2"></div>
            <div class="tpl-hero-content">
              <span class="tpl-emoji">{{ categoryEmoji(tpl.category) }}</span>
              <div class="tpl-hero-text">
                <h3 class="tpl-name">{{ tpl.name }}</h3>
                <span class="tpl-category-label">{{ categoryLabel(tpl.category) }}</span>
              </div>
            </div>
            <div class="tpl-duration-badge">{{ tpl.duration_days }}天</div>
          </div>

          <div class="tpl-info">
            <div class="tpl-info-row">
              <div class="tpl-info-item">
                <el-icon size="13"><List /></el-icon>
                <span>{{ templateActivities(tpl).length }} 项活动</span>
              </div>
              <div class="tpl-info-item" v-if="tpl.content?.guest_count">
                <el-icon size="13"><User /></el-icon>
                <span>{{ tpl.content.guest_count }} 人</span>
              </div>
              <div class="tpl-info-item" v-if="tpl.content?.budget">
                <el-icon size="13"><Money /></el-icon>
                <span>¥{{ Number(tpl.content.budget).toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <div class="tpl-highlights">
            <span v-for="tag in getHighlightTags(tpl)" :key="tag" class="highlight-tag">{{ tag }}</span>
            <span v-if="!getHighlightTags(tpl).length" class="highlight-tag muted">暂无亮点</span>
          </div>

          <div class="tpl-footer">
            <template v-if="isAdminView">
              <span class="tpl-footer-hint">模板维护</span>
              <span class="tpl-admin-actions" @click.stop>
                <el-button class="tpl-action-btn" size="small" round @click="openDetail(tpl)">
                  查看
                </el-button>
                <el-button class="tpl-action-btn primary" size="small" round @click="openEditTemplate(tpl)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button class="tpl-action-btn danger" size="small" circle @click="confirmDeleteTemplate(tpl)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </span>
            </template>
            <template v-else>
              <span class="tpl-footer-hint">点击查看详情</span>
              <el-icon size="14" class="tpl-footer-arrow"><ArrowRight /></el-icon>
            </template>
          </div>
        </div>
      </div>
    </transition-group>

    <div v-else class="empty-wrap">
      <div class="empty-icon">📦</div>
      <p class="empty-title">{{ searchText ? '未找到匹配的模板' : filterCategory ? '该分类暂无模板' : '暂无模板' }}</p>
      <p class="empty-desc">
        {{ searchText ? '试试其他关键词' : filterCategory ? '试试查看其他分类' : isAdminView ? '新建一个模板，后续计划员就能快速复用' : '管理员可在后台添加模板' }}
      </p>
      <el-button v-if="isAdminView && !filterCategory && !searchText" type="primary" round @click="openCreateTemplate">
        <el-icon><Plus /></el-icon> 新建模板
      </el-button>
      <el-button v-else-if="filterCategory || searchText" round @click="filterCategory = ''; searchText = ''; loadTemplates()">查看全部</el-button>
    </div>

    <el-drawer v-model="showDetail" :title="null" size="520px" :with-header="false" class="tpl-detail-drawer" destroy-on-close>
      <template v-if="selectedTemplate">
        <div class="detail-header" :class="selectedTemplate.category">
          <div class="detail-header-deco"></div>
          <div class="detail-close" @click="showDetail = false">
            <el-icon size="18"><Close /></el-icon>
          </div>
          <div class="detail-header-body">
            <span class="detail-emoji">{{ categoryEmoji(selectedTemplate.category) }}</span>
            <h2 class="detail-title">{{ selectedTemplate.name }}</h2>
            <div class="detail-meta">
              <span class="detail-meta-item">{{ categoryLabel(selectedTemplate.category) }}</span>
              <span class="detail-meta-sep">·</span>
              <span class="detail-meta-item">{{ selectedTemplate.duration_days }}天行程</span>
              <template v-if="selectedTemplate.content?.guest_count">
                <span class="detail-meta-sep">·</span>
                <span class="detail-meta-item">{{ selectedTemplate.content.guest_count }}人</span>
              </template>
              <template v-if="selectedTemplate.content?.budget">
                <span class="detail-meta-sep">·</span>
                <span class="detail-meta-item">¥{{ Number(selectedTemplate.content.budget).toLocaleString() }}</span>
              </template>
            </div>
          </div>
        </div>

        <div class="detail-timeline">
          <div v-for="day in detailDays" :key="day.day" class="timeline-day">
            <div class="timeline-day-header" @click="day.expanded = !day.expanded">
              <div class="timeline-day-dot" :class="selectedTemplate.category"></div>
              <span class="timeline-day-label">第{{ day.day }}天</span>
              <span class="timeline-day-count">{{ day.acts.length }}项活动</span>
              <span v-if="day.cost > 0" class="timeline-day-cost">¥{{ day.cost.toLocaleString() }}</span>
              <el-icon size="14" class="timeline-day-arrow" :class="{ expanded: day.expanded }"><ArrowDown /></el-icon>
            </div>
            <transition name="slide-down">
              <div v-show="day.expanded" class="timeline-day-acts">
                <div v-for="(act, idx) in day.acts" :key="idx" class="timeline-act">
                  <div class="timeline-act-time">{{ act.start_time || act.time || '--:--' }}</div>
                  <div class="timeline-act-line">
                    <div class="timeline-act-dot" :class="act.type"></div>
                    <div v-if="idx < day.acts.length - 1" class="timeline-act-connector"></div>
                  </div>
                  <div class="timeline-act-body">
                    <div class="timeline-act-name">
                      <span class="act-type-emoji">{{ actTypeIcon(act.type) }}</span>
                      {{ act.name }}
                    </div>
                    <div class="timeline-act-info">
                      <span v-if="act.location" class="act-info-item">📍 {{ act.location }}</span>
                      <span v-if="act.cost" class="act-info-item cost">¥{{ act.cost }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>

        <div class="detail-action-bar">
          <template v-if="isAdminView">
            <el-button size="large" round @click="showDetail = false" class="detail-cancel-btn">关闭</el-button>
            <el-button size="large" type="primary" round @click="openEditTemplate(selectedTemplate)" class="detail-edit-btn">
              <el-icon><Edit /></el-icon> 编辑模板
            </el-button>
            <el-button size="large" type="danger" plain round @click="confirmDeleteTemplate(selectedTemplate)">
              删除
            </el-button>
          </template>
          <template v-else>
            <el-button size="large" round @click="showDetail = false" class="detail-cancel-btn">返回</el-button>
            <el-button size="large" type="primary" round @click="openUseDialog" class="detail-use-btn">
              <el-icon><Right /></el-icon> 使用此模板创建行程
            </el-button>
          </template>
        </div>
      </template>
    </el-drawer>

    <el-dialog v-model="showUse" title="从模板创建行程" width="450px" destroy-on-close>
      <el-form :model="useForm" :rules="useRules" ref="useFormRef" label-width="80px">
        <el-form-item label="行程名称" prop="name">
          <el-input v-model="useForm.name" placeholder="输入行程名称" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="useForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" placeholder="选择出发日期" :disabled-date="(d) => d < new Date(new Date().setHours(0,0,0,0))" />
        </el-form-item>
        <el-form-item label="人数" prop="guest_count">
          <el-input-number v-model="useForm.guest_count" :min="1" :max="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUse = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleUseTemplate">创建行程</el-button>
      </template>
    </el-dialog>

    <el-drawer
      v-model="showTemplateDialog"
      :title="editingTemplate ? '编辑模板' : '新建模板'"
      size="760px"
      class="template-editor-drawer"
      destroy-on-close
    >
      <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-position="top" class="template-editor-form">
        <div class="editor-section">
          <div class="editor-section-head">
            <div>
              <h3>基础信息</h3>
              <p>设置模板在模板库中的名称、分类和行程跨度。</p>
            </div>
          </div>
          <div class="editor-grid three">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="templateForm.name" placeholder="输入模板名称" maxlength="80" show-word-limit />
            </el-form-item>
            <el-form-item label="模板分类" prop="category">
              <el-select v-model="templateForm.category" style="width:100%">
                <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="行程天数" prop="duration_days">
              <el-input-number v-model="templateForm.duration_days" :min="1" :max="60" controls-position="right" style="width:100%" />
            </el-form-item>
          </div>
        </div>

        <div class="editor-section">
          <div class="editor-section-head">
            <div>
              <h3>默认参数</h3>
              <p>计划员使用模板创建行程时，会优先带入这些默认值。</p>
            </div>
          </div>
          <div class="editor-grid two">
            <el-form-item label="默认人数" prop="guest_count">
              <el-input-number v-model="templateForm.guest_count" :min="1" :max="999" controls-position="right" style="width:100%" />
            </el-form-item>
            <el-form-item label="默认预算">
              <el-input v-model.number="templateForm.budget" type="number" min="0" placeholder="选填，单位：元">
                <template #prefix>¥</template>
              </el-input>
            </el-form-item>
          </div>
        </div>

        <div class="editor-section">
          <div class="editor-section-head">
            <div>
              <h3>活动编排</h3>
              <p>按天维护活动，保存后自动生成模板内容。</p>
            </div>
            <el-button type="primary" plain round @click="addActivity()">
              <el-icon><Plus /></el-icon> 新增活动
            </el-button>
          </div>

          <div v-if="!templateForm.activities.length" class="activities-empty">
            <span class="empty-icon small">🗓️</span>
            <p>还没有活动，请先添加一项活动。</p>
            <el-button type="primary" round @click="addActivity(1)">添加第 1 天活动</el-button>
          </div>

          <div v-else class="activity-days">
            <div v-for="day in editorDayGroups" :key="day.day" class="activity-day">
              <div class="activity-day-head">
                <span>第{{ day.day }}天</span>
                <em>{{ day.activities.length }} 项</em>
                <el-button link type="primary" @click="addActivity(day.day)">
                  <el-icon><Plus /></el-icon> 添加
                </el-button>
              </div>
              <div v-if="day.activities.length" class="activity-list">
                <div v-for="act in day.activities" :key="act.uid" class="activity-editor-row">
                  <div class="activity-main-fields">
                    <el-form-item label="类型" class="activity-field type-field">
                      <el-select v-model="act.type">
                        <el-option v-for="item in activityTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="活动名称" class="activity-field name-field" :class="{ 'is-error': !act.name?.trim() }">
                      <el-input v-model="act.name" placeholder="例如：西湖游船" />
                    </el-form-item>
                    <el-form-item label="开始" class="activity-field time-field">
                      <el-time-picker v-model="act.start_time" value-format="HH:mm" format="HH:mm" placeholder="09:00" style="width:100%" />
                    </el-form-item>
                    <el-form-item label="结束" class="activity-field time-field">
                      <el-time-picker v-model="act.end_time" value-format="HH:mm" format="HH:mm" placeholder="11:00" style="width:100%" />
                    </el-form-item>
                  </div>
                  <div class="activity-sub-fields">
                    <el-form-item label="地点" class="activity-field location-field">
                      <el-input v-model="act.location" placeholder="地点" />
                    </el-form-item>
                    <el-form-item label="费用" class="activity-field cost-field">
                      <el-input v-model.number="act.cost" type="number" min="0" placeholder="0">
                        <template #prefix>¥</template>
                      </el-input>
                    </el-form-item>
                    <el-form-item label="备注" class="activity-field notes-field">
                      <el-input v-model="act.notes" placeholder="选填" />
                    </el-form-item>
                  </div>
                  <div class="activity-row-actions">
                    <el-button text type="primary" @click="copyActivity(act)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                    <el-button text type="danger" @click="removeActivity(act.uid)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="invalidActivities.length" class="activity-day invalid">
              <div class="activity-day-head">
                <span>超出天数的活动</span>
                <em>{{ invalidActivities.length }} 项需调整</em>
              </div>
              <div class="activity-list">
                <div v-for="act in invalidActivities" :key="act.uid" class="activity-editor-row invalid-row">
                  <div class="activity-main-fields">
                    <el-form-item label="第几天" class="activity-field day-field is-error">
                      <el-input-number v-model="act.day" :min="1" :max="60" controls-position="right" style="width:100%" />
                    </el-form-item>
                    <el-form-item label="活动名称" class="activity-field name-field">
                      <el-input v-model="act.name" />
                    </el-form-item>
                    <el-form-item label="类型" class="activity-field type-field">
                      <el-select v-model="act.type">
                        <el-option v-for="item in activityTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                      </el-select>
                    </el-form-item>
                  </div>
                  <div class="activity-row-actions">
                    <el-button text type="danger" @click="removeActivity(act.uid)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-form>

      <template #footer>
        <div class="editor-footer">
          <div class="editor-footer-meta">
            共 {{ templateForm.activities.length }} 项活动
            <span v-if="invalidActivities.length">，{{ invalidActivities.length }} 项超出天数</span>
          </div>
          <div class="editor-footer-actions">
            <el-button @click="showTemplateDialog = false">取消</el-button>
            <el-button type="primary" :loading="savingTemplate" @click="handleSaveTemplate">保存模板</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate, createTripFromTemplate } from '@/api/templates'

const router = useRouter()
const route = useRoute()
const templates = ref([])
const allCount = ref(0)
const loading = ref(true)
const filterCategory = ref('')
const searchText = ref('')
const showDetail = ref(false)
const showUse = ref(false)
const creating = ref(false)
const showTemplateDialog = ref(false)
const savingTemplate = ref(false)
const selectedTemplate = ref(null)
const editingTemplate = ref(null)
const preservedContent = ref({})
const activityIdSeed = ref(1)
const useFormRef = ref(null)
const useForm = reactive({ name: '', start_date: '', guest_count: 1 })
const templateFormRef = ref(null)
const templateForm = reactive({
  name: '',
  category: 'family',
  duration_days: 1,
  guest_count: 1,
  budget: null,
  activities: []
})

const isAdminView = computed(() => route.path.startsWith('/admin'))

const categoryOptions = [
  { label: '亲子游', value: 'family' },
  { label: '商务考察', value: 'business' },
  { label: '团建拓展', value: 'team_building' },
  { label: '探险之旅', value: 'adventure' }
]

const activityTypeOptions = [
  { label: '交通', value: 'transport' },
  { label: '景点', value: 'attraction' },
  { label: '餐饮', value: 'meal' },
  { label: '住宿', value: 'hotel' },
  { label: '自由活动', value: 'free' }
]

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择模板分类', trigger: 'change' }],
  duration_days: [{ required: true, message: '请输入行程天数', trigger: 'change' }],
  guest_count: [{ required: true, message: '请输入默认人数', trigger: 'change' }]
}

const useRules = {
  name: [{ required: true, message: '请输入行程名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

const categoryLabel = (c) => ({ family: '亲子游', business: '商务考察', team_building: '团建拓展', adventure: '探险之旅' }[c] || c)
const categoryEmoji = (c) => ({ family: '👨‍👩‍👧‍👦', business: '💼', team_building: '🤝', adventure: '⛰️' }[c] || '📋')
const actTypeIcon = (t) => ({ transport: '🚌', attraction: '🏛️', meal: '🍽️', hotel: '🏨', free: '🎯' }[t] || '📌')

const filteredTemplates = computed(() => {
  if (!searchText.value) return templates.value
  const kw = searchText.value.toLowerCase()
  return templates.value.filter(t =>
    t.name.toLowerCase().includes(kw) ||
    categoryLabel(t.category).includes(kw) ||
    templateActivities(t).some(a => a.name?.toLowerCase().includes(kw) || a.location?.toLowerCase().includes(kw))
  )
})

const detailDays = computed(() => {
  if (!selectedTemplate.value) return []
  const dayMap = {}
  for (const act of templateActivities(selectedTemplate.value)) {
    const d = Number(act.day || 1)
    if (!dayMap[d]) dayMap[d] = { day: d, acts: [], cost: 0, expanded: d <= 3 }
    dayMap[d].acts.push(act)
    dayMap[d].cost += Number(act.cost || 0)
  }
  return Object.values(dayMap).sort((a, b) => a.day - b.day)
})

const editorDayGroups = computed(() => {
  const days = []
  for (let day = 1; day <= Number(templateForm.duration_days || 1); day += 1) {
    days.push({
      day,
      activities: templateForm.activities
        .filter(act => Number(act.day) === day)
        .sort(sortActivities)
    })
  }
  return days
})

const invalidActivities = computed(() =>
  templateForm.activities.filter(act => Number(act.day) > Number(templateForm.duration_days || 1) || Number(act.day) < 1)
)

function templateActivities(tpl) {
  return Array.isArray(tpl?.content?.activities) ? tpl.content.activities : []
}

function getHighlightTags(tpl) {
  const attractions = templateActivities(tpl).filter(a => a.type === 'attraction').map(a => a.name).filter(Boolean)
  return [...new Set(attractions)].slice(0, 4)
}

function sortActivities(a, b) {
  return String(a.start_time || a.time || '').localeCompare(String(b.start_time || b.time || ''))
}

function onSearch() {
  // 搜索由 computed 驱动
}

async function loadTemplates() {
  loading.value = true
  try {
    templates.value = await getTemplates(filterCategory.value || undefined)
    if (!filterCategory.value) allCount.value = templates.value.length
  } finally {
    loading.value = false
  }
}

function openDetail(tpl) {
  selectedTemplate.value = tpl
  showDetail.value = true
}

function openUseDialog() {
  const tpl = selectedTemplate.value
  useForm.name = `${tpl.name} - 新行程`
  useForm.start_date = ''
  useForm.guest_count = tpl.content?.guest_count || 1
  showUse.value = true
}

function normalizeContent(content) {
  if (typeof content === 'string') {
    try {
      return normalizeContent(JSON.parse(content))
    } catch {
      return {}
    }
  }
  if (!content || typeof content !== 'object' || Array.isArray(content)) return {}
  return { ...content }
}

function resetTemplateForm() {
  templateForm.name = ''
  templateForm.category = 'family'
  templateForm.duration_days = 1
  templateForm.guest_count = 1
  templateForm.budget = null
  templateForm.activities = []
  preservedContent.value = {}
}

function toEditorActivity(act = {}, day = 1) {
  const start = act.start_time || act.time || '09:00'
  return {
    uid: activityIdSeed.value++,
    day: Number(act.day || day || 1),
    type: act.type || 'attraction',
    name: act.name || '',
    start_time: start,
    end_time: act.end_time || '',
    location: act.location || '',
    cost: act.cost ?? act.estimated_cost ?? null,
    notes: act.notes || ''
  }
}

function openCreateTemplate() {
  editingTemplate.value = null
  resetTemplateForm()
  addActivity(1)
  showTemplateDialog.value = true
}

function openEditTemplate(tpl) {
  const content = normalizeContent(tpl.content)
  editingTemplate.value = tpl
  preservedContent.value = { ...content }
  delete preservedContent.value.activities
  delete preservedContent.value.guest_count
  delete preservedContent.value.budget

  templateForm.name = tpl.name || ''
  templateForm.category = tpl.category || 'family'
  templateForm.duration_days = Number(tpl.duration_days || 1)
  templateForm.guest_count = Number(content.guest_count || 1)
  templateForm.budget = content.budget ?? null
  templateForm.activities = (Array.isArray(content.activities) ? content.activities : []).map((act, index) => toEditorActivity(act, index + 1))
  showTemplateDialog.value = true
}

function addActivity(day) {
  const targetDay = Number(day || 1)
  templateForm.activities.push(toEditorActivity({ day: Math.min(Math.max(targetDay, 1), Number(templateForm.duration_days || 1)) }, targetDay))
}

function copyActivity(act) {
  templateForm.activities.push(toEditorActivity({ ...act, name: `${act.name || '未命名活动'} 副本` }, act.day))
}

function removeActivity(uid) {
  templateForm.activities = templateForm.activities.filter(act => act.uid !== uid)
}

function buildTemplateContent() {
  const activities = templateForm.activities
    .map(act => ({
      day: Number(act.day || 1),
      type: act.type || 'attraction',
      name: (act.name || '').trim(),
      time: act.start_time || '09:00',
      start_time: act.start_time || '09:00',
      end_time: act.end_time || '',
      location: act.location || '',
      cost: act.cost === '' || act.cost === null || act.cost === undefined ? null : Number(act.cost),
      notes: act.notes || ''
    }))
    .sort((a, b) => a.day - b.day || String(a.start_time).localeCompare(String(b.start_time)))

  return {
    ...preservedContent.value,
    guest_count: Number(templateForm.guest_count || 1),
    budget: templateForm.budget === '' || templateForm.budget === null || templateForm.budget === undefined ? null : Number(templateForm.budget),
    activities
  }
}

function validateTemplateEditor() {
  if (!templateForm.activities.length) {
    ElMessage.error('请至少添加一项活动')
    return false
  }
  if (invalidActivities.value.length) {
    ElMessage.error('存在超出行程天数的活动，请先调整第几天')
    return false
  }
  const unnamed = templateForm.activities.find(act => !act.name?.trim())
  if (unnamed) {
    ElMessage.error('请补全活动名称')
    return false
  }
  return true
}

async function handleSaveTemplate() {
  const valid = await templateFormRef.value?.validate().catch(() => false)
  if (!valid || !validateTemplateEditor()) return

  savingTemplate.value = true
  try {
    const payload = {
      name: templateForm.name,
      category: templateForm.category,
      duration_days: Number(templateForm.duration_days || 1),
      content: buildTemplateContent()
    }
    let saved
    if (editingTemplate.value) {
      saved = await updateTemplate(editingTemplate.value.id, payload)
      ElMessage.success('模板已更新')
    } else {
      saved = await createTemplate(payload)
      ElMessage.success('模板已创建')
    }
    showTemplateDialog.value = false
    await loadTemplates()
    if (selectedTemplate.value?.id === saved?.id) {
      selectedTemplate.value = templates.value.find(t => t.id === saved.id) || saved
    }
  } finally {
    savingTemplate.value = false
  }
}

async function confirmDeleteTemplate(tpl) {
  if (!tpl) return
  try {
    await ElMessageBox.confirm(`确认删除模板「${tpl.name}」吗？`, '删除模板', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteTemplate(tpl.id)
    ElMessage.success('模板已删除')
    if (selectedTemplate.value?.id === tpl.id) {
      showDetail.value = false
      selectedTemplate.value = null
    }
    await loadTemplates()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e?.response?.data?.detail || '删除失败')
    }
  }
}

async function handleUseTemplate() {
  const valid = await useFormRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    const res = await createTripFromTemplate(selectedTemplate.value.id, useForm)
    showUse.value = false
    showDetail.value = false
    ElMessage.success('行程创建成功，正在跳转...')
    router.push(`/trips/${res.id}`)
  } catch (e) {
    const msg = e?.response?.data?.detail || '创建失败'
    ElMessage.error(msg)
  } finally {
    creating.value = false
  }
}

onMounted(loadTemplates)
</script>

<style scoped>
.templates-page { max-width: 1200px; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
}
.page-header-left { display: flex; align-items: baseline; gap: 12px; }
.page-header-right { display: flex; align-items: center; gap: 10px; }
.page-title { font-size: 22px; font-weight: 800; color: #1a1a2e; margin: 0; letter-spacing: 0; }
.page-subtitle { font-size: 13px; color: #a8abb2; font-weight: 500; }
.search-input { width: 220px; }

.filter-bar { margin-bottom: 24px; }
.filter-chips { display: flex; gap: 10px; flex-wrap: wrap; }
.filter-chip {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px; background: #fff;
  border: 1px solid rgba(0,0,0,0.06); border-radius: 14px;
  cursor: pointer; font-size: 14px; font-weight: 500; color: #606266;
  transition: all 0.25s ease; user-select: none;
}
.filter-chip:hover { border-color: rgba(139,92,246,0.2); background: #f5f3ff; color: #7c3aed; }
.filter-chip.active {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff; border-color: transparent;
  box-shadow: 0 4px 12px rgba(139,92,246,0.25);
}
.chip-icon { font-size: 16px; }
.chip-count { font-size: 12px; background: rgba(255,255,255,0.2); padding: 1px 8px; border-radius: 8px; font-weight: 600; }
.filter-chip:not(.active) .chip-count { background: #f0f2f5; color: #909399; }

.tpl-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.tpl-grid-item { display: flex; }
.tpl-card {
  background: #fff; border-radius: 20px; overflow: hidden;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  cursor: pointer; transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
  display: flex; flex-direction: column; width: 100%;
}
.tpl-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,0.07); }

.tpl-hero { padding: 24px 22px 20px; position: relative; overflow: hidden; }
.tpl-hero.family { background: linear-gradient(135deg, #ecfdf5, #d1fae5); }
.tpl-hero.business { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.tpl-hero.team_building { background: linear-gradient(135deg, #fffbeb, #fef3c7); }
.tpl-hero.adventure { background: linear-gradient(135deg, #fef2f2, #fee2e2); }
.tpl-hero-deco {
  position: absolute; top: -30px; right: -30px;
  width: 120px; height: 120px; border-radius: 50%; opacity: 0.12;
}
.tpl-hero.family .tpl-hero-deco { background: #10b981; }
.tpl-hero.business .tpl-hero-deco { background: #8b5cf6; }
.tpl-hero.team_building .tpl-hero-deco { background: #f59e0b; }
.tpl-hero.adventure .tpl-hero-deco { background: #ef4444; }
.tpl-hero-deco2 {
  position: absolute; bottom: -20px; left: -20px;
  width: 80px; height: 80px; border-radius: 50%; opacity: 0.08;
}
.tpl-hero.family .tpl-hero-deco2 { background: #059669; }
.tpl-hero.business .tpl-hero-deco2 { background: #6d28d9; }
.tpl-hero.team_building .tpl-hero-deco2 { background: #d97706; }
.tpl-hero.adventure .tpl-hero-deco2 { background: #dc2626; }
.tpl-hero-content { display: flex; align-items: center; gap: 14px; position: relative; }
.tpl-emoji { font-size: 36px; flex-shrink: 0; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.tpl-hero-text { min-width: 0; }
.tpl-name {
  font-size: 17px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px;
  letter-spacing: 0; line-height: 1.3;
  overflow: hidden; text-overflow: ellipsis;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}
.tpl-category-label { font-size: 12px; font-weight: 600; opacity: 0.6; }
.tpl-hero.family .tpl-category-label { color: #059669; }
.tpl-hero.business .tpl-category-label { color: #7c3aed; }
.tpl-hero.team_building .tpl-category-label { color: #d97706; }
.tpl-hero.adventure .tpl-category-label { color: #dc2626; }
.tpl-duration-badge {
  position: absolute; top: 14px; right: 14px;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(4px);
  padding: 4px 12px; border-radius: 10px;
  font-size: 12px; font-weight: 700; color: #1a1a2e;
}

.tpl-info { padding: 14px 20px 8px; }
.tpl-info-row { display: flex; gap: 16px; flex-wrap: wrap; }
.tpl-info-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; color: #909399; font-weight: 500;
}

.tpl-highlights { padding: 4px 20px 14px; display: flex; gap: 6px; flex-wrap: wrap; flex: 1; }
.highlight-tag {
  font-size: 11px; padding: 3px 10px; border-radius: 8px;
  background: #f5f3ff; color: #7c3aed; font-weight: 500;
  white-space: nowrap;
}
.highlight-tag.muted { color: #a8abb2; background: #f5f6fa; }

.tpl-footer {
  padding: 12px 20px; border-top: 1px solid #f5f6fa;
  display: flex; align-items: center; justify-content: space-between;
  margin-top: auto;
}
.tpl-footer-hint { font-size: 12px; color: #c0c4cc; font-weight: 500; }
.tpl-admin-actions { display: flex; align-items: center; gap: 6px; }
.tpl-action-btn {
  height: 28px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  color: #64748b;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
}
.tpl-action-btn:hover {
  border-color: #c7d2fe;
  color: #6366f1;
  background: #f8f7ff;
}
.tpl-action-btn.primary {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}
.tpl-action-btn.primary:hover {
  color: #fff;
  box-shadow: 0 5px 14px rgba(99, 102, 241, 0.22);
}
.tpl-action-btn.danger {
  width: 28px;
  padding: 0;
  border-color: #fee2e2;
  color: #dc2626;
  background: #fff7f7;
}
.tpl-action-btn.danger:hover {
  border-color: #fecaca;
  color: #b91c1c;
  background: #fee2e2;
}
.tpl-footer-arrow { color: #c0c4cc; transition: transform 0.25s; }
.tpl-card:hover .tpl-footer-arrow { transform: translateX(3px); color: #8b5cf6; }
.tpl-card:hover .tpl-footer-hint { color: #8b5cf6; }

.empty-wrap { text-align: center; padding: 80px 0; }
.empty-icon { font-size: 56px; margin-bottom: 16px; }
.empty-icon.small { font-size: 36px; margin-bottom: 8px; }
.empty-title { font-size: 17px; font-weight: 700; color: #1a1a2e; margin-bottom: 6px; }
.empty-desc { font-size: 14px; color: #909399; margin-bottom: 20px; }

.card-list-enter-active { transition: all 0.4s cubic-bezier(0.4,0,0.2,1); }
.card-list-leave-active { transition: all 0.3s ease; }
.card-list-enter-from { opacity: 0; transform: translateY(20px) scale(0.97); }
.card-list-leave-to { opacity: 0; transform: scale(0.95); }

.detail-header {
  padding: 32px 28px 24px; position: relative; overflow: hidden;
}
.detail-header.family { background: linear-gradient(135deg, #ecfdf5, #d1fae5); }
.detail-header.business { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.detail-header.team_building { background: linear-gradient(135deg, #fffbeb, #fef3c7); }
.detail-header.adventure { background: linear-gradient(135deg, #fef2f2, #fee2e2); }
.detail-header-deco {
  position: absolute; top: -40px; right: -40px;
  width: 160px; height: 160px; border-radius: 50%; opacity: 0.1;
  background: currentColor;
}
.detail-close {
  position: absolute; top: 16px; right: 16px;
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255,255,255,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #606266; transition: all 0.2s;
  z-index: 1;
}
.detail-close:hover { background: #fff; color: #1a1a2e; }
.detail-header-body { position: relative; }
.detail-emoji { font-size: 48px; display: block; margin-bottom: 12px; }
.detail-title { font-size: 22px; font-weight: 800; color: #1a1a2e; margin: 0 0 8px; letter-spacing: 0; }
.detail-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.detail-meta-item { font-size: 13px; color: #606266; font-weight: 500; }
.detail-meta-sep { color: #c0c4cc; font-size: 12px; }

.detail-timeline { padding: 20px 28px; flex: 1; overflow-y: auto; }
.timeline-day { margin-bottom: 8px; }
.timeline-day-header {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 12px;
  cursor: pointer; transition: background 0.2s;
  user-select: none;
}
.timeline-day-header:hover { background: #f8f9fc; }
.timeline-day-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(0,0,0,0.06);
}
.timeline-day-dot.family { background: #10b981; }
.timeline-day-dot.business { background: #8b5cf6; }
.timeline-day-dot.team_building { background: #f59e0b; }
.timeline-day-dot.adventure { background: #ef4444; }
.timeline-day-label { font-size: 15px; font-weight: 700; color: #1a1a2e; }
.timeline-day-count { font-size: 12px; color: #a8abb2; font-weight: 500; }
.timeline-day-cost {
  font-size: 12px; color: #d97706; font-weight: 600;
  background: #fffbeb; padding: 2px 8px; border-radius: 6px; margin-left: auto;
}
.timeline-day-arrow {
  color: #c0c4cc; transition: transform 0.3s; margin-left: auto;
}
.timeline-day-cost + .timeline-day-arrow { margin-left: 0; }
.timeline-day-arrow.expanded { transform: rotate(180deg); }

.timeline-day-acts { padding: 4px 0 8px 20px; }
.timeline-act {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 8px 0; min-height: 44px;
}
.timeline-act-time {
  font-size: 12px; font-weight: 600; color: #909399;
  width: 42px; flex-shrink: 0; padding-top: 2px; text-align: right;
}
.timeline-act-line {
  display: flex; flex-direction: column; align-items: center;
  flex-shrink: 0; width: 16px; padding-top: 5px;
}
.timeline-act-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.timeline-act-dot.transport { background: #f97316; }
.timeline-act-dot.attraction { background: #10b981; }
.timeline-act-dot.meal { background: #ef4444; }
.timeline-act-dot.hotel { background: #8b5cf6; }
.timeline-act-dot.free { background: #3b82f6; }
.timeline-act-connector {
  width: 2px; flex: 1; min-height: 20px;
  background: #eef0f4; margin-top: 4px;
}
.timeline-act-body { flex: 1; min-width: 0; }
.timeline-act-name {
  font-size: 13px; font-weight: 600; color: #1a1a2e;
  display: flex; align-items: center; gap: 6px;
}
.act-type-emoji { font-size: 14px; }
.timeline-act-info {
  display: flex; gap: 12px; margin-top: 3px; flex-wrap: wrap;
}
.act-info-item { font-size: 11px; color: #a8abb2; }
.act-info-item.cost { color: #d97706; font-weight: 600; }

.slide-down-enter-active { transition: all 0.3s ease; overflow: hidden; }
.slide-down-leave-active { transition: all 0.25s ease; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; max-height: 0; }
.slide-down-enter-to, .slide-down-leave-from { opacity: 1; max-height: 800px; }

.detail-action-bar {
  padding: 16px 28px; border-top: 1px solid #f0f2f5;
  display: flex; gap: 12px; flex-shrink: 0;
  background: #fff;
}
.detail-cancel-btn { flex: 0 0 auto; }
.detail-use-btn {
  flex: 1;
  background: linear-gradient(135deg, #8b5cf6, #6366f1); border: none;
  font-weight: 600;
}
.detail-use-btn:hover { box-shadow: 0 6px 20px rgba(139,92,246,0.3); }
.detail-edit-btn {
  flex: 1;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border: none;
  font-weight: 600;
}
.detail-edit-btn:hover { box-shadow: 0 6px 20px rgba(139,92,246,0.3); }

.template-editor-form { padding-right: 4px; }
.editor-section {
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 16px;
}
.editor-section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}
.editor-section-head h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #1a1a2e;
  letter-spacing: 0;
}
.editor-section-head p {
  margin: 0;
  color: #909399;
  font-size: 12px;
}
.editor-grid {
  display: grid;
  gap: 14px;
}
.editor-grid.two { grid-template-columns: repeat(2, 1fr); }
.editor-grid.three { grid-template-columns: 1.4fr 1fr 0.8fr; }
.activities-empty {
  text-align: center;
  padding: 34px 16px;
  border: 1px dashed #d9dce3;
  border-radius: 14px;
  background: #fafbff;
}
.activities-empty p { margin: 0 0 12px; color: #909399; font-size: 13px; }
.activity-days { display: flex; flex-direction: column; gap: 12px; }
.activity-day {
  border: 1px solid #eef0f4;
  border-radius: 14px;
  overflow: hidden;
}
.activity-day.invalid { border-color: #fca5a5; background: #fff7f7; }
.activity-day-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f8f9fc;
  font-weight: 700;
  color: #1a1a2e;
}
.activity-day.invalid .activity-day-head { background: #fee2e2; color: #b91c1c; }
.activity-day-head em {
  font-style: normal;
  color: #a8abb2;
  font-size: 12px;
  font-weight: 500;
  margin-right: auto;
}
.activity-list { padding: 12px; display: flex; flex-direction: column; gap: 12px; }
.activity-editor-row {
  position: relative;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  padding: 12px 52px 8px 12px;
  background: #fff;
}
.invalid-row { border-color: #fca5a5; }
.activity-main-fields,
.activity-sub-fields {
  display: grid;
  gap: 10px;
  align-items: start;
}
.activity-main-fields { grid-template-columns: 110px 1fr 110px 110px; }
.activity-sub-fields { grid-template-columns: 1fr 120px 1fr; margin-top: 2px; }
.activity-field { margin-bottom: 8px; }
.activity-row-actions {
  position: absolute;
  right: 10px;
  top: 28px;
  display: flex;
  flex-direction: column;
}
.activity-field.is-error :deep(.el-input__wrapper),
.activity-field.is-error :deep(.el-input-number__decrease),
.activity-field.is-error :deep(.el-input-number__increase) {
  box-shadow: 0 0 0 1px #f56c6c inset;
}
.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  width: 100%;
}
.editor-footer-meta {
  color: #909399;
  font-size: 13px;
}
.editor-footer-actions { display: flex; gap: 10px; }

@media (max-width: 1024px) { .tpl-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .page-header-right { width: 100%; flex-wrap: wrap; }
  .search-input { flex: 1; min-width: 180px; width: auto; }
  .filter-chips { gap: 8px; }
  .filter-chip { padding: 8px 14px; font-size: 13px; }
  .tpl-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; }
  .editor-grid.two,
  .editor-grid.three,
  .activity-main-fields,
  .activity-sub-fields {
    grid-template-columns: 1fr;
  }
  .activity-editor-row { padding-right: 12px; }
  .activity-row-actions {
    position: static;
    flex-direction: row;
    justify-content: flex-end;
  }
  .editor-footer { flex-direction: column; align-items: stretch; }
  .editor-footer-actions { justify-content: flex-end; }
}
@media (max-width: 640px) {
  .tpl-grid { grid-template-columns: 1fr; }
  .filter-chips { overflow-x: auto; flex-wrap: nowrap; padding-bottom: 4px; }
  .filter-chip { flex-shrink: 0; }
}
</style>

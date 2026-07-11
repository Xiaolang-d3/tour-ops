<template>
  <div class="users-page">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon total"><el-icon size="22"><User /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ users.length }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon admin"><el-icon size="22"><Star /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ adminCount }}</div>
          <div class="stat-label">管理员</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon planner"><el-icon size="22"><Coordinate /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ plannerCount }}</div>
          <div class="stat-label">计划员</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon recent"><el-icon size="22"><Clock /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ recentCount }}</div>
          <div class="stat-label">近7天新增</div>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="page-toolbar">
      <el-input v-model="searchText" placeholder="搜索用户名或昵称..." prefix-icon="Search" clearable class="search-input" />
      <el-button type="primary" @click="showCreate = true" round>
        <el-icon><Plus /></el-icon> 创建用户
      </el-button>
    </div>

    <!-- 用户表格 -->
    <div class="table-wrap">
      <el-table v-loading="loading" :data="filteredUsers" stripe class="user-table">
        <el-table-column label="用户" min-width="220">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="38" class="user-cell-avatar" :style="getAvatarStyle(row.avatar)">
                <span v-if="getAvatarEmoji(row.avatar)">{{ getAvatarEmoji(row.avatar) }}</span>
                <span v-else>{{ (row.name || row.username).charAt(0) }}</span>
              </el-avatar>
              <div>
                <div class="user-cell-name">{{ row.name || '未设置昵称' }}</div>
                <div class="user-cell-username">@{{ row.username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="130" align="center">
          <template #default="{ row }">
            <div class="role-badge" :class="row.role">
              <el-icon size="12"><Star v-if="row.role === 'admin'" /><Coordinate v-else /></el-icon>
              {{ row.role === 'admin' ? '管理员' : '计划员' }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="160">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="right">
          <template #default="{ row }">
            <el-button text size="small" class="action-btn" @click="handleToggleRole(row)">
              <el-icon><Switch /></el-icon>
              {{ row.role === 'admin' ? '设为计划员' : '设为管理员' }}
            </el-button>
            <el-popconfirm
              title="确定删除该用户？关联数据将一并删除。"
              confirm-button-text="删除"
              confirm-button-type="danger"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建用户对话框 -->
    <el-dialog v-model="showCreate" title="创建用户" width="440px" destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="70px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.name" placeholder="选填" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="planner">计划员</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, createUser, updateUserRole, deleteUser } from '@/api/auth'

const users = ref([])
const loading = ref(true)
const showCreate = ref(false)
const creating = ref(false)
const searchText = ref('')
const formRef = ref(null)
const form = reactive({ username: '', password: '', name: '', role: 'planner' })

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)
const plannerCount = computed(() => users.value.filter(u => u.role === 'planner').length)
const recentCount = computed(() => {
  const week = Date.now() - 7 * 24 * 3600 * 1000
  return users.value.filter(u => u.created_at && new Date(u.created_at).getTime() > week).length
})

const avatarOptions = [
  { id: 'avatar-1', emoji: '😊', bg: 'linear-gradient(135deg, #8b5cf6, #6366f1)' },
  { id: 'avatar-2', emoji: '🚀', bg: 'linear-gradient(135deg, #3b82f6, #06b6d4)' },
  { id: 'avatar-3', emoji: '🌸', bg: 'linear-gradient(135deg, #ec4899, #f43f5e)' },
  { id: 'avatar-4', emoji: '🌿', bg: 'linear-gradient(135deg, #10b981, #059669)' },
  { id: 'avatar-5', emoji: '🔥', bg: 'linear-gradient(135deg, #f97316, #ef4444)' },
  { id: 'avatar-6', emoji: '⭐', bg: 'linear-gradient(135deg, #f59e0b, #eab308)' },
  { id: 'avatar-7', emoji: '🎵', bg: 'linear-gradient(135deg, #8b5cf6, #ec4899)' },
  { id: 'avatar-8', emoji: '🌊', bg: 'linear-gradient(135deg, #0ea5e9, #6366f1)' },
]
function getAvatarStyle(avatarId) {
  const av = avatarOptions.find(a => a.id === avatarId)
  return av ? { background: av.bg } : {}
}
function getAvatarEmoji(avatarId) {
  const av = avatarOptions.find(a => a.id === avatarId)
  return av ? av.emoji : null
}

function formatTime(dt) {
  if (!dt) return '-'
  const d = new Date(dt)
  const y = d.getFullYear(), m = d.getMonth() + 1, day = d.getDate()
  return `${y}-${String(m).padStart(2,'0')}-${String(day).padStart(2,'0')}`
}

const filteredUsers = computed(() => {
  if (!searchText.value) return users.value
  const kw = searchText.value.toLowerCase()
  return users.value.filter(u =>
    u.username.toLowerCase().includes(kw) || (u.name || '').toLowerCase().includes(kw)
  )
})

async function loadUsers() {
  loading.value = true
  try { users.value = await getUsers() }
  finally { loading.value = false }
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await createUser({ ...form })
    showCreate.value = false
    ElMessage.success('创建成功')
    loadUsers()
  } finally { creating.value = false }
}

async function handleToggleRole(user) {
  const newRole = user.role === 'admin' ? 'planner' : 'admin'
  await updateUserRole(user.id, { role: newRole })
  ElMessage.success('角色已更新')
  loadUsers()
}

async function handleDelete(user) {
  try {
    await deleteUser(user.id, true)
    ElMessage.success('已删除')
    loadUsers()
  } catch { /* handled */ }
}

onMounted(loadUsers)
</script>

<style scoped>
.users-page { max-width: 1100px; }

/* 统计卡片 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(0,0,0,0.04);
  transition: all 0.3s ease;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.stat-icon {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
}
.stat-icon.total { background: linear-gradient(135deg, #e6a23c, #f59e0b); }
.stat-icon.admin { background: linear-gradient(135deg, #ef4444, #f97316); }
.stat-icon.planner { background: linear-gradient(135deg, #10b981, #059669); }
.stat-icon.recent { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
.stat-value { font-size: 26px; font-weight: 800; color: #1a1a2e; line-height: 1.2; }
.stat-label { font-size: 13px; color: #909399; font-weight: 500; margin-top: 2px; }

/* 工具栏 */
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.search-input { width: 280px; }

/* 表格 */
.table-wrap {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.04);
}
.user-table :deep(.el-table__header th) {
  background: #fefce8 !important;
  color: #92400e;
  font-weight: 600;
  font-size: 13px;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-cell-avatar {
  background: linear-gradient(135deg, #e6a23c, #f59e0b);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}
.user-cell-name { font-weight: 600; font-size: 14px; color: #1a1a2e; }
.user-cell-username { font-size: 12px; color: #909399; }

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 14px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}
.role-badge.admin {
  background: #fef2f2;
  color: #dc2626;
}
.role-badge.planner {
  background: #ecfdf5;
  color: #059669;
}

.time-text { font-size: 13px; color: #909399; }

.action-btn { color: #d97706; }
.action-btn:hover { color: #b45309; }

@media (max-width: 1024px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 14px; }
  .stat-icon { width: 40px; height: 40px; border-radius: 10px; }
  .stat-value { font-size: 20px; }
  .page-toolbar { flex-direction: column; gap: 12px; align-items: stretch; }
  .search-input { width: 100% !important; }
  .table-wrap { overflow-x: auto; }
  .table-wrap :deep(.el-table) { min-width: 600px; }
}
@media (max-width: 480px) {
  .stat-cards { grid-template-columns: 1fr 1fr; gap: 8px; }
  .stat-card { padding: 12px; gap: 10px; }
  .stat-icon { width: 36px; height: 36px; }
  .stat-value { font-size: 18px; }
  .stat-label { font-size: 11px; }
}
</style>

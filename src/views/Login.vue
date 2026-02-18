<template>
  <div class="login-page">
    <!-- 动态背景 -->
    <div class="login-bg">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-glow glow-1"></div>
      <div class="bg-glow glow-2"></div>
      <div class="bg-glow glow-3"></div>
      <div class="bg-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="orb orb-4"></div>
      </div>
    </div>

    <div class="login-card">
      <!-- 顶部装饰光条 -->
      <div class="card-glow-bar"></div>

      <div class="login-brand">
        <div class="brand-icon">
          <span style="color:#fff;font-size:26px;font-weight:700;letter-spacing:-1px">T</span>
          <div class="brand-icon-ring"></div>
        </div>
        <div class="brand-text">
          <h2>TourOps</h2>
          <p class="subtitle">智能行程编排系统</p>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @keyup.enter="handleLogin">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password size="large" />
            </el-form-item>
            <el-button type="primary" :loading="loading" size="large" class="submit-btn" @click="handleLogin">
              <span>登 录</span>
              <el-icon class="btn-arrow"><Right /></el-icon>
            </el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm" :rules="regRules" ref="regFormRef" @keyup.enter="handleRegister">
            <el-form-item prop="username">
              <el-input v-model="regForm.username" placeholder="用户名" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.name" placeholder="昵称（选填）" prefix-icon="Postcard" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="regForm.password" type="password" placeholder="密码（至少6位）" prefix-icon="Lock" show-password size="large" />
            </el-form-item>
            <el-button type="primary" :loading="loading" size="large" class="submit-btn" @click="handleRegister">
              <span>注 册</span>
              <el-icon class="btn-arrow"><Right /></el-icon>
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <span>© 2026 TourOps · 旅行从这里开始</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const regFormRef = ref(null)
const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', password: '', name: '' })

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}
const regRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await login(loginForm)
    localStorage.setItem('token', res.access_token)
    await userStore.fetchUser()
    if (userStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } finally { loading.value = false }
}

async function handleRegister() {
  const valid = await regFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await register(regForm)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = regForm.username
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 30%, #ddd6fe 60%, #e0e7ff 100%);
}

/* ===== 动态背景 ===== */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 40%, rgba(139, 92, 246, 0.08) 0%, transparent 70%),
              radial-gradient(ellipse 60% 50% at 80% 20%, rgba(99, 102, 241, 0.06) 0%, transparent 60%),
              radial-gradient(ellipse 50% 40% at 20% 80%, rgba(167, 139, 250, 0.05) 0%, transparent 60%);
}
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(139, 92, 246, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.04) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 30%, transparent 80%);
}
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
}
.glow-1 {
  width: 500px; height: 500px;
  top: -15%; right: -5%;
  background: rgba(139, 92, 246, 0.12);
  animation: glow-drift 20s ease-in-out infinite;
}
.glow-2 {
  width: 400px; height: 400px;
  bottom: -10%; left: -5%;
  background: rgba(99, 102, 241, 0.1);
  animation: glow-drift 16s ease-in-out infinite reverse;
}
.glow-3 {
  width: 300px; height: 300px;
  top: 40%; left: 50%;
  background: rgba(167, 139, 250, 0.08);
  animation: glow-drift 12s ease-in-out infinite 3s;
}
@keyframes glow-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
}

.bg-orbs { position: absolute; inset: 0; }
.orb {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(139, 92, 246, 0.1);
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(2px);
}
.orb-1 { width: 120px; height: 120px; top: 15%; left: 10%; animation: orb-float 18s ease-in-out infinite; }
.orb-2 { width: 80px; height: 80px; top: 60%; right: 15%; animation: orb-float 14s ease-in-out infinite 2s; }
.orb-3 { width: 60px; height: 60px; bottom: 20%; left: 25%; animation: orb-float 12s ease-in-out infinite 4s; }
.orb-4 { width: 40px; height: 40px; top: 25%; right: 30%; animation: orb-float 10s ease-in-out infinite 1s; }
@keyframes orb-float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.5; }
  50% { transform: translateY(-25px) rotate(180deg); opacity: 0.8; }
}

/* ===== 登录卡片 ===== */
.login-card {
  width: 440px;
  padding: 0 40px 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(40px) saturate(1.4);
  -webkit-backdrop-filter: blur(40px) saturate(1.4);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 32px 64px rgba(139, 92, 246, 0.08),
    0 8px 24px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  position: relative;
  z-index: 1;
  animation: card-enter 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}
.card-glow-bar {
  height: 3px;
  background: linear-gradient(90deg, transparent, #8b5cf6, #6366f1, #8b5cf6, transparent);
  margin-bottom: 32px;
  opacity: 0.7;
}
@keyframes card-enter {
  from { opacity: 0; transform: translateY(30px) scale(0.96); filter: blur(10px); }
  to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}

/* ===== 品牌区 ===== */
.login-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}
.brand-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.25);
}
.brand-icon-ring {
  position: absolute;
  inset: -3px;
  border-radius: 18px;
  border: 1px solid rgba(139, 92, 246, 0.2);
  animation: ring-pulse 3s ease-in-out infinite;
}
@keyframes ring-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}
.brand-text h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.5px;
}
.subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 2px 0 0;
}

/* ===== Tabs ===== */
.login-tabs :deep(.el-tabs__nav-wrap) {
  display: flex;
  justify-content: center;
}
.login-tabs :deep(.el-tabs__nav-wrap::after) {
  background: #e8ecf1;
}
.login-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
  height: 2px;
  border-radius: 1px;
}
.login-tabs :deep(.el-tabs__item) {
  color: #94a3b8;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.3s;
}
.login-tabs :deep(.el-tabs__item:hover) {
  color: #64748b;
}
.login-tabs :deep(.el-tabs__item.is-active) {
  color: #7c3aed;
  font-weight: 600;
}

/* ===== 表单 ===== */
.login-tabs :deep(.el-input__wrapper) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s ease;
}
.login-tabs :deep(.el-input__wrapper:hover) {
  border-color: #cbd5e1;
  background: #fff;
}
.login-tabs :deep(.el-input__wrapper.is-focus) {
  border-color: #7c3aed;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}
.login-tabs :deep(.el-input__inner) {
  color: #1e293b;
}
.login-tabs :deep(.el-input__inner::placeholder) {
  color: #94a3b8;
}
.login-tabs :deep(.el-input__prefix .el-icon) {
  color: #94a3b8;
}
.login-tabs :deep(.el-form-item__error) {
  color: #ef4444;
}

/* ===== 提交按钮 ===== */
.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #7c3aed, #6366f1);
  border: none;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}
.submit-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #8b5cf6, #818cf8);
  opacity: 0;
  transition: opacity 0.3s;
}
.submit-btn:hover::before { opacity: 1; }
.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.25);
}
.submit-btn:active { transform: translateY(0); }
.submit-btn span,
.submit-btn .btn-arrow { position: relative; z-index: 1; }
.btn-arrow {
  transition: transform 0.3s;
}
.submit-btn:hover .btn-arrow {
  transform: translateX(4px);
}

/* ===== 底部 ===== */
.login-footer {
  text-align: center;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #e8ecf1;
}
.login-footer span {
  font-size: 12px;
  color: #94a3b8;
}

@media (max-width: 480px) {
  .login-card {
    width: calc(100vw - 32px);
    padding: 0 24px 24px;
    border-radius: 20px;
  }
  .card-glow-bar { margin-bottom: 24px; }
  .login-brand { margin-bottom: 20px; }
  .brand-icon { width: 44px; height: 44px; border-radius: 14px; }
  .brand-icon span { font-size: 22px !important; }
  .brand-text h2 { font-size: 22px; }
  .submit-btn { height: 44px; font-size: 14px; border-radius: 12px; }
  .login-footer { margin-top: 20px; padding-top: 16px; }
  .glow-1 { width: 300px; height: 300px; }
  .glow-2 { width: 250px; height: 250px; }
  .orb-1 { width: 80px; height: 80px; }
  .orb-2 { width: 50px; height: 50px; }
}
</style>

<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1 class="title">创建账号</h1>
        <p class="subtitle">加入学者评估系统</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名（3-50位）"
            required
            minlength="3"
            maxlength="50"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="fullName">全名</label>
          <input
            id="fullName"
            v-model="formData.full_name"
            type="text"
            placeholder="请输入您的姓名（选填）"
            maxlength="100"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            required
            minlength="6"
            maxlength="50"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
            :disabled="loading"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="register-button" :disabled="loading">
          <span v-if="!loading">注册</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <div class="register-footer">
        <p>已有账号？ <router-link to="/login" class="link">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const formData = reactive({
      username: '',
      email: '',
      full_name: '',
      password: '',
      confirmPassword: ''
    })

    const loading = ref(false)
    const error = ref('')

    const handleRegister = async () => {
      // 验证密码
      if (formData.password !== formData.confirmPassword) {
        error.value = '两次输入的密码不一致'
        return
      }

      loading.value = true
      error.value = ''

      const result = await authStore.register({
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name || undefined,
        password: formData.password
      })

      if (result.success) {
        // 注册成功后自动登录
        const loginResult = await authStore.login(formData.username, formData.password)
        if (loginResult.success) {
          router.push('/')
        } else {
          error.value = '注册成功，但登录失败：' + loginResult.error
        }
      } else {
        error.value = result.error
      }

      loading.value = false
    }

    return {
      formData,
      loading,
      error,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.register-container::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 200%;
  background: var(--accent-gradient);
  opacity: 0.08;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 20s ease-in-out infinite;
}

.register-container::after {
  content: '';
  position: absolute;
  bottom: -50%;
  left: -20%;
  width: 60%;
  height: 200%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  opacity: 0.05;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 25s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(-30px, 30px) rotate(5deg);
  }
}

.register-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  padding: 3rem;
  width: 100%;
  max-width: 440px;
  position: relative;
  z-index: 1;
  border: 1px solid var(--border-light);
}

.register-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 400;
}

.register-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  transition: var(--transition-base);
  background: var(--bg-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.1);
  background: var(--bg-secondary);
}

.form-group input:disabled {
  background: var(--bg-tertiary);
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: var(--error);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(239, 68, 68, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.register-button {
  width: 100%;
  padding: 0.875rem 1rem;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-base);
  box-shadow: var(--shadow-md);
  letter-spacing: 0.01em;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.register-button:active:not(:disabled) {
  transform: translateY(0);
}

.register-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
}

.loading-spinner {
  display: inline-block;
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.register-footer {
  text-align: center;
  padding-top: 1.75rem;
  border-top: 1px solid var(--border-light);
}

.register-footer p {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition-fast);
}

.link:hover {
  text-decoration: underline;
  color: var(--accent-light);
}
</style>

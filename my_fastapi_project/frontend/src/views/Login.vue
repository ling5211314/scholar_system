<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="title">欢迎回来</h1>
        <p class="subtitle">登录学者评估系统</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名 / 邮箱</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名或邮箱"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          <span v-if="!loading">登录</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <div class="login-footer">
        <p>还没有账号？ <router-link to="/register" class="link">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const formData = reactive({
      username: '',
      password: ''
    })

    const loading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      loading.value = true
      error.value = ''

      const result = await authStore.login(formData.username, formData.password)

      if (result.success) {
        router.push('/')
      } else {
        error.value = result.error
      }

      loading.value = false
    }

    return {
      formData,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.login-container::before {
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

.login-container::after {
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

.login-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  padding: 3rem;
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 1;
  border: 1px solid var(--border-light);
}

.login-header {
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

.login-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
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

.login-button {
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

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
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

.login-footer {
  text-align: center;
  padding-top: 1.75rem;
  border-top: 1px solid var(--border-light);
}

.login-footer p {
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

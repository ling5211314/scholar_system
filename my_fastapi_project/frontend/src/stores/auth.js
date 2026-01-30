import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // 设置认证信息
  function setAuth(authToken, userData) {
    token.value = authToken
    user.value = userData
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
    
    // 设置axios默认请求头
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
  }

  // 清除认证信息
  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  // 登录
  async function login(username, password) {
    try {
      const response = await axios.post(`${API_BASE}/users/login`, {
        username,
        password
      })
      setAuth(response.data.access_token, response.data.user)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '登录失败' 
      }
    }
  }

  // 注册
  async function register(userData) {
    try {
      const response = await axios.post(`${API_BASE}/users/register`, userData)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '注册失败' 
      }
    }
  }

  // 登出
  function logout() {
    clearAuth()
  }

  // 获取当前用户信息
  async function getCurrentUser() {
    if (!token.value) return null
    
    try {
      const response = await axios.get(`${API_BASE}/users/me`)
      user.value = response.data
      return response.data
    } catch (error) {
      clearAuth()
      return null
    }
  }

  // 初始化：从localStorage恢复用户信息
  function init() {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  // 初始化
  init()

  return {
    token,
    user,
    isAuthenticated,
    setAuth,
    clearAuth,
    login,
    register,
    logout,
    getCurrentUser,
    init
  }
})

<template>
  <div class="chat-layout">
    <!-- 头部 -->
    <header class="chat-header">
      <div class="header-content">
        <div class="header-left">
          <router-link to="/" class="nav-link active">问答</router-link>
          <router-link to="/navigator" class="nav-link">研究向导</router-link>
          <router-link to="/papers" class="nav-link">论文搜索</router-link>
        </div>
        <div class="header-right">
          <span class="user-info">{{ authStore.user?.username }}</span>
          <button @click="handleLogout" class="logout-button">退出</button>
        </div>
      </div>
    </header>

    <!-- 聊天区域 -->
    <main class="chat-main">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h2 class="welcome-title">欢迎使用智能问答系统</h2>
        <p class="welcome-text">请输入您的问题，系统将根据知识库为您提供答案</p>
        
        <!-- 示例问题 -->
        <div class="example-questions">
          <h3 class="example-title">您可以尝试以下问题：</h3>
          <div class="question-cards">
            <div 
              v-for="(example, idx) in exampleQuestions" 
              :key="idx"
              @click="selectExample(example)"
              class="question-card"
            >
              {{ example }}
            </div>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div ref="messagesContainer" class="messages-container">
        <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="message user-message">
            <div class="message-content user-content">
              <p>{{ message.content }}</p>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar">{{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}</div>
          </div>
          
          <!-- AI消息 -->
          <div v-else class="message ai-message">
            <div class="message-avatar ai-avatar">AI</div>
            <div class="message-content ai-content">
              <!-- 加载状态 -->
              <div v-if="message.loading" class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
              </div>
              
              <!-- 消息内容 -->
              <div v-else>
                <p>{{ message.content }}</p>
                
                <!-- 错误状态 -->
                <div v-if="message.error" class="error-message">
                  发生错误，请重试
                </div>
                
                <!-- 源文档 -->
                <div v-if="message.sources && message.sources.length > 0" class="sources-section">
                  <button 
                    @click="toggleSources(index)" 
                    class="sources-toggle"
                    :class="{ 'sources-open': message.showSources }"
                  >
                    知识来源 ({{ message.sources.length }})
                  </button>
                  
                  <div v-if="message.showSources" class="sources-list">
                    <div v-for="(source, idx) in message.sources" :key="idx" class="source-item">
                      {{ source }}
                    </div>
                  </div>
                </div>
                
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="chat-footer">
      <div class="input-container">
        <div class="input-wrapper">
          <textarea 
            ref="messageInput"
            v-model="inputMessage" 
            @keydown="handleKeyDown"
            @input="adjustTextareaHeight"
            placeholder="请输入您的问题..." 
            class="message-input"
            :disabled="isLoading"
            rows="1"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="!inputMessage.trim() || isLoading"
            class="send-button"
            :class="{ 'sending': isLoading }"
          >
            <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="animate-spin" width="20" height="20" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </button>
        </div>
        <div class="input-hint">按 Enter 发送，Shift + Enter 换行</div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Chat',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const inputMessage = ref('')
    const messages = ref([])
    const isLoading = ref(false)
    const exampleQuestions = [
      '什么是图神经网络？',
      '推荐一些深度学习的入门书籍',
      '机器学习和深度学习有什么区别？',
      '如何构建一个神经网络模型？'
    ]

    const messageInput = ref(null)
    const messagesContainer = ref(null)

    onMounted(() => {
      if (messageInput.value) {
        messageInput.value.focus()
      }
    })

    const selectExample = (question) => {
      inputMessage.value = question
      sendMessage()
    }

    const toggleSources = (index) => {
      messages.value[index].showSources = !messages.value[index].showSources
    }

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isLoading.value) return

      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''

      messages.value.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      })

      scrollToBottom()

      const loadingMessageIndex = messages.value.length
      messages.value.push({
        role: 'ai',
        content: '',
        loading: true,
        timestamp: new Date(),
        showSources: false
      })

      isLoading.value = true

      if (messageInput.value) {
        messageInput.value.style.height = 'auto'
      }

      try {
        const response = await axios.post('/api/rag/ask', {
          question: userMessage,
          use_hybrid: true,
          semantic_weight: 0.7,
          bm25_weight: 0.3
        })

        messages.value[loadingMessageIndex] = {
          role: 'ai',
          content: response.data.answer,
          sources: response.data.sources || [],
          timestamp: new Date(),
          showSources: false
        }
      } catch (error) {
        console.error('RAG请求错误:', error)
        messages.value[loadingMessageIndex] = {
          role: 'ai',
          content: '抱歉，处理您的请求时遇到了问题。请检查网络连接或稍后再试。',
          error: true,
          timestamp: new Date(),
          showSources: false
        }
      } finally {
        isLoading.value = false
        scrollToBottom()
      }
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    const adjustTextareaHeight = () => {
      const textarea = messageInput.value
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
      }
    }

    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }

    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      authStore,
      inputMessage,
      messages,
      isLoading,
      exampleQuestions,
      messageInput,
      messagesContainer,
      selectExample,
      toggleSources,
      sendMessage,
      handleKeyDown,
      adjustTextareaHeight,
      scrollToBottom,
      formatTime,
      handleLogout
    }
  }
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
}

/* 头部样式 */
.chat-header {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 1rem 1.5rem;
  box-shadow: var(--shadow-sm);
  z-index: 10;
  border-bottom: 1px solid var(--border-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.header-left {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  padding: 0.625rem 1.125rem;
  border-radius: var(--radius-lg);
  transition: var(--transition-base);
  font-size: 0.875rem;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: var(--accent-gradient);
  transition: var(--transition-base);
}

.nav-link:hover {
  color: var(--primary);
  background: var(--bg-tertiary);
}

.nav-link:hover::after {
  width: 60%;
}

.nav-link.active {
  color: var(--accent);
  background: var(--bg-tertiary);
}

.nav-link.active::after {
  width: 60%;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.logout-button {
  padding: 0.5rem 1rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: var(--transition-base);
}

.logout-button:hover {
  background: var(--error);
  color: white;
  border-color: var(--error);
}

/* 聊天区域样式 */
.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

/* 欢迎消息样式 */
.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  color: var(--text-secondary);
  padding: 2rem;
}

.welcome-icon {
  margin-bottom: 1.5rem;
  color: var(--accent);
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.1) 0%, rgba(34, 211, 238, 0.1) 100%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-icon svg {
  width: 40px;
  height: 40px;
}

.welcome-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--primary);
  letter-spacing: -0.02em;
}

.welcome-text {
  font-size: 1rem;
  margin-bottom: 2.5rem;
  color: var(--text-secondary);
  font-weight: 400;
}

.example-questions {
  width: 100%;
  max-width: 750px;
}

.example-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.question-card {
  background: var(--bg-secondary);
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: var(--transition-base);
  border: 1.5px solid var(--border-light);
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
  position: relative;
  overflow: hidden;
}

.question-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--accent-gradient);
  opacity: 0;
  transition: var(--transition-base);
}

.question-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
  border-color: var(--accent);
}

.question-card:hover::before {
  opacity: 1;
}

/* 消息列表样式 */
.messages-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-wrapper {
  width: 100%;
  animation: fadeInUp 0.3s ease-out;
}

.message {
  display: flex;
  align-items: flex-end;
  margin-bottom: 0.5rem;
}

.user-message {
  flex-direction: row-reverse;
}

.ai-message {
  flex-direction: row;
}

.message-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
  margin: 0 0.75rem;
  flex-shrink: 0;
}

.user-avatar {
  background: var(--accent-gradient);
  color: white;
  box-shadow: var(--shadow-md);
}

.ai-avatar {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  border: 1.5px solid var(--border);
}

.message-content {
  max-width: 70%;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-xl);
  word-wrap: break-word;
  box-shadow: var(--shadow-sm);
}

.user-content {
  background: var(--accent-gradient);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.ai-content {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 0.25rem;
  border: 1px solid var(--border-light);
}

.message-content p {
  margin: 0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.message-time {
  font-size: 0.75rem;
  margin-top: 0.75rem;
  opacity: 0.6;
  text-align: right;
  font-weight: 400;
}

/* 加载指示器样式 */
.typing-indicator {
  display: flex;
  align-items: center;
  padding: 0.75rem 0;
  gap: 0.25rem;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  margin-right: 4px;
  animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

/* 错误消息样式 */
.error-message {
  color: var(--error);
  font-size: 0.85rem;
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(239, 68, 68, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 源文档样式 */
.sources-section {
  margin-top: 1rem;
}

.sources-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.375rem 0.75rem;
  transition: var(--transition-base);
  border-radius: var(--radius-md);
}

.sources-toggle:hover {
  color: var(--accent);
  background: var(--bg-tertiary);
}

.sources-open {
  color: var(--accent);
  background: rgba(8, 145, 178, 0.08);
}

.sources-list {
  margin-top: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 1rem;
  border: 1px solid var(--border-light);
}

.source-item {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  line-height: 1.5;
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  font-family: 'JetBrains Mono', monospace;
}

.source-item:last-child {
  margin-bottom: 0;
}

/* 输入区域样式 */
.chat-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-light);
  padding: 1.25rem 1.5rem;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
}

.input-container {
  max-width: 1000px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 0.875rem;
}

.message-input {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 0.875rem 1.25rem;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  transition: var(--transition-base);
  min-height: 2.75rem;
  line-height: 1.5;
  background: var(--bg-primary);
  font-family: inherit;
}

.message-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.1);
  background: var(--bg-secondary);
}

.message-input:disabled {
  background: var(--bg-tertiary);
  cursor: not-allowed;
  opacity: 0.6;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  border: none;
  cursor: pointer;
  transition: var(--transition-base);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
}

.send-button:active:not(:disabled) {
  transform: scale(0.98);
}

.send-button:disabled {
  background: var(--text-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.sending {
  background: var(--accent-gradient);
}

.input-hint {
  display: flex;
  justify-content: center;
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-left {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .question-cards {
    grid-template-columns: 1fr;
  }
  
  .chat-header {
    padding: 0.75rem 1rem;
  }
  
  .chat-main {
    padding: 1rem;
  }
  
  .welcome-message {
    padding: 1rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .message-input {
    font-size: 0.875rem;
  }
}
</style>

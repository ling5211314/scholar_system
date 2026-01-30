<template>
  <div class="navigator-container">
    <!-- 头部导航 -->
    <header class="chat-header">
      <div class="header-content">
        <div class="header-left">
          <router-link to="/" class="nav-link">问答</router-link>
          <router-link to="/navigator" class="nav-link active">研究向导</router-link>
          <router-link to="/papers" class="nav-link">论文搜索</router-link>
        </div>
        <div class="header-right">
          <router-link to="/login" class="nav-link">返回登录</router-link>
        </div>
      </div>
    </header>

    <!-- 头部输入区 -->
    <div class="header-section">
      <h1>研究向导</h1>
      <p class="subtitle">输入研究领域，获取个性化学习路径推荐</p>
      
      <div class="search-box">
        <input
          v-model="topic"
          type="text"
          placeholder="请输入研究方向，如：大模型、计算机视觉、多模态学习..."
          @keyup.enter="generatePath"
          :disabled="loading"
        />
        <button 
          @click="generatePath" 
          :disabled="loading || !topic.trim()"
          class="generate-btn"
        >
          <span v-if="loading">生成中...</span>
          <span v-else>生成路径</span>
        </button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 结果展示区 -->
    <div v-if="result" class="result-section">
      <!-- 研究主题 -->
      <div class="topic-banner">
        <h2>{{ result.topic }} - 学习路径</h2>
      </div>

      <!-- 三阶段论文推荐 -->
      <div class="path-stages">
        <!-- 入门必读 -->
        <div class="stage-card foundation">
          <div class="stage-header">
            <span class="stage-icon">📚</span>
            <h3>入门必读</h3>
            <span class="stage-desc">经典奠基性论文</span>
          </div>
          <div class="paper-list">
            <div v-for="(paper, idx) in result.path.foundation" :key="idx" class="paper-item">
              <div class="paper-title">{{ paper.title }}</div>
              <div class="paper-meta">
                <span class="paper-authors">{{ paper.authors.join(', ') }}</span>
                <span class="paper-year">{{ paper.year }}</span>
                <span class="paper-venue">{{ paper.venue }}</span>
              </div>
              <div class="paper-stats">
                <span class="citations">引用: {{ paper.cited_by_count }}</span>
                <a :href="paper.url" target="_blank" class="paper-link">查看论文</a>
              </div>
            </div>
            <div v-if="!result.path.foundation || result.path.foundation.length === 0" class="empty-state">
              暂无推荐论文
            </div>
          </div>
        </div>

        <!-- 进阶核心 -->
        <div class="stage-card core">
          <div class="stage-header">
            <span class="stage-icon">🔬</span>
            <h3>进阶核心</h3>
            <span class="stage-desc">近3年高质量顶会论文</span>
          </div>
          <div class="paper-list">
            <div v-for="(paper, idx) in result.path.core" :key="idx" class="paper-item">
              <div class="paper-title">{{ paper.title }}</div>
              <div class="paper-meta">
                <span class="paper-authors">{{ paper.authors.join(', ') }}</span>
                <span class="paper-year">{{ paper.year }}</span>
                <span class="paper-venue">{{ paper.venue }}</span>
              </div>
              <div class="paper-stats">
                <span class="citations">引用: {{ paper.cited_by_count }}</span>
                <a :href="paper.url" target="_blank" class="paper-link">查看论文</a>
              </div>
            </div>
            <div v-if="!result.path.core || result.path.core.length === 0" class="empty-state">
              暂无推荐论文
            </div>
          </div>
        </div>

        <!-- 前沿探索 -->
        <div class="stage-card frontier">
          <div class="stage-header">
            <span class="stage-icon">🚀</span>
            <h3>前沿探索</h3>
            <span class="stage-desc">最近最新预印本</span>
          </div>
          <div class="paper-list">
            <div v-for="(paper, idx) in result.path.frontier" :key="idx" class="paper-item">
              <div class="paper-title">{{ paper.title }}</div>
              <div class="paper-meta">
                <span class="paper-authors">{{ paper.authors.join(', ') }}</span>
                <span class="paper-year">{{ paper.year }}</span>
                <span class="paper-venue">{{ paper.venue }}</span>
              </div>
              <div class="paper-stats">
                <span class="citations">引用: {{ paper.cited_by_count }}</span>
                <a :href="paper.url" target="_blank" class="paper-link">查看论文</a>
              </div>
            </div>
            <div v-if="!result.path.frontier || result.path.frontier.length === 0" class="empty-state">
              暂无推荐论文
            </div>
          </div>
        </div>
      </div>

      <!-- 核心学者推荐 -->
      <div class="scholars-section">
        <h3>👥 核心学者推荐</h3>
        <div class="scholars-grid">
          <div v-for="(scholar, idx) in result.scholars" :key="idx" class="scholar-card">
            <div class="scholar-avatar">
              {{ scholar.name.charAt(0) }}
            </div>
            <div class="scholar-info">
              <div class="scholar-name">{{ scholar.name }}</div>
              <div class="scholar-institution">{{ scholar.institution }}</div>
              <div class="scholar-areas">
                <span v-for="area in scholar.research_areas" :key="area" class="area-tag">
                  {{ area }}
                </span>
              </div>
              <a :href="scholar.profile_url" target="_blank" class="scholar-link">查看主页</a>
            </div>
          </div>
          <div v-if="!result.scholars || result.scholars.length === 0" class="empty-state">
            暂无推荐学者
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const topic = ref('');
const result = ref(null);
const loading = ref(false);
const error = ref('');

const generatePath = async () => {
  if (!topic.value.trim()) {
    error.value = '请输入研究方向';
    return;
  }

  loading.value = true;
  error.value = '';
  result.value = null;

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/navigator/generate', {
      topic: topic.value,
      language: 'zh'
    });

    result.value = response.data;
  } catch (err) {
    console.error('生成失败:', err);
    error.value = err.response?.data?.detail || '生成失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.navigator-container {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

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
  max-width: 1200px;
  margin: 0 auto;
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

.header-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2.5rem 1.5rem 1.5rem;
}

.header-section h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  color: var(--primary);
  margin-bottom: 0.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  font-weight: 400;
}

.search-box {
  display: flex;
  justify-content: center;
  gap: 1rem;
  max-width: 700px;
  margin: 0 auto;
  background: var(--bg-secondary);
  padding: 0.5rem;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
}

.search-box input {
  flex: 1;
  padding: 1rem 1.25rem;
  font-size: 1rem;
  border: none;
  outline: none;
  background: transparent;
  font-weight: 400;
}

.search-box input:focus {
  outline: none;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.search-box input:disabled {
  background: transparent;
  opacity: 0.6;
  cursor: not-allowed;
}

.generate-btn {
  padding: 0.875rem 2rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition-base);
  box-shadow: var(--shadow-sm);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(0);
}

.generate-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
  box-shadow: none;
}

.error-message {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: var(--error);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: 2rem;
  border: 1px solid rgba(239, 68, 68, 0.2);
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.topic-banner {
  background: var(--accent-gradient);
  color: white;
  padding: 2rem 2.5rem;
  border-radius: var(--radius-xl);
  margin-bottom: 2.5rem;
  box-shadow: var(--shadow-md);
}

.topic-banner h2 {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.path-stages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stage-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 1.75rem;
  box-shadow: var(--shadow-sm);
  border: 1.5px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.stage-card.foundation::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0891b2 0%, #22d3ee 100%);
}

.stage-card.core::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.stage-card.frontier::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.stage-icon {
  font-size: 1.5rem;
}

.stage-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--primary);
  font-weight: 600;
}

.stage-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-left: auto;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.paper-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.paper-item {
  padding: 1rem 1.25rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  transition: var(--transition-base);
  border: 1.5px solid transparent;
}

.paper-item:hover {
  transform: translateX(5px);
  border-color: var(--accent);
  background: var(--bg-secondary);
  box-shadow: var(--shadow-sm);
}

.paper-title {
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 0.75rem;
  line-height: 1.5;
  font-size: 0.95rem;
}

.paper-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.875rem;
}

.paper-venue {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.1) 0%, rgba(34, 211, 238, 0.08) 100%);
  color: var(--accent);
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.paper-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.citations {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

.paper-link {
  color: var(--accent);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition-fast);
}

.paper-link:hover {
  text-decoration: underline;
  color: var(--accent-light);
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.scholars-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1.5px solid var(--border-light);
}

.scholars-section h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.375rem;
  color: var(--primary);
  font-weight: 600;
}

.scholars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.scholar-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  transition: var(--transition-base);
  border: 1.5px solid transparent;
}

.scholar-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent);
  background: var(--bg-secondary);
}

.scholar-avatar {
  width: 50px;
  height: 50px;
  background: var(--accent-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  font-weight: bold;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.scholar-info {
  flex: 1;
}

.scholar-name {
  font-weight: 600;
  font-size: 1rem;
  color: var(--primary);
  margin-bottom: 0.375rem;
}

.scholar-institution {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.875rem;
}

.scholar-areas {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-bottom: 0.75rem;
}

.area-tag {
  font-size: 0.7rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.08) 100%);
  color: #6366f1;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.scholar-link {
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.scholar-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .header-section h1 {
    font-size: 2rem;
  }
  
  .search-box {
    flex-direction: column;
    padding: 0.75rem;
  }
  
  .generate-btn {
    width: 100%;
  }
  
  .path-stages {
    grid-template-columns: 1fr;
  }
  
  .scholars-grid {
    grid-template-columns: 1fr;
  }
  
  .stage-card {
    padding: 1.25rem;
  }
}
</style>

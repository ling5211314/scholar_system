<template>
  <div class="papers-search-container">
    <!-- 头部导航 -->
    <header class="chat-header">
      <div class="header-content">
        <div class="header-left">
          <router-link to="/" class="nav-link">问答</router-link>
          <router-link to="/navigator" class="nav-link">研究向导</router-link>
          <router-link to="/papers" class="nav-link active">论文搜索</router-link>
        </div>
        <div class="header-right">
          <router-link to="/login" class="nav-link">返回登录</router-link>
        </div>
      </div>
    </header>

    <!-- 搜索栏 -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="输入查询，如：2023年发表的关于图像分割的论文"
          @keyup.enter="searchPapers"
        />
        <button @click="searchPapers" :disabled="loading" class="search-btn">
          <span v-if="loading">搜索中...</span>
          <span v-else>搜索</span>
        </button>
      </div>
      
      <!-- 显示生成的查询条件 -->
      <div v-if="generatedQuery" class="query-info">
        <span class="query-label">生成的查询条件：</span>
        <code class="query-code">{{ JSON.stringify(generatedQuery) }}</code>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 搜索结果 -->
    <div class="results-section">
      <div class="results-header">
        <h2>搜索结果</h2>
        <span v-if="results" class="results-count">共 {{ results.total }} 篇论文</span>
      </div>

      <div v-if="results && results.papers.length > 0" class="papers-list">
        <div v-for="(paper, index) in results.papers" :key="index" class="paper-card">
          <div class="paper-header">
            <span class="paper-type">{{ paper.文献类型 }}</span>
            <span class="paper-year">{{ paper.发表时间 }}</span>
          </div>
          <h3 class="paper-title">{{ paper.论文题目 }}</h3>
          <div class="paper-meta">
            <span class="paper-venue">{{ paper.期刊_会议名称 }}</span>
            <span class="paper-authors">{{ paper.作者 }}</span>
          </div>
          <div class="paper-keywords">
            <span v-for="keyword in parseKeywords(paper.关键词)" :key="keyword" class="keyword-tag">
              {{ keyword }}
            </span>
          </div>
          <div class="paper-abstract">
            <strong>摘要：</strong>{{ paper.摘要 }}
          </div>
        </div>
      </div>

      <div v-else-if="results && results.papers.length === 0" class="empty-state">
        <div class="empty-icon">📄</div>
        <h3>未找到匹配的论文</h3>
        <p>请尝试其他搜索关键词</p>
      </div>

      <div v-if="!results && !loading" class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>输入关键词开始搜索</h3>
        <p>支持自然语言查询，如："2023年CVPR论文"</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const searchQuery = ref('');
const results = ref(null);
const loading = ref(false);
const error = ref('');
const generatedQuery = ref(null);

// 如果从对话页面跳转过来，读取查询参数
if (route.query.q) {
  searchQuery.value = route.query.q;
  searchPapers();
}

const parseKeywords = (keywords) => {
  if (!keywords) return [];
  return keywords.split(',').map(k => k.trim()).filter(k => k);
};

const searchPapers = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '请输入搜索内容';
    return;
  }

  loading.value = true;
  error.value = '';
  results.value = null;
  generatedQuery.value = null;

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/papers/search', {
      message: searchQuery.value
    });

    results.value = response.data;
    generatedQuery.value = response.data.query;
  } catch (err) {
    console.error('搜索失败:', err);
    error.value = err.response?.data?.detail || '搜索失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.papers-search-container {
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

.search-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
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

.search-btn {
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

.search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.search-btn:active:not(:disabled) {
  transform: translateY(0);
}

.search-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
  box-shadow: none;
}

.query-info {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08) 0%, rgba(34, 211, 238, 0.05) 100%);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  color: var(--accent);
  font-size: 0.875rem;
  border: 1px solid rgba(8, 145, 178, 0.2);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.query-label {
  font-weight: 600;
  white-space: nowrap;
}

.query-code {
  background: var(--bg-secondary);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--primary);
  flex: 1;
  overflow-x: auto;
}

.error-message {
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: var(--error);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(239, 68, 68, 0.2);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem 3rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-header h2 {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem;
  color: var(--primary);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.results-count {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--bg-tertiary);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.paper-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 1.75rem;
  box-shadow: var(--shadow-sm);
  transition: var(--transition-base);
  border: 1.5px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.paper-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: var(--accent-gradient);
  opacity: 0;
  transition: var(--transition-base);
}

.paper-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  border-color: var(--accent);
}

.paper-card:hover::before {
  opacity: 1;
}

.paper-header {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.paper-type {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.1) 0%, rgba(34, 211, 238, 0.08) 100%);
  color: var(--accent);
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.paper-year {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
}

.paper-title {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  color: var(--primary);
  line-height: 1.5;
  font-weight: 600;
}

.paper-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.paper-venue {
  color: var(--accent);
  font-weight: 600;
}

.paper-authors {
  color: var(--text-muted);
}

.paper-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.keyword-tag {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.06) 100%);
  color: #6366f1;
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
  transition: var(--transition-fast);
}

.keyword-tag:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.12) 100%);
}

.paper-abstract {
  font-size: 0.875rem;
  color: var(--text-primary);
  line-height: 1.7;
  background: var(--bg-tertiary);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  border-left: 3px solid var(--accent);
}

.paper-abstract strong {
  color: var(--primary);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1.5rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }
  
  .search-btn {
    width: 100%;
  }
  
  .paper-card {
    padding: 1.25rem;
  }
  
  .paper-title {
    font-size: 1.1rem;
  }
  
  .query-info {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

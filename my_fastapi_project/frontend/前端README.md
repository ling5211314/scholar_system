# 学者评估系统 - 前端

基于 Vue 3 + Vite + Pinia 的前端项目。

## 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js
    ├── App.vue
    ├── style.css
    ├── router.js          # 路由配置
    ├── stores/
    │   └── auth.js        # 认证状态管理
    └── views/
        ├── Login.vue      # 登录页
        ├── Register.vue   # 注册页
        └── Chat.vue       # 聊天页
```

## 安装步骤

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

默认访问地址: http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 功能说明

### 认证功能
- 用户注册：支持用户名、邮箱、密码注册
- 用户登录：支持用户名或邮箱登录
- JWT Token 自动管理
- 登出功能

### 聊天功能
- 基于 RAG 技术的智能问答
- 实时对话界面
- 支持显示知识来源
- 消息历史记录

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP客户端**: Axios

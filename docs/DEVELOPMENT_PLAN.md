# Pixelle-Video 前后端分离改造开发计划

## 一、项目背景

当前 Pixelle-Video 采用 Streamlit 前后端一体化架构，存在以下问题：
- Streamlit 的 HTML 结构不可控，无法实现自定义顶部导航栏等 UI 需求
- CSS 注入受限，主题定制能力弱
- 前后端耦合在同一进程中，不利于扩展和部署
- 现有 FastAPI API 仅覆盖约 30% 功能，大量业务逻辑未暴露为 REST 接口

**目标**：使用 Vue 3 + TypeScript 重写前端，补全 FastAPI 后端接口，实现真正的前后端分离。

---

## 二、技术选型

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 组合式 API，类型安全，生态成熟 |
| 构建工具 | Vite | 快速 HMR，开箱即用 |
| UI 组件库 | Element Plus | 中文生态好，组件丰富 |
| 路由 | Vue Router 4 | 官方路由，支持懒加载 |
| 状态管理 | Pinia | 轻量，TypeScript 友好 |
| HTTP 客户端 | Axios | 拦截器、请求/响应转换 |
| CSS 框架 | Tailwind CSS + 自定义主题 | 原子化样式，便于定制 |
| 图表 | ECharts | 历史记录可视化 |
| 后端框架 | FastAPI（现有） | 已有 22 个端点，补全即可 |
| 实时推送 | Server-Sent Events (SSE) | 比 WebSocket 简单，适合进度推送 |
| 部署 | Docker Compose（现有） | 保持现有部署架构 |

---

## 三、现有 API 盘点（22 个端点）

### 3.1 已有的端点

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| 1 | GET | `/health` | 健康检查 | ✅ 完成 |
| 2 | GET | `/version` | 版本信息 | ✅ 完成 |
| 3 | GET | `/` | 服务信息 | ✅ 完成 |
| 4 | POST | `/api/llm/chat` | LLM 对话 | ✅ 完成 |
| 5 | POST | `/api/tts/synthesize` | TTS 合成 | ✅ 完成 |
| 6 | POST | `/api/image/generate` | 图片生成 | ✅ 完成 |
| 7 | POST | `/api/content/narration` | 旁白生成 | ✅ 完成 |
| 8 | POST | `/api/content/image-prompt` | 图片提示词生成 | ✅ 完成 |
| 9 | POST | `/api/content/title` | 标题生成 | ✅ 完成 |
| 10 | POST | `/api/video/generate/sync` | 同步视频生成 | ✅ 完成 |
| 11 | POST | `/api/video/generate/async` | 异步视频生成 | ✅ 完成 |
| 12 | GET | `/api/tasks` | 任务列表（内存） | ✅ 完成 |
| 13 | GET | `/api/tasks/{task_id}` | 任务详情（内存） | ✅ 完成 |
| 14 | DELETE | `/api/tasks/{task_id}` | 取消任务 | ✅ 完成 |
| 15 | GET | `/api/files/{file_path}` | 文件服务 | ✅ 完成 |
| 16 | GET | `/api/resources/workflows/tts` | TTS 工作流列表 | ✅ 完成 |
| 17 | GET | `/api/resources/workflows/media` | 媒体工作流列表 | ✅ 完成 |
| 18 | GET | `/api/resources/workflows/image` | 图片工作流列表（废弃） | ✅ 完成 |
| 19 | GET | `/api/resources/templates` | 帧模板列表 | ✅ 完成 |
| 20 | GET | `/api/resources/bgm` | BGM 列表 | ✅ 完成 |
| 21 | POST | `/api/frame/render` | 帧渲染 | ✅ 完成 |
| 22 | GET | `/api/frame/template/params` | 模板参数查询 | ✅ 完成 |

### 3.2 缺失的端点（需新增）

| 优先级 | 方法 | 路径 | 功能 | 说明 |
|--------|------|------|------|------|
| **P0** | POST | `/api/files/upload` | 文件上传 | 支持参考音频、角色图片、素材图片/视频等 |
| **P0** | GET | `/api/history/tasks` | 历史记录列表 | 分页、筛选、排序，基于 HistoryManager |
| **P0** | GET | `/api/history/tasks/{task_id}` | 历史详情 | 含 storyboard 完整数据 |
| **P0** | DELETE | `/api/history/tasks/{task_id}` | 删除历史 | 删除目录及索引 |
| **P1** | POST | `/api/history/tasks/{task_id}/duplicate` | 复制任务参数 | 用于"重新生成"功能 |
| **P1** | GET | `/api/history/statistics` | 统计信息 | 总数、完成率、总时长等 |
| **P1** | POST | `/api/config/llm` | 保存 LLM 配置 | api_key、base_url、model |
| **P1** | POST | `/api/config/comfyui` | 保存 ComfyUI 配置 | URL、API Key、RunningHub 等 |
| **P1** | GET | `/api/config` | 获取当前配置 | 脱敏返回（隐藏密钥） |
| **P1** | POST | `/api/llm/test-connection` | 测试 LLM 连接 | 验证 api_key 和 base_url |
| **P1** | GET | `/api/llm/models` | 列出可用模型 | 调用 LLM 提供商 API |
| **P1** | POST | `/api/comfyui/test-connection` | 测试 ComfyUI 连接 | 验证 URL 和可达性 |
| **P2** | POST | `/api/media/generate` | 统一媒体生成 | 合并 image/video，media_type 区分 |
| **P2** | POST | `/api/tts/preview` | TTS 试听 | 快速生成音频预览 |
| **P2** | GET | `/api/capabilities` | 服务能力发现 | 报告哪些服务已配置可用 |
| **P3** | GET | `/api/tasks/{task_id}/stream` | SSE 进度推送 | 实时推送 ProgressEvent |

---

## 四、前端页面规划

### 4.1 页面清单

| 页面 | 路由 | 功能 | 复杂度 |
|------|------|------|--------|
| 首页 | `/` | 视频生成主界面，包含 5 个流水线 Tab | 高 |
| 历史记录 | `/history` | 任务列表、筛选、详情、下载、删除 | 中 |
| 设置面板 | 首页侧抽屉 | LLM/ComfyUI 配置、连接测试 | 中 |

### 4.2 首页 - 5 个流水线 Tab

#### Tab 1: 快速创作（Quick Create）
| 区域 | 功能 |
|------|------|
| 左侧 | 批量/单条模式切换、处理模式（AI创作/固定内容）、文本输入框、标题输入、场景数滑块、分割方式选择、BGM 选择+试听、版本信息 |
| 中间 | TTS 配置（本地/ComfyUI 模式、声音选择、语速滑块、工作流选择、参考音频上传+试听）、模板画廊（类型选择、尺寸分组、预览网格、自定义参数）、媒体工作流选择、提示词前缀 |
| 右侧 | 生成按钮、进度条+状态文字、视频播放器、下载按钮、生成时长/文件大小/场景数展示 |

#### Tab 2: 素材创作（Custom Media）
| 区域 | 功能 |
|------|------|
| 左侧 | 多文件素材上传（图片+视频）、素材预览网格、视频标题、意图描述、BGM 选择 |
| 中间 | 时长滑块、工作流源选择（RunningHub/自托管）、TTS 声音选择、语速滑块 |
| 右侧 | 生成按钮（上传素材前禁用）、进度追踪、视频播放器、下载 |

#### Tab 3: 图生视频（Image to Video）
| 区域 | 功能 |
|------|------|
| 左侧 | 图片上传（单张/多张）、图片预览网格、文本提示词、工作流选择 |
| 右侧 | 生成按钮、进度追踪、视频播放器、下载 |

#### Tab 4: 动作迁移（Action Transfer）
| 区域 | 功能 |
|------|------|
| 左侧 | 视频上传（参考动作视频）、视频预览 |
| 中间 | 图片上传（角色图片）、图片预览网格、文本提示词、工作流选择 |
| 右侧 | 生成按钮、进度追踪、视频播放器、下载 |

#### Tab 5: 数字人（Digital Human）
| 区域 | 功能 |
|------|------|
| 左侧 | 角色图片上传、预览网格、TTS 配置 |
| 中间 | 工作流源选择、处理模式（数字人/自定义）、商品图片上传（数字人模式）、商品标题、商品文案、自定义文案（自定义模式） |
| 右侧 | 生成按钮、多步骤进度、视频播放器、下载 |

### 4.3 历史记录页

| 功能 | 说明 |
|------|------|
| 任务列表 | 卡片式展示，含缩略图、标题、日期、时长、文件大小 |
| 筛选 | 按状态（成功/失败/进行中）筛选 |
| 排序 | 按时间/时长/大小排序 |
| 分页 | 自定义每页条数 |
| 详情弹窗 | 完整 storyboard 查看、逐帧数据、视频播放 |
| 操作 | 重新生成（复制参数）、删除、下载 |
| 统计 | 总任务数、完成率、总时长汇总 |

### 4.4 设置面板（抽屉式）

| 区块 | 功能 |
|------|------|
| LLM 配置 | 预设选择器、API Key、Base URL、模型选择（加载/刷新）、连接测试按钮 |
| ComfyUI 配置 | 本地 URL + API Key、连接测试、RunningHub API Key、并发数滑块、实例类型选择（24G/48G） |
| 操作 | 保存配置、重置为默认 |

---

## 五、数据模型

### 5.1 核心 API Schema（前后端共用）

```python
# 视频生成请求
VideoGenerateRequest {
    text: str              # 脚本内容
    mode: "generate" | "fixed"  # 处理模式
    title: str             # 视频标题
    n_scenes: int          # 场景数
    tts_workflow: str      # TTS 工作流
    ref_audio: str | None  # 参考音频路径
    voice_id: str | None   # 声音 ID
    media_workflow: str    # 媒体工作流
    video_fps: int         # 帧率
    frame_template: str    # 帧模板
    prompt_prefix: str     # 提示词前缀
    bgm_path: str | None   # BGM 路径
    bgm_volume: float      # BGM 音量
    template_params: dict  # 模板自定义参数
}

# 任务（异步）
Task {
    task_id: str
    task_type: str
    status: "pending" | "running" | "completed" | "failed" | "cancelled"
    progress: TaskProgress
    result: dict | None
    error: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None
    request_params: dict
}

# 进度
TaskProgress {
    current: int
    total: int
    percentage: float
    message: str
}

# 历史记录（持久化）
HistoryTask {
    task_id: str
    created_at: str
    completed_at: str
    status: "completed" | "failed"
    title: str
    thumbnail: str
    duration: float
    file_size: int
    n_frames: int
    input: dict
    config: dict
    storyboard: Storyboard | None
}

# Storyboard
Storyboard {
    title: str
    config: StoryboardConfig
    frames: List[StoryboardFrame]
    content_metadata: dict
    final_video_path: str
    total_duration: float
}

# StoryboardFrame
StoryboardFrame {
    index: int
    narration: str
    image_prompt: str
    audio_path: str
    media_type: str
    image_path: str
    video_path: str
    duration: float
}
```

### 5.2 前端 TypeScript 接口

```typescript
// 配置
interface LLMConfig {
    api_key: string
    base_url: string
    model: string
}

interface ComfyUIConfig {
    comfyui_url: string
    comfyui_api_key: string
    runninghub_api_key: string
    runninghub_concurrent_limit: number
    runninghub_instance_type: '24G' | '48G'
}

// 流水线
interface PipelineTab {
    key: string
    icon: string
    label: string
    description: string
}

// 模板
interface TemplateInfo {
    name: string
    path: string
    type: 'static' | 'image' | 'video'
    size_group: string
    width: number
    height: number
    thumbnail_url: string
}

// BGM
interface BGMInfo {
    name: string
    path: string
    duration: number
    file_size: number
}
```

---

## 六、开发阶段与排期

### Phase 1: 后端 API 补全（预估 3-5 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 文件上传端点 `/api/files/upload` | 支持 multipart 上传，返回路径/URL |
| D2 | 历史记录 CRUD（4 个端点） | list/detail/delete/duplicate + statistics |
| D3 | 配置管理（4 个端点） | get/save LLM & ComfyUI 配置 |
| D4 | 连接测试（3 个端点） | LLM 测试、ComfyUI 测试、模型列表 |
| D5 | 统一媒体生成 + 能力发现 | `/api/media/generate` + `/api/capabilities` |

**关键文件**：
- `api/routers/config.py`（新建）- 配置管理
- `api/routers/history.py`（新建）- 历史记录 CRUD
- `api/routers/upload.py`（新建）- 文件上传
- `api/routers/test.py`（新建）- 连接测试
- `api/schemas/config.py`（新建）- 配置 Schema
- `api/schemas/history.py`（新建）- 历史 Schema
- `api/schemas/upload.py`（新建）- 上传 Schema

### Phase 2: SSE 进度推送（预估 1-2 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | ProgressEvent 序列化 + TaskManager 集成 | 异步任务能捕获进度 |
| D2 | SSE 端点 `/api/tasks/{task_id}/stream` | 前端可订阅实时进度 |

**关键文件**：
- `api/routers/stream.py`（新建）- SSE 端点
- `api/tasks/manager.py`（修改）- 集成 ProgressEvent

### Phase 3: 前端项目搭建（预估 2-3 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 项目初始化（Vite + Vue 3 + TS） | 项目骨架、路由、状态管理 |
| D2 | 全局布局 + 顶部导航栏 | Header、Nav、Footer 组件 |
| D3 | Axios 封装 + API 层 | 请求/响应拦截、错误处理、TypeScript 类型 |

**目录结构**：
```
frontend/
├── src/
│   ├── api/           # API 调用层
│   │   ├── index.ts   # Axios 实例
│   │   ├── video.ts   # 视频生成 API
│   │   ├── history.ts # 历史记录 API
│   │   ├── config.ts  # 配置管理 API
│   │   ├── resource.ts# 资源查询 API
│   │   └── upload.ts  # 文件上传 API
│   ├── components/    # 通用组件
│   │   ├── AppHeader.vue
│   │   ├── NavBar.vue
│   │   ├── LanguageSelector.vue
│   │   ├── VideoPlayer.vue
│   │   ├── ProgressBar.vue
│   │   ├── FileUploader.vue
│   │   ├── TemplateGallery.vue
│   │   └── SettingsDrawer.vue
│   ├── views/         # 页面
│   │   ├── HomeView.vue
│   │   └── HistoryView.vue
│   ├── stores/        # Pinia 状态
│   │   ├── app.ts     # 全局状态（语言、主题）
│   │   ├── config.ts  # 配置状态
│   │   └── tasks.ts   # 任务状态
│   ├── types/         # TypeScript 类型
│   │   └── index.ts
│   ├── i18n/          # 国际化
│   │   ├── locales/zh-CN.ts
│   │   └── locales/en-US.ts
│   ├── styles/        # 全局样式
│   │   └── theme.css
│   ├── router/        # 路由
│   │   └── index.ts
│   └── App.vue
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

### Phase 4: 首页 - 流水线页面（预估 5-7 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | Tab 切换框架 + 快速创作（左侧输入区） | 文本输入、模式切换、BGM 选择 |
| D2 | 快速创作（中间配置区） | TTS 配置、模板画廊、工作流选择 |
| D3 | 快速创作（右侧预览区） | 生成按钮、进度条、视频播放器 |
| D4 | 素材创作流水线 | 文件上传、预览网格、参数配置 |
| D5 | 图生视频 + 动作迁移流水线 | 图片/视频上传、提示词、工作流 |
| D6 | 数字人流水线 | 角色上传、TTS、商品配置 |
| D7 | 联调 + 边界处理 | 表单验证、错误处理、loading 状态 |

### Phase 5: 历史记录页（预估 2-3 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 任务列表 + 筛选/排序/分页 | 卡片式列表、状态筛选 |
| D2 | 详情弹窗 + 操作 | Storyboard 查看、视频播放、下载、删除 |
| D3 | 统计面板 + 联调 | 数据汇总、边界 case 处理 |

### Phase 6: 设置面板 + i18n（预估 2 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 设置抽屉 + LLM/ComfyUI 配置表单 | 表单验证、连接测试 |
| D2 | 国际化完善 | 中英文全覆盖、语言切换 |

### Phase 7: 集成测试与上线（预估 2-3 天）

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 全链路联调 | 前后端对接、5 个流水线端到端测试 |
| D2 | 浏览器兼容性 + 响应式适配 | Chrome/Firefox/Safari、移动端适配 |
| D3 | Docker 集成 + 部署 | docker-compose.yml 更新、CI/CD |

---

## 七、总体排期

| 阶段 | 内容 | 预估天数 | 优先级 |
|------|------|----------|--------|
| Phase 1 | 后端 API 补全 | 3-5 天 | P0 |
| Phase 2 | SSE 进度推送 | 1-2 天 | P1 |
| Phase 3 | 前端项目搭建 | 2-3 天 | P0 |
| Phase 4 | 首页流水线 | 5-7 天 | P0 |
| Phase 5 | 历史记录页 | 2-3 天 | P1 |
| Phase 6 | 设置 + i18n | 2 天 | P2 |
| Phase 7 | 集成测试上线 | 2-3 天 | P0 |
| **合计** | | **17-25 天** | |

---

## 八、外部服务依赖

| 服务 | 用途 | 配置项 |
|------|------|--------|
| LLM（OpenAI 兼容） | 旁白/图片提示词/标题生成 | `api_key`, `base_url`, `model` |
| ComfyUI（自托管） | TTS、图片生成、视频生成 | `comfyui_url`, `comfyui_api_key` |
| RunningHub（云端） | 云端 ComfyUI 执行 | `runninghub_api_key`, `concurrent_limit`, `instance_type` |
| Edge TTS | 本地 TTS 合成 | `voice`, `speed` |
| Playwright | HTML 帧模板渲染 | 自动初始化 |
| MoviePy + ffmpeg | 视频拼接、BGM 混音 | 系统依赖 |

---

## 九、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| ProgressEvent 无法注入到异步 TaskManager | 进度推送降级为轮询 | 保留轮询方案作为 fallback |
| ComfyKit 库 API 不便于从 FastAPI 调用 | 需要封装适配层 | 复用 `pixelle_video/service.py` 中的 PixelleVideoCore |
| 大文件上传超时 | 用户体验差 | Nginx/uvicorn 配置 `client_max_body_size` + 分片上传 |
| 数字人/动作迁移依赖 RunningHub | 云端服务不可用 | 增加自托管 fallback 选项 |

---

## 十、交付标准

1. **功能完整**：现有 Streamlit 的所有功能 1:1 复刻
2. **API 覆盖**：所有新增 16 个端点均有 OpenAPI 文档
3. **类型安全**：前端 TypeScript 零 `any`，后端 Pydantic 全校验
4. **测试覆盖**：核心 API 有单元测试，前端有组件测试
5. **部署无缝**：docker-compose 一条命令启动，前端 build 产物由 FastAPI 静态文件服务或直接 Nginx 代理

---

## 十一、与当前 Streamlit 版本的关系

- **改造期间**：Streamlit 版本保持可用，不删除
- **改造完成后**：`docker-compose.yml` 中将 `web` 服务替换为前端 Nginx/Vite 服务
- **API 服务**：保持不变，仅新增端点
- **迁移策略**：先在 `frontend/` 目录独立开发，验证通过后替换

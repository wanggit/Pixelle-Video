// ==========================================
// Core API Types
// ==========================================

export interface VideoGenerateRequest {
  text: string
  mode: 'generate' | 'fixed'
  title: string
  n_scenes: number
  tts_workflow?: string
  ref_audio?: string
  voice_id?: string
  min_narration_words?: number
  max_narration_words?: number
  min_image_prompt_words?: number
  max_image_prompt_words?: number
  media_workflow: string
  video_fps: number
  frame_template?: string
  prompt_prefix?: string
  bgm_path?: string
  bgm_volume?: number
  template_params?: Record<string, unknown>
}

export interface VideoGenerateResponse {
  success: boolean
  message: string
  video_url?: string
  duration?: number
  file_size?: number
}

export interface VideoGenerateAsyncResponse {
  success: boolean
  message: string
  task_id: string
}

// ==========================================
// Task Types
// ==========================================

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface TaskProgress {
  current: number
  total: number
  percentage: number
  message: string
}

export interface Task {
  task_id: string
  task_type: string
  status: TaskStatus
  progress: TaskProgress | null
  result: Record<string, unknown> | null
  error: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  request_params: Record<string, unknown>
}

// ==========================================
// History Types
// ==========================================

export interface HistoryTaskSummary {
  task_id: string
  title: string
  created_at: string
  completed_at?: string
  status: string
  thumbnail?: string
  duration?: number
  file_size?: number
  n_frames?: number
}

export interface HistoryListResponse {
  tasks: HistoryTaskSummary[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HistoryTaskDetail {
  task_id: string
  title: string
  created_at: string
  completed_at?: string
  status: string
  duration?: number
  file_size?: number
  n_frames?: number
  video_url?: string
  input_params?: Record<string, unknown>
  storyboard?: Record<string, unknown>
}

export interface HistoryStatistics {
  total_tasks: number
  completed: number
  failed: number
  total_duration: number
  total_size: number
}

// ==========================================
// Config Types
// ==========================================

export interface LLMConfig {
  api_key: string
  base_url: string
  model: string
}

export interface ComfyUIConfig {
  comfyui_url: string
  comfyui_api_key: string
  runninghub_api_key: string
  runninghub_concurrent_limit: number
  runninghub_instance_type: string
}

export interface ConfigResponse {
  llm: LLMConfig
  comfyui: ComfyUIConfig
  template: { default_template: string }
}

export interface LLMTestResponse {
  success: boolean
  message: string
  models: string[]
}

export interface ComfyUITestResponse {
  success: boolean
  message: string
  system_stats: Record<string, unknown> | null
}

// ==========================================
// Resource Types
// ==========================================

export interface WorkflowInfo {
  name: string
  path: string
  description?: string
}

export interface TemplateInfo {
  name: string
  path: string
  type: 'static' | 'image' | 'video'
  size_group: string
  width: number
  height: number
  thumbnail_url?: string
}

export interface BGMInfo {
  name: string
  path: string
  duration: number
  file_size: number
}

export interface WorkflowListResponse {
  success: boolean
  message: string
  workflows: WorkflowInfo[]
}

export interface TemplateListResponse {
  success: boolean
  message: string
  templates: TemplateInfo[]
}

export interface BGMListResponse {
  success: boolean
  message: string
  bgm_files: BGMInfo[]
}

// ==========================================
// Upload Types
// ==========================================

export interface FileUploadResponse {
  success: boolean
  message: string
  file_path: string
  file_url: string
  file_type: string
  file_size: number
}

// ==========================================
// Capabilities Types
// ==========================================

export interface Capabilities {
  llm: {
    configured: boolean
    model: string
    base_url: string
  }
  comfyui: {
    local_url: string
    runninghub_enabled: boolean
    workflows: {
      tts: boolean
      image: boolean
      video: boolean
    }
  }
  edge_tts: {
    enabled: boolean
    default_voice: string
    default_speed: number
  }
  pipelines: {
    standard: boolean
    asset_based: boolean
    digital_human: boolean
    image_to_video: boolean
    action_transfer: boolean
  }
}

// ==========================================
// Progress Event Types
// ==========================================

export interface ProgressEvent {
  event_type: string
  progress: number
  frame_current?: number
  frame_total?: number
  step?: string
  action?: string
  extra_info?: string
}

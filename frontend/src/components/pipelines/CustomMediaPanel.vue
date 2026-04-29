<template>
  <div class="custom-media-panel">
    <el-form :model="form" label-width="120px" label-position="top">
      <el-row :gutter="24">
        <!-- Left: Assets Upload -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">素材上传</span></template>

            <el-form-item label="图片/视频素材">
              <el-upload
                :before-upload="(file: File) => handleFileUpload(file)"
                :show-file-list="false"
                multiple
                accept=".jpg,.jpeg,.png,.gif,.webp,.mp4,.mov,.avi,.mkv,.webm"
                drag
              >
                <div class="upload-area">
                  <el-icon :size="32"><UploadFilled /></el-icon>
                  <p>拖拽或点击上传</p>
                  <p class="upload-hint">支持 jpg/png/gif/webp/mp4/mov/avi/mkv/webm</p>
                </div>
              </el-upload>
            </el-form-item>

            <div v-if="uploadedFiles.length > 0" class="preview-grid">
              <div v-for="file in uploadedFiles" :key="file.path" class="preview-item">
                <img v-if="file.type.startsWith('image')" :src="file.preview" alt="" />
                <video v-else :src="file.preview" muted />
                <el-tag size="small" class="file-tag">{{ file.name }}</el-tag>
              </div>
            </div>

            <el-form-item label="视频标题（可选）">
              <el-input v-model="form.videoTitle" placeholder="自定义视频标题" />
            </el-form-item>

            <el-form-item label="创作意图">
              <el-input
                v-model="form.intent"
                type="textarea"
                :rows="4"
                placeholder="描述你的创作意图或期望效果..."
              />
            </el-form-item>
          </el-card>
        </el-col>

        <!-- Middle: Settings -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">参数设置</span></template>

            <el-form-item label="视频时长">
              <el-slider v-model="form.duration" :min="15" :max="120" :step="5" show-input />
              <span class="slider-label">秒</span>
            </el-form-item>

            <el-form-item label="推理源">
              <el-radio-group v-model="form.source">
                <el-radio value="runninghub">RunningHub</el-radio>
                <el-radio value="selfhost">Self-Host</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="TTS 语音">
              <el-select v-model="form.voiceId" filterable clearable style="width: 100%">
                <el-option
                  v-for="voice in edgeTtsVoices"
                  :key="voice"
                  :label="voice"
                  :value="voice"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="TTS 语速">
              <el-slider v-model="form.ttsSpeed" :min="0.5" :max="2" :step="0.1" show-input />
            </el-form-item>

            <!-- BGM -->
            <el-form-item label="背景音乐">
              <el-select v-model="form.bgmPath" filterable clearable style="width: 100%">
                <el-option
                  v-for="bgm in bgmList"
                  :key="bgm.path"
                  :label="bgm.name"
                  :value="bgm.path"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="BGM 音量">
              <el-slider v-model="form.bgmVolume" :min="0" :max="0.5" :step="0.05" show-input />
            </el-form-item>
          </el-card>
        </el-col>

        <!-- Right: Generate & Preview -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">生成与预览</span></template>

            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="generating"
              :disabled="uploadedFiles.length === 0"
              @click="handleGenerate"
            >
              {{ generating ? '生成中...' : '生成视频' }}
            </el-button>

            <div v-if="generating || progress > 0" class="progress-section">
              <el-progress :percentage="Math.round(progress)" :status="progress >= 100 ? 'success' : undefined" />
              <p class="status-text">{{ statusText }}</p>
            </div>

            <div v-if="currentError" class="error-section">
              <el-alert type="error" :title="currentError" :closable="false" show-icon />
            </div>

            <div v-if="resultVideoUrl" class="video-preview">
              <h4>生成结果</h4>
              <video :src="resultVideoUrl" controls class="video-player" />
              <el-button type="success" link @click="handleDownload">
                <el-icon><Download /></el-icon> 下载视频
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import { uploadApi } from '@/api/upload'
import { resourceApi } from '@/api/resource'
import type { BGMInfo, FileUploadResponse } from '@/types'

interface UploadedFile {
  name: string
  type: string
  path: string
  preview: string
}

const edgeTtsVoices = [
  'zh-CN-XiaoxiaoNeural',
  'zh-CN-YunxiNeural',
  'zh-CN-YunjianNeural',
  'zh-CN-XiaoyiNeural',
  'zh-CN-YunyangNeural',
]

const form = ref({
  videoTitle: '',
  intent: '',
  duration: 30,
  source: 'runninghub' as 'runninghub' | 'selfhost',
  voiceId: '',
  ttsSpeed: 1.0,
  bgmPath: '',
  bgmVolume: 0.2,
})

const uploadedFiles = ref<UploadedFile[]>([])
const bgmList = ref<BGMInfo[]>([])
const generating = ref(false)
const resultVideoUrl = ref('')
const progress = ref(0)
const statusText = ref('')
const currentError = ref<string | null>(null)

let eventSource: EventSource | null = null

onMounted(async () => {
  try {
    const bgm = await resourceApi.bgm()
    bgmList.value = bgm.bgm_files || []
  } catch {
    // ignore
  }
})

async function handleFileUpload(file: File) {
  try {
    const resp: FileUploadResponse = await uploadApi.upload(file, file.type.startsWith('image') ? 'image' : 'video')
    const preview = file.type.startsWith('image')
      ? URL.createObjectURL(file)
      : URL.createObjectURL(file)

    uploadedFiles.value.push({
      name: file.name,
      type: file.type,
      path: resp.file_path,
      preview,
    })
    ElMessage.success(`文件 ${file.name} 上传成功`)
  } catch {
    ElMessage.error(`文件 ${file.name} 上传失败`)
  }
  return false
}

function startSSE(taskId: string) {
  progress.value = 0
  statusText.value = '任务已提交...'
  currentError.value = null

  eventSource = new EventSource(`/api/tasks/${taskId}/stream`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.progress !== undefined) progress.value = data.progress

      const parts: string[] = []
      if (data.step) parts.push(data.step)
      if (data.action) parts.push(data.action)
      if (data.extra_info) parts.push(data.extra_info)
      statusText.value = parts.join(' - ') || statusText.value

      if (data.event_type === 'completed' || data.event_type === 'success') {
        progress.value = 100
        statusText.value = '完成！'
        eventSource?.close()
        eventSource = null
        generating.value = false
        fetchTaskResult(taskId)
      }

      if (data.event_type === 'error' || data.event_type === 'failed') {
        currentError.value = data.extra_info || '任务失败'
        eventSource?.close()
        eventSource = null
        generating.value = false
      }
    } catch {
      // ignore
    }
  }

  eventSource.onerror = () => {
    if (eventSource?.readyState === EventSource.CLOSED) return
    currentError.value = '连接中断'
    eventSource?.close()
    eventSource = null
    generating.value = false
  }
}

async function handleGenerate() {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请上传素材文件')
    return
  }

  generating.value = true
  resultVideoUrl.value = ''

  // For now, show a placeholder message since the backend needs a dedicated endpoint
  ElMessage.info('素材创作后端接口对接中，当前使用快速创作接口演示')

  try {
    const { videoApi } = await import('@/api/video')
    const resp = await videoApi.generateAsync({
      text: form.value.intent || '基于素材生成视频',
      mode: 'generate',
      n_scenes: 3,
      bgm_path: form.value.bgmPath || undefined,
      bgm_volume: form.value.bgmVolume,
      tts_inference_mode: 'local',
      tts_voice: form.value.voiceId || undefined,
      tts_speed: form.value.ttsSpeed,
      media_workflow: '',
    })

    if (!resp.success) {
      ElMessage.error(resp.message)
      generating.value = false
      return
    }

    startSSE(resp.task_id)
  } catch {
    ElMessage.error('提交任务失败')
    generating.value = false
  }
}

async function fetchTaskResult(taskId: string) {
  try {
    const { taskApi } = await import('@/api/task')
    const task = await taskApi.detail(taskId)
    if (task.result?.video_url) {
      resultVideoUrl.value = task.result.video_url as string
      ElMessage.success('视频生成完成！')
    }
  } catch {
    ElMessage.warning('任务完成但无法获取视频链接')
  }
}

function handleDownload() {
  if (resultVideoUrl.value) {
    const a = document.createElement('a')
    a.href = resultVideoUrl.value
    a.download = 'pixelle-video.mp4'
    a.click()
  }
}
</script>

<style scoped>
.custom-media-panel { padding: 8px 0; }

.form-card {
  border: 1px solid #BAE6FD;
  border-radius: 12px;
}

.form-card :deep(.el-card__header) {
  background: #F0F9FF;
  border-bottom: 1px solid #BAE6FD;
  padding: 12px 16px;
}

.card-title {
  font-weight: 600;
  color: #0C4A6E;
  font-size: 14px;
}

.upload-area {
  text-align: center;
  padding: 20px;
  color: #64748B;
}

.upload-area p { margin: 8px 0 4px; }
.upload-hint { font-size: 12px; color: #94A3B8; }

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #F0F9FF;
}

.preview-item img,
.preview-item video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-tag {
  position: absolute;
  bottom: 4px;
  left: 4px;
  font-size: 10px;
  max-width: calc(100% - 8px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slider-label { font-size: 12px; color: #64748B; margin-left: 8px; }

.progress-section { margin-top: 20px; }
.status-text { font-size: 12px; color: #64748B; margin-top: 8px; }
.error-section { margin-top: 16px; }

.video-preview { margin-top: 20px; }
.video-preview h4 { margin-bottom: 12px; color: #0C4A6E; }
.video-player { width: 100%; max-height: 400px; border-radius: 8px; background: #0F172A; }
</style>

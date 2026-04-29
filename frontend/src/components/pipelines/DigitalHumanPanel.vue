<template>
  <div class="digital-human-panel">
    <el-row :gutter="24">
      <!-- Left: Character & Goods -->
      <el-col :span="8">
        <el-card shadow="hover" class="form-card">
          <template #header><span class="card-title">角色与商品</span></template>

          <el-form-item label="角色图片" label-position="top">
            <el-upload
              :before-upload="(file: File) => handleCharacterUpload(file)"
              :show-file-list="false"
              multiple
              accept=".jpg,.jpeg,.png,.webp"
              drag
            >
              <div class="upload-area">
                <el-icon :size="32"><UploadFilled /></el-icon>
                <p>上传角色图片</p>
                <p class="upload-hint">至少 1 张，支持 jpg/png/webp</p>
              </div>
            </el-upload>
          </el-form-item>

          <div v-if="characterImages.length > 0" class="preview-grid">
            <div v-for="(img, idx) in characterImages" :key="idx" class="preview-item">
              <img :src="img.preview" alt="" />
              <span v-if="idx === 0" class="badge-primary">使用中</span>
            </div>
          </div>

          <template v-if="form.mode === 'digital'">
            <el-form-item label="商品图片（可选）" label-position="top">
              <el-upload
                :before-upload="(file: File) => handleGoodsUpload(file)"
                :show-file-list="false"
                multiple
                accept=".jpg,.jpeg,.png,.webp"
                drag
              >
                <div class="upload-area">
                  <el-icon :size="24"><UploadFilled /></el-icon>
                  <p>上传商品图片</p>
                </div>
              </el-upload>
            </el-form-item>

            <div v-if="goodsImages.length > 0" class="preview-grid">
              <div v-for="(img, idx) in goodsImages" :key="idx" class="preview-item">
                <img :src="img.preview" alt="" />
              </div>
            </div>
          </template>
        </el-card>
      </el-col>

      <!-- Middle: TTS & Workflow -->
      <el-col :span="8">
        <el-card shadow="hover" class="form-card">
          <template #header><span class="card-title">TTS 与工作流</span></template>

          <!-- Processing Mode -->
          <el-form-item label="处理模式" label-position="top">
            <el-radio-group v-model="form.mode">
              <el-radio value="digital">数字人模式</el-radio>
              <el-radio value="customize">自定义模式</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- TTS -->
          <el-form-item label="TTS 推理模式" label-position="top">
            <el-radio-group v-model="form.ttsMode">
              <el-radio value="local">本地 (Edge TTS)</el-radio>
              <el-radio value="comfyui">ComfyUI</el-radio>
            </el-radio-group>
          </el-form-item>

          <template v-if="form.ttsMode === 'local'">
            <el-form-item label="语音" label-position="top">
              <el-select v-model="form.ttsVoice" filterable style="width: 100%">
                <el-option
                  v-for="voice in edgeTtsVoices"
                  :key="voice"
                  :label="voice"
                  :value="voice"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="语速" label-position="top">
              <el-slider v-model="form.ttsSpeed" :min="0.5" :max="2" :step="0.1" show-input />
            </el-form-item>
          </template>

          <template v-else>
            <el-form-item label="参考音频" label-position="top">
              <el-upload
                :before-upload="(file: File) => handleRefAudioUpload(file)"
                :show-file-list="!!form.refAudio"
                :limit="1"
                accept=".mp3,.wav,.flac,.m4a,.aac,.ogg"
              >
                <el-button size="small">上传音频</el-button>
              </el-upload>
            </el-form-item>
          </template>

          <!-- Workflow Source -->
          <el-form-item label="工作流源" label-position="top">
            <el-radio-group v-model="form.workflowSource">
              <el-radio value="runninghub">RunningHub</el-radio>
              <el-radio value="selfhost">Self-Host</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="工作流类型" label-position="top">
            <el-select v-model="form.workflowType" style="width: 100%">
              <el-option label="数字人图片" value="digital_image" />
              <el-option label="数字人组合" value="digital_combination" />
              <el-option label="数字人定制" value="digital_customize" />
            </el-select>
          </el-form-item>

          <!-- Goods Text / Customize Text -->
          <template v-if="form.mode === 'digital'">
            <el-form-item label="商品标题" label-position="top">
              <el-input v-model="form.goodsTitle" placeholder="商品名称" />
            </el-form-item>
            <el-form-item label="商品介绍" label-position="top">
              <el-input
                v-model="form.goodsText"
                type="textarea"
                :rows="4"
                placeholder="商品描述文本..."
              />
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item label="自定义文本" label-position="top">
              <el-input
                v-model="form.goodsText"
                type="textarea"
                :rows="7"
                placeholder="输入数字人要说的内容..."
              />
            </el-form-item>
          </template>
        </el-card>
      </el-col>

      <!-- Right: Generate & Preview -->
      <el-col :span="8">
        <el-card shadow="hover" class="form-card">
          <template #header><span class="card-title">生成与预览</span></template>

          <el-alert
            v-if="characterImages.length === 0"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 16px"
          >
            请上传至少 1 张角色图片
          </el-alert>

          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="generating"
            :disabled="characterImages.length === 0 || !form.goodsText"
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

          <el-empty v-if="!generating && !resultVideoUrl && !currentError && characterImages.length === 0" description="上传角色图片后开始生成" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import { uploadApi } from '@/api/upload'
import type { FileUploadResponse } from '@/types'

interface UploadedImage {
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
  mode: 'digital' as 'digital' | 'customize',
  ttsMode: 'local' as 'local' | 'comfyui',
  ttsVoice: 'zh-CN-XiaoxiaoNeural',
  ttsSpeed: 1.0,
  refAudio: '',
  workflowSource: 'runninghub' as 'runninghub' | 'selfhost',
  workflowType: 'digital_image' as 'digital_image' | 'digital_combination' | 'digital_customize',
  goodsTitle: '',
  goodsText: '',
})

const characterImages = ref<UploadedImage[]>([])
const goodsImages = ref<UploadedImage[]>([])
const generating = ref(false)
const resultVideoUrl = ref('')
const progress = ref(0)
const statusText = ref('')
const currentError = ref<string | null>(null)

let eventSource: EventSource | null = null

async function handleCharacterUpload(file: File) {
  try {
    const resp: FileUploadResponse = await uploadApi.upload(file, 'image')
    characterImages.value.push({
      path: resp.file_path,
      preview: URL.createObjectURL(file),
    })
    ElMessage.success(`角色图片 ${file.name} 上传成功`)
  } catch {
    ElMessage.error(`角色图片 ${file.name} 上传失败`)
  }
  return false
}

async function handleGoodsUpload(file: File) {
  try {
    const resp: FileUploadResponse = await uploadApi.upload(file, 'image')
    goodsImages.value.push({
      path: resp.file_path,
      preview: URL.createObjectURL(file),
    })
    ElMessage.success(`商品图片 ${file.name} 上传成功`)
  } catch {
    ElMessage.error(`商品图片 ${file.name} 上传失败`)
  }
  return false
}

async function handleRefAudioUpload(file: File) {
  try {
    const resp: FileUploadResponse = await uploadApi.upload(file, 'audio')
    form.value.refAudio = resp.file_path
    ElMessage.success('参考音频上传成功')
  } catch {
    ElMessage.error('参考音频上传失败')
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
      if (data.step || data.action) {
        const parts: string[] = []
        if (data.step) parts.push(data.step)
        if (data.action) parts.push(data.action)
        statusText.value = parts.join(' - ')
      }

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
  if (characterImages.value.length === 0) {
    ElMessage.warning('请上传角色图片')
    return
  }
  if (!form.value.goodsText) {
    ElMessage.warning('请输入文本内容')
    return
  }

  generating.value = true
  resultVideoUrl.value = ''

  ElMessage.info('数字人后端接口对接中，当前使用快速创作接口演示')

  try {
    const { videoApi } = await import('@/api/video')
    const resp = await videoApi.generateAsync({
      text: form.value.goodsText,
      mode: 'generate',
      n_scenes: 3,
      media_workflow: '',
      tts_inference_mode: form.value.ttsMode,
      tts_voice: form.value.ttsMode === 'local' ? form.value.ttsVoice : undefined,
      tts_speed: form.value.ttsSpeed,
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
.digital-human-panel { padding: 8px 0; }

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

.upload-area { text-align: center; padding: 20px; color: #64748B; }
.upload-area p { margin: 8px 0 4px; }
.upload-hint { font-size: 12px; color: #94A3B8; }

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #F0F9FF;
}

.preview-item img { width: 100%; height: 100%; object-fit: cover; }

.badge-primary {
  position: absolute;
  top: 4px;
  left: 4px;
  background: #0EA5E9;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.progress-section { margin-top: 20px; }
.status-text { font-size: 12px; color: #64748B; margin-top: 8px; }
.error-section { margin-top: 16px; }

.video-preview { margin-top: 20px; }
.video-preview h4 { margin-bottom: 12px; color: #0C4A6E; }
.video-player { width: 100%; max-height: 400px; border-radius: 8px; background: #0F172A; }
</style>

<template>
  <div class="image-to-video-panel">
    <el-row :gutter="24">
      <!-- Left: Image Upload & Prompt -->
      <el-col :span="12">
        <el-card shadow="hover" class="form-card">
          <template #header><span class="card-title">图片上传</span></template>

          <el-upload
            :before-upload="(file: File) => handleImageUpload(file)"
            :show-file-list="false"
            multiple
            accept=".jpg,.jpeg,.png,.webp"
            drag
          >
            <div class="upload-area">
              <el-icon :size="32"><UploadFilled /></el-icon>
              <p>拖拽或点击上传图片</p>
              <p class="upload-hint">支持 jpg/jpeg/png/webp，多张图片取第一张</p>
            </div>
          </el-upload>

          <div v-if="uploadedImages.length > 0" class="preview-grid">
            <div v-for="(img, idx) in uploadedImages" :key="idx" class="preview-item">
              <img :src="img.preview" alt="" />
              <span v-if="idx === 0" class="badge-primary">使用中</span>
            </div>
          </div>

          <el-form :model="form" label-position="top" style="margin-top: 16px">
            <el-form-item label="提示词">
              <el-input
                v-model="form.prompt"
                type="textarea"
                :rows="6"
                placeholder="描述你期望的视频动态效果..."
              />
            </el-form-item>

            <el-form-item label="工作流">
              <el-select v-model="form.workflow" filterable style="width: 100%">
                <el-option
                  v-for="wf in workflows"
                  :key="wf.path"
                  :label="wf.name"
                  :value="wf.path"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="推理源">
              <el-radio-group v-model="form.source">
                <el-radio value="runninghub">RunningHub</el-radio>
                <el-radio value="selfhost">Self-Host</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right: Generate & Preview -->
      <el-col :span="12">
        <el-card shadow="hover" class="form-card">
          <template #header><span class="card-title">生成与预览</span></template>

          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="generating"
            :disabled="uploadedImages.length === 0 || !form.prompt || !form.workflow"
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

          <el-empty v-if="!generating && !resultVideoUrl && !currentError" description="上传图片并输入提示词后点击生成" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import { uploadApi } from '@/api/upload'
import { resourceApi } from '@/api/resource'
import { pipelineApi } from '@/api/pipeline'
import { taskApi } from '@/api/task'
import type { WorkflowInfo, FileUploadResponse } from '@/types'

interface UploadedImage {
  file: File
  path: string
  preview: string
}

const form = ref({
  prompt: '',
  workflow: '',
  source: 'runninghub' as 'runninghub' | 'selfhost',
})

const uploadedImages = ref<UploadedImage[]>([])
const workflows = ref<WorkflowInfo[]>([])
const generating = ref(false)
const resultVideoUrl = ref('')
const progress = ref(0)
const statusText = ref('')
const currentError = ref<string | null>(null)

let eventSource: EventSource | null = null

onMounted(async () => {
  try {
    const resp = await resourceApi.workflows.image()
    workflows.value = (resp.workflows || []).filter(w => w.name.startsWith('i2v_'))
    if (workflows.value.length > 0) {
      form.value.workflow = workflows.value[0].path
    }
  } catch {
    // ignore
  }
})

async function handleImageUpload(file: File) {
  try {
    const resp: FileUploadResponse = await uploadApi.upload(file, 'image')
    uploadedImages.value.push({
      file,
      path: resp.file_path,
      preview: URL.createObjectURL(file),
    })
    ElMessage.success(`图片 ${file.name} 上传成功`)
  } catch {
    ElMessage.error(`图片 ${file.name} 上传失败`)
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
  if (uploadedImages.value.length === 0) {
    ElMessage.warning('请上传图片')
    return
  }
  if (!form.value.prompt) {
    ElMessage.warning('请输入提示词')
    return
  }
  if (!form.value.workflow) {
    ElMessage.warning('请选择工作流')
    return
  }

  generating.value = true
  resultVideoUrl.value = ''

  try {
    const resp = await pipelineApi.imageToVideo({
      image: uploadedImages.value[0].path,
      prompt: form.value.prompt,
      workflow: form.value.workflow,
      source: form.value.source,
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
.image-to-video-panel { padding: 8px 0; }

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
  grid-template-columns: repeat(4, 1fr);
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

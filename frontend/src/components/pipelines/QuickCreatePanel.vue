<template>
  <div class="quick-create-panel">
    <el-form :model="form" label-width="120px" label-position="top">
      <el-row :gutter="24">
        <!-- Left Column: Content Input -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">内容输入</span></template>

            <el-form-item label="批量模式">
              <el-switch v-model="form.batchMode" />
            </el-form-item>

            <el-form-item label="处理模式">
              <el-radio-group v-model="form.mode">
                <el-radio value="generate">生成模式</el-radio>
                <el-radio value="fixed">固定文本</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item :label="form.mode === 'generate' ? '主题描述' : '视频文本'">
              <el-input
                v-model="form.text"
                type="textarea"
                :rows="form.mode === 'generate' ? 4 : 7"
                :placeholder="form.mode === 'generate' ? '描述你想生成的视频内容...' : '粘贴完整的视频文本...'"
              />
            </el-form-item>

            <template v-if="form.mode === 'fixed'">
              <el-form-item label="分割模式">
                <el-select v-model="form.splitMode" style="width: 100%">
                  <el-option label="按段落" value="paragraph" />
                  <el-option label="按行" value="line" />
                  <el-option label="按句子" value="sentence" />
                </el-select>
              </el-form-item>
            </template>

            <el-form-item label="标题（可选）">
              <el-input v-model="form.title" placeholder="视频标题" />
            </el-form-item>

            <el-form-item v-if="form.mode === 'generate'" label="场景数">
              <el-slider v-model="form.nScenes" :min="3" :max="30" :step="1" show-input />
            </el-form-item>
          </el-card>
        </el-col>

        <!-- Middle Column: Style & TTS -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">风格与配音</span></template>

            <!-- TTS -->
            <el-form-item label="TTS 推理模式">
              <el-radio-group v-model="form.ttsMode">
                <el-radio value="local">本地 (Edge TTS)</el-radio>
                <el-radio value="comfyui">ComfyUI</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="form.ttsMode === 'local'">
              <el-form-item label="语音">
                <el-select v-model="form.ttsVoice" filterable style="width: 100%">
                  <el-option
                    v-for="voice in edgeTtsVoices"
                    :key="voice"
                    :label="voice"
                    :value="voice"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="语速">
                <el-slider v-model="form.ttsSpeed" :min="0.5" :max="2" :step="0.1" show-input />
              </el-form-item>
            </template>

            <template v-else>
              <el-form-item label="参考音频">
                <el-upload
                  :before-upload="(file: File) => handleRefAudioUpload(file)"
                  :show-file-list="!!form.refAudio"
                  :limit="1"
                  accept=".mp3,.wav,.flac,.m4a,.aac,.ogg"
                >
                  <el-button size="small">上传音频</el-button>
                </el-upload>
              </el-form-item>
              <el-form-item label="TTS 工作流">
                <el-select v-model="form.ttsWorkflow" filterable style="width: 100%">
                  <el-option
                    v-for="wf in ttsWorkflows"
                    :key="wf.path"
                    :label="wf.name"
                    :value="wf.path"
                  />
                </el-select>
              </el-form-item>
            </template>

            <!-- Template -->
            <el-form-item label="模板类型">
              <el-radio-group v-model="form.templateType">
                <el-radio value="static">静态</el-radio>
                <el-radio value="image">图片</el-radio>
                <el-radio value="video">视频</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="选择模板">
              <el-select v-model="form.frameTemplate" filterable style="width: 100%">
                <el-option
                  v-for="tpl in filteredTemplates"
                  :key="tpl.path"
                  :label="`${tpl.name} (${tpl.width}x${tpl.height})`"
                  :value="tpl.path"
                />
              </el-select>
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

            <!-- Media Workflow -->
            <el-form-item label="媒体生成工作流">
              <el-select v-model="form.mediaWorkflow" filterable style="width: 100%">
                <el-option
                  v-for="wf in mediaWorkflows"
                  :key="wf.path"
                  :label="wf.name"
                  :value="wf.path"
                />
              </el-select>
            </el-form-item>
          </el-card>
        </el-col>

        <!-- Right Column: Generate & Preview -->
        <el-col :span="8">
          <el-card shadow="hover" class="form-card">
            <template #header><span class="card-title">生成与预览</span></template>

            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="generating"
              :disabled="!form.text"
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { videoApi } from '@/api/video'
import { taskApi } from '@/api/task'
import { resourceApi } from '@/api/resource'
import { uploadApi } from '@/api/upload'
import type { BGMInfo, WorkflowInfo, TemplateInfo } from '@/types'

const edgeTtsVoices = [
  'zh-CN-XiaoxiaoNeural',
  'zh-CN-YunxiNeural',
  'zh-CN-YunjianNeural',
  'zh-CN-XiaoyiNeural',
  'zh-CN-YunyangNeural',
  'en-US-GuyNeural',
  'en-US-JennyNeural',
]

const form = ref({
  batchMode: false,
  mode: 'generate' as 'generate' | 'fixed',
  text: '',
  title: '',
  nScenes: 5,
  splitMode: 'paragraph' as 'paragraph' | 'line' | 'sentence',
  bgmPath: '',
  bgmVolume: 0.2,
  ttsMode: 'local' as 'local' | 'comfyui',
  ttsVoice: 'zh-CN-XiaoxiaoNeural',
  ttsSpeed: 1.2,
  ttsWorkflow: '',
  refAudio: '',
  templateType: 'image' as 'static' | 'image' | 'video',
  frameTemplate: '',
  mediaWorkflow: '',
})

const bgmList = ref<BGMInfo[]>([])
const ttsWorkflows = ref<WorkflowInfo[]>([])
const mediaWorkflows = ref<WorkflowInfo[]>([])
const allTemplates = ref<TemplateInfo[]>([])

const generating = ref(false)
const resultVideoUrl = ref('')
const progress = ref(0)
const statusText = ref('')
const currentError = ref<string | null>(null)

let eventSource: EventSource | null = null

const filteredTemplates = computed(() =>
  allTemplates.value.filter(t => t.type === form.value.templateType)
)

onMounted(async () => {
  try {
    const [bgm, ttsWf, mediaWf, templates] = await Promise.all([
      resourceApi.bgm(),
      resourceApi.workflows.tts(),
      resourceApi.workflows.media(),
      resourceApi.templates(),
    ])
    bgmList.value = bgm.bgm_files || []
    ttsWorkflows.value = ttsWf.workflows || []
    mediaWorkflows.value = mediaWf.workflows || []
    allTemplates.value = templates.templates || []

    if (mediaWorkflows.value.length > 0) {
      form.value.mediaWorkflow = mediaWf.workflows[0].path
    }
    if (allTemplates.value.length > 0) {
      form.value.frameTemplate = templates.templates[0].path
    }
  } catch (e) {
    console.error('Failed to load resources:', e)
  }
})

async function handleRefAudioUpload(file: File) {
  try {
    const resp = await uploadApi.upload(file, 'audio')
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

      const parts: string[] = []
      if (data.step) parts.push(data.step)
      if (data.action) parts.push(data.action)
      if (data.extra_info) parts.push(data.extra_info)
      if (data.frame_current && data.frame_total) {
        parts.push(`${data.frame_current}/${data.frame_total}`)
      }
      statusText.value = parts.length > 0 ? parts.join(' - ') : statusText.value

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
  if (!form.value.text) {
    ElMessage.warning('请输入内容')
    return
  }

  generating.value = true
  resultVideoUrl.value = ''

  try {
    const resp = await videoApi.generateAsync({
      text: form.value.text,
      mode: form.value.mode,
      title: form.value.title || undefined,
      n_scenes: form.value.nScenes,
      split_mode: form.value.mode === 'fixed' ? form.value.splitMode : undefined,
      bgm_path: form.value.bgmPath || undefined,
      bgm_volume: form.value.bgmVolume,
      tts_inference_mode: form.value.ttsMode,
      tts_voice: form.value.ttsMode === 'local' ? form.value.ttsVoice : undefined,
      tts_speed: form.value.ttsMode === 'local' ? form.value.ttsSpeed : undefined,
      tts_workflow: form.value.ttsMode === 'comfyui' ? form.value.ttsWorkflow : undefined,
      ref_audio: form.value.ttsMode === 'comfyui' && form.value.refAudio ? form.value.refAudio : undefined,
      media_workflow: form.value.mediaWorkflow,
      frame_template: form.value.frameTemplate || undefined,
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
.quick-create-panel {
  padding: 8px 0;
}

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

.progress-section {
  margin-top: 20px;
}

.status-text {
  font-size: 12px;
  color: #64748B;
  margin-top: 8px;
}

.error-section {
  margin-top: 16px;
}

.video-preview {
  margin-top: 20px;
}

.video-preview h4 {
  margin-bottom: 12px;
  color: #0C4A6E;
}

.video-player {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
  background: #0F172A;
}
</style>

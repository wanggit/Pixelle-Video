<template>
  <div class="task-detail-modal">
    <el-dialog
      :model-value="visible"
      :title="taskDetail?.title || '任务详情'"
      width="800px"
      @update:model-value="$emit('update:visible', $event)"
    >
      <div v-if="taskDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ taskDetail.task_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="taskDetail.status === 'completed' ? 'success' : 'danger'">
              {{ taskDetail.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时长">{{ formatDuration(taskDetail.duration) }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatSize(taskDetail.file_size) }}</el-descriptions-item>
        </el-descriptions>

        <!-- Video Player -->
        <div v-if="taskDetail.video_url" class="video-container">
          <video :src="taskDetail.video_url" controls class="video-player" />
        </div>

        <!-- Storyboard -->
        <div v-if="taskDetail.storyboard" class="storyboard-section">
          <h4>分镜脚本</h4>
          <pre>{{ JSON.stringify(taskDetail.storyboard, null, 2) }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
        <el-button type="primary" @click="handleDuplicate">重新生成</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { historyApi } from '@/api/history'
import type { HistoryTaskDetail } from '@/types'

const props = defineProps<{ visible: boolean; taskId: string | null }>()
const emit = defineEmits<{ 'update:visible': [boolean] }>()

const taskDetail = ref<HistoryTaskDetail | null>(null)

watch(() => props.taskId, async (id) => {
  if (id) {
    taskDetail.value = await historyApi.detail(id)
  }
}, { immediate: true })

function formatDuration(seconds?: number): string {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`
}

function formatSize(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`
  return `${(bytes / 1024 / 1024).toFixed(1)}MB`
}

async function handleDuplicate() {
  if (props.taskId) {
    await historyApi.duplicate(props.taskId)
    emit('update:visible', false)
  }
}

async function handleDelete() {
  if (props.taskId) {
    await historyApi.remove(props.taskId)
    emit('update:visible', false)
    location.reload()
  }
}
</script>

<style scoped>
.detail-content {
  padding: 16px 0;
}

.video-container {
  margin-top: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 400px;
}

.storyboard-section {
  margin-top: 16px;
}

.storyboard-section h4 {
  margin-bottom: 8px;
}

.storyboard-section pre {
  background: #F0F9FF;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
}
</style>

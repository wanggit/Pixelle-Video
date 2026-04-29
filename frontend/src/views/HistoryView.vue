<template>
  <div class="history-view">
    <h1 class="page-title">历史记录</h1>

    <!-- Statistics -->
    <div class="stats-bar" v-if="stats">
      <el-statistic title="总任务" :value="stats.total_tasks" />
      <el-statistic title="已完成" :value="stats.completed" />
      <el-statistic title="失败" :value="stats.failed" />
      <el-statistic title="总时长" :value="formatDuration(stats.total_duration)" />
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="loadTasks">
        <el-option label="全部" value="" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-select v-model="sortBy" @change="loadTasks">
        <el-option label="按时间" value="created_at" />
        <el-option label="按时长" value="duration" />
      </el-select>
    </div>

    <!-- Task List -->
    <div class="task-grid">
      <div
        v-for="task in tasks"
        :key="task.task_id"
        class="task-card"
        @click="showDetail(task.task_id)"
      >
        <div class="task-thumbnail">
          <img v-if="task.thumbnail" :src="task.thumbnail" alt="" />
          <div v-else class="placeholder">🎬</div>
        </div>
        <div class="task-info">
          <h3 class="task-title">{{ task.title }}</h3>
          <p class="task-date">{{ formatDate(task.created_at) }}</p>
          <el-tag :type="task.status === 'completed' ? 'success' : 'danger'" size="small">
            {{ task.status === 'completed' ? '成功' : '失败' }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <el-pagination
      v-if="totalPages > 1"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="totalTasks"
      layout="prev, pager, next"
      @current-change="loadTasks"
    />

    <!-- Detail Modal -->
    <TaskDetailModal
      v-model:visible="showDetailModal"
      :task-id="selectedTaskId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { historyApi } from '@/api/history'
import type { HistoryTaskSummary, HistoryStatistics } from '@/types'
import TaskDetailModal from '@/components/history/TaskDetailModal.vue'

const tasks = ref<HistoryTaskSummary[]>([])
const stats = ref<HistoryStatistics | null>(null)
const filterStatus = ref('')
const sortBy = ref('created_at')
const currentPage = ref(1)
const pageSize = ref(20)
const totalTasks = ref(0)
const totalPages = ref(0)
const showDetailModal = ref(false)
const selectedTaskId = ref('')

async function loadTasks() {
  const resp = await historyApi.list(
    currentPage.value, pageSize.value,
    filterStatus.value || undefined, sortBy.value
  )
  tasks.value = resp.tasks
  totalTasks.value = resp.total
  totalPages.value = resp.total_pages
}

async function loadStats() {
  stats.value = await historyApi.statistics()
}

function showDetail(taskId: string) {
  selectedTaskId.value = taskId
  showDetailModal.value = true
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(0)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
}

onMounted(() => {
  loadTasks()
  loadStats()
})
</script>

<style scoped>
.history-view {
  padding-bottom: 48px;
}

.page-title {
  font-family: 'Poppins', sans-serif;
  font-size: 28px;
  font-weight: 600;
  color: #0C4A6E;
  margin-bottom: 24px;
}

.stats-bar {
  display: flex;
  gap: 32px;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  border: 1px solid #BAE6FD;
  margin-bottom: 16px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.taskgrid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.task-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #BAE6FD;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 200ms ease-out;
}

.task-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.task-thumbnail {
  width: 100%;
  height: 160px;
  background: #F0F9FF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  font-size: 48px;
}

.task-info {
  padding: 12px;
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  color: #0C4A6E;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-date {
  font-size: 12px;
  color: #64748B;
  margin-bottom: 8px;
}
</style>

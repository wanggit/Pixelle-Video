<template>
  <div class="home-view">
    <h1 class="page-title">Pixelle-Video</h1>
    <p class="page-subtitle">AI 全自动短视频引擎</p>

    <!-- Pipeline Tabs -->
    <el-tabs v-model="activePipeline" class="pipeline-tabs">
      <el-tab-pane label="⚡ 快速创作" name="quick_create">
        <QuickCreatePanel />
      </el-tab-pane>
      <el-tab-pane label="🎨 素材创作" name="custom_media">
        <CustomMediaPanel />
      </el-tab-pane>
      <el-tab-pane label="🎬 图生视频" name="image_to_video">
        <ImageToVideoPanel />
      </el-tab-pane>
      <el-tab-pane label="💃 动作迁移" name="action_transfer">
        <ActionTransferPanel />
      </el-tab-pane>
      <el-tab-pane label="🤖 数字人" name="digital_human">
        <DigitalHumanPanel />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import QuickCreatePanel from '@/components/pipelines/QuickCreatePanel.vue'
import CustomMediaPanel from '@/components/pipelines/CustomMediaPanel.vue'
import ImageToVideoPanel from '@/components/pipelines/ImageToVideoPanel.vue'
import ActionTransferPanel from '@/components/pipelines/ActionTransferPanel.vue'
import DigitalHumanPanel from '@/components/pipelines/DigitalHumanPanel.vue'

const activePipeline = ref('quick_create')
</script>

<style scoped>
.home-view {
  padding-bottom: 48px;
}

.page-title {
  font-family: 'Poppins', sans-serif;
  font-size: 28px;
  font-weight: 600;
  color: #0C4A6E;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 24px;
}

.pipeline-tabs :deep(.el-tabs__item) {
  font-size: 14px;
}

.pipeline-tabs :deep(.el-tabs__item.is-active) {
  color: #0EA5E9;
}
</style>

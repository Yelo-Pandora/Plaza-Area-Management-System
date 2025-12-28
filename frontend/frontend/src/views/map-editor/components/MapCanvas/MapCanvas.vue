<template>
  <main class="map-canvas-container">
    <!-- 保存按钮区域 -->
    <div class="canvas-toolbar">
      <button
        class="btn-save"
        @click="handleSaveAll"
        :disabled="isSaving || loading || !currentMap"
      >
        <span v-if="isSaving" class="spinner"></span>
        <span v-else>💾 保存更改</span>
      </button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="!currentMap" class="empty-state">
      <span class="empty-icon">🗺️</span>
      <p>请选择一个地图进行编辑</p>
    </div>

    <div v-else class="map-canvas-wrapper">
      <div ref="stageContainer" class="konva-stage-container"></div>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useCanvasLogic } from './MapCanvas.js'
import { useMapSaveLogic } from './MapSaveLogic.js' // 引入新逻辑
import { useMapEditorStore } from '../../composables/useMapEditorStore'

const { loading, currentMap } = useMapEditorStore()
const stageContainer = ref(null)

// 初始化 Canvas 逻辑
useCanvasLogic(stageContainer)

// 初始化 保存 逻辑
const { handleSaveAll, isSaving } = useMapSaveLogic()
</script>

<style scoped src="./MapCanvas.css"></style>

<template>
  <main class="map-canvas-container">
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
import { useMapEditorStore } from '../../composables/useMapEditorStore'
const { loading, currentMap } = useMapEditorStore()
const stageContainer = ref(null)
useCanvasLogic(stageContainer)
</script>

<style scoped src="./MapCanvas.css"></style>

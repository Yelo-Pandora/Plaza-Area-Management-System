<template>
  <div class="map-editor-layout">
    <MapHeader />

    <div class="editor-body">
      <!-- 传递事件打开弹窗 -->
      <LayerSidebar @open-create="showCreate = true" />
      <MapCanvas />
      <PropertiesPanel />
    </div>

    <!-- 弹窗 -->
    <CreateModal :visible="showCreate" @update:visible="showCreate = $event" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMapEditorStore } from './composables/useMapEditorStore'

import MapHeader from './components/EditorHeader/EditorHeader.vue'
import LayerSidebar from './components/Sidebar/Sidebar.vue'
import MapCanvas from './components/MapCanvas/MapCanvas.vue'
import PropertiesPanel from './components/PropertyPanel/PropertyPanel.vue'
import CreateModal from './components/CreateModel/CreateModel.vue'

const { loadMaps } = useMapEditorStore()
const showCreate = ref(false)

onMounted(() => {
  loadMaps()
})
</script>

<style scoped>
.map-editor-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>

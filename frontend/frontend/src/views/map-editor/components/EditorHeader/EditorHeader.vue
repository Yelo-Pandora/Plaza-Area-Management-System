<template>
  <div class="header">
    <h1 class="title">地图编辑器</h1>
    <div class="actions">
      <button class="btn-create-map" @click="showCreateMap = true">
        📄 新建地图
      </button>
      <button
        class="btn-delete-map"
        @click="handleDeleteMap"
        :disabled="!currentMapId"
        v-if="currentMapId"
      >
        🗑️ 删除当前地图
      </button>

      <div class="map-selector">
        <select v-model="currentMapId" @change="handleChange" class="filter-select">
          <option value="">选择地图</option>
          <option v-for="m in maps" :key="m.id" :value="m.id">
            {{ m.building_name || '地图' }} - 楼层 {{ m.floor_number }}
          </option>
        </select>
      </div>
    </div>

    <!-- 2. 新增：挂载弹窗组件 -->
    <CreateMapModal
      :visible="showCreateMap"
      @update:visible="showCreateMap = $event"
    />
  </div>
</template>

<script setup>
import { useHeaderLogic } from './EditorHeader.js'
import CreateMapModal from '../CreateMapModal/CreateMapModal.vue'

// 解构出 showCreateMap
const { maps, currentMapId, handleChange, showCreateMap, handleDeleteMap } = useHeaderLogic()
</script>

<style scoped src="./EditorHeader.css"></style>

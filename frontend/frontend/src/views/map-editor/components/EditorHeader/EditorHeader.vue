<template>
  <div class="header">
    <h1 class="title">地图编辑器</h1>
    <div class="actions">
      <div class="map-selector">
        <select v-model="currentMapId" @change="handleChange" class="filter-select">
          <option value="">选择地图</option>
          <option v-for="m in maps" :key="m.id" :value="m.id">
            {{ m.building_name || '地图' }} - 楼层 {{ m.floor_number }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useHeaderLogic } from './EditorHeader'
const { maps, currentMapId, handleChange } = useHeaderLogic()
</script>

<style scoped src="./EditorHeader.css"></style>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3 class="sidebar-title">区域列表</h3>
      <button class="btn btn-primary" @click="$emit('open-create')">
        <span class="btn-icon">+</span> 新建区域
      </button>
    </div>

    <div class="layer-groups">
      <!-- 1. 店铺区域 -->
      <div class="layer-group">
        <div class="layer-group-header" @click="toggleLayer('storearea')">
          <span class="layer-icon">🏪</span>
          <span class="layer-title">店铺区域</span>
          <span class="layer-count">({{ storeareas.length }})</span>
          <span :class="['layer-toggle', { expanded: expandedLayers.storearea }]">
            {{ expandedLayers.storearea ? '▼' : '▶' }}
          </span>
        </div>
        <div v-if="expandedLayers.storearea" class="layer-items">
          <div
            v-for="area in storeareas"
            :key="area.id"
            :class="['layer-item', { selected: isSelected('storearea', area.id) }]"
            @click="handleSelect('storearea', area)"
          >
            <span class="layer-item-name">{{ area.store_name || '未命名' }}</span>
          </div>
        </div>
      </div>

      <!-- 2. 活动区域 -->
      <div class="layer-group">
        <div class="layer-group-header" @click="toggleLayer('eventarea')">
          <span class="layer-icon">🎪</span>
          <span class="layer-title">活动区域</span>
          <span class="layer-count">({{ eventareas.length }})</span>
          <span :class="['layer-toggle', { expanded: expandedLayers.eventarea }]">
            {{ expandedLayers.eventarea ? '▼' : '▶' }}
          </span>
        </div>
        <div v-if="expandedLayers.eventarea" class="layer-items">
          <div
            v-for="area in eventareas"
            :key="area.id"
            :class="['layer-item', { selected: isSelected('eventarea', area.id) }]"
            @click="handleSelect('eventarea', area)"
          >
            <span class="layer-item-name">{{ area.event_name || '未命名' }}</span>
          </div>
        </div>
      </div>

      <!-- 3. 其他区域 -->
      <div class="layer-group">
        <div class="layer-group-header" @click="toggleLayer('otherarea')">
          <span class="layer-icon">🏢</span>
          <span class="layer-title">其他区域</span>
          <span class="layer-count">({{ otherareas.length }})</span>
          <span :class="['layer-toggle', { expanded: expandedLayers.otherarea }]">
            {{ expandedLayers.otherarea ? '▼' : '▶' }}
          </span>
        </div>
        <div v-if="expandedLayers.otherarea" class="layer-items">
          <div
            v-for="area in otherareas"
            :key="area.id"
            :class="['layer-item', { selected: isSelected('otherarea', area.id) }]"
            @click="handleSelect('otherarea', area)"
          >
            <span class="layer-item-name">{{ area.name || '未命名' }}</span>
          </div>
        </div>
      </div>

      <!-- 4. 设施 -->
      <div class="layer-group">
        <div class="layer-group-header" @click="toggleLayer('facility')">
          <span class="layer-icon">🚻</span>
          <span class="layer-title">设施</span>
          <span class="layer-count">({{ facilities.length }})</span>
          <span :class="['layer-toggle', { expanded: expandedLayers.facility }]">
            {{ expandedLayers.facility ? '▼' : '▶' }}
          </span>
        </div>
        <div v-if="expandedLayers.facility" class="layer-items">
          <div
            v-for="facility in facilities"
            :key="facility.id"
            :class="['layer-item', { selected: isSelected('facility', facility.id) }]"
            @click="handleSelect('facility', facility)"
          >
            <span class="layer-item-name">{{ facility.description || '未命名' }}</span>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useSidebarLogic } from './Sidebar.js'
const {
  storeareas, eventareas, otherareas, facilities,
  expandedLayers, toggleLayer, handleSelect, isSelected
} = useSidebarLogic()

defineEmits(['open-create'])
</script>

<style scoped src="./Sidebar.css"></style>

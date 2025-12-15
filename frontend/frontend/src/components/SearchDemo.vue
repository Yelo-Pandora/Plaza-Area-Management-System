<script setup>
import { ref } from 'vue'
import {
  getStoreareaById,
  searchStoreareaByName,
  listStoreareaByType,
  getStoreareaEvents,
  getAllStoreareaIdsByMap
} from '../api/search'

const id = ref('')
const name = ref('')
const type = ref('')
const mapId = ref('')
const result = ref(null)
const error = ref(null)

async function doGetById() {
  error.value = null
  result.value = null
  try {
    result.value = await getStoreareaById(id.value)
  } catch (e) {
    error.value = e.message || JSON.stringify(e)
  }
}

async function doSearchByName() {
  error.value = null
  result.value = null
  try {
    result.value = await searchStoreareaByName(name.value)
  } catch (e) {
    error.value = e.message || JSON.stringify(e)
  }
}

async function doListByType() {
  error.value = null
  result.value = null
  try {
    result.value = await listStoreareaByType(type.value)
  } catch (e) {
    error.value = e.message || JSON.stringify(e)
  }
}

async function doEvents() {
  error.value = null
  result.value = null
  try {
    result.value = await getStoreareaEvents(id.value)
  } catch (e) {
    error.value = e.message || JSON.stringify(e)
  }
}

async function doAllIdsByMap() {
  error.value = null
  result.value = null
  try {
    result.value = await getAllStoreareaIdsByMap(mapId.value)
  } catch (e) {
    error.value = e.message || JSON.stringify(e)
  }
}
</script>

<template>
  <section class="search-demo">
    <h2>Search API 示例</h2>

    <div class="row">
      <label>Storearea ID: <input v-model="id" /></label>
      <button @click="doGetById">按 ID 获取</button>
      <button @click="doEvents">获取该店铺的活动列表</button>
    </div>

    <div class="row">
      <label>名称搜索: <input v-model="name" /></label>
      <button @click="doSearchByName">按名称搜索</button>
    </div>

    <div class="row">
      <label>类型搜索: <input v-model="type" /></label>
      <button @click="doListByType">按类型列出</button>
    </div>

    <div class="row">
      <label>Map ID: <input v-model="mapId" /></label>
      <button @click="doAllIdsByMap">获取地图所有 storearea id</button>
    </div>

    <div class="output">
      <h3>结果</h3>
      <div v-if="error" class="error">错误: {{ error }}</div>
      <pre v-else>{{ result ? JSON.stringify(result, null, 2) : '尚无结果' }}</pre>
    </div>
  </section>
</template>

<style scoped>
.search-demo { padding: 1rem; border: 1px solid #e6e6e6; border-radius: 8px; margin: 1rem; }
.row { display:flex; gap:0.5rem; align-items:center; margin:0.5rem 0 }
button { padding: 0.3rem 0.6rem }
.output { margin-top:1rem }
.error { color: #b00020 }
</style>

<template>
  <aside class="properties-panel">
    <div class="panel-header">
      <h3 class="panel-title">属性编辑</h3>
    </div>

    <div v-if="!selectedFeature" class="panel-empty">
      <p>请选择一个区域进行编辑</p>
    </div>

    <div v-else class="panel-content">
      <form @submit.prevent="save" class="properties-form">
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label class="form-label">ID</label>
          <input type="text" :value="selectedFeature.id" class="form-input" disabled>
        </div>

        <div class="form-group" v-if="selectedType === 'storearea'">
          <label class="form-label">名称</label>
          <input
            v-model="form.name"
            type="text"
            class="form-input"
            :placeholder="`请输入${getTypeName()}名称`"
          >
        </div>

        <div class="form-group">
          <label class="form-label">类型</label>
          <select v-model="form.type" class="form-select">
             <template v-if="selectedType === 'storearea'">
              <option value="0">普通店铺</option>
              <option value="1">餐饮</option>
              <option value="2">服饰</option>
              <option value="3">娱乐</option>
              <option value="4">服务</option>
            </template>
            <template v-if="selectedType === 'eventarea'">
              <option value="0">通用活动区域</option>
              <option value="1">促销活动</option>
              <option value="2">展览活动</option>
              <option value="3">表演活动</option>
            </template>
            <template v-if="selectedType === 'otherarea'">
              <option value="0">公共区域</option>
              <option value="1">卫生间</option>
              <option value="2">电梯间</option>
              <option value="3">其他</option>
            </template>
            <template v-if="selectedType === 'facility'">
              <option value="0">电动扶梯</option>
              <option value="1">灭火器</option>
              <option value="2">安全出口</option>
              <option value="3">服务台</option>
              <option value="4">其他</option>
            </template>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea
            v-model="form.description"
            class="form-textarea"
            rows="3"
            :placeholder="`请输入${getTypeName()}描述`"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">状态</label>
          <div class="toggle-switch">
            <input
              v-model="form.is_active"
              type="checkbox"
              id="status-toggle"
              class="toggle-input"
            >
            <label for="status-toggle" class="toggle-label">
              <span class="toggle-slider"></span>
              <span class="toggle-text">{{ form.is_active ? '启用' : '停用' }}</span>
            </label>
          </div>
        </div>

        <div class="form-actions space-between">
          <button
            type="button"
            class="btn btn-danger"
            @click="handleDelete"
            :disabled="submitting || isDeleting"
          >
            删除
          </button>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="submitting || isDeleting"
          >
            <span v-if="submitting" class="btn-spinner"></span>
            保存属性
          </button>
        </div>
      </form>
    </div>
  </aside>
</template>

<script setup>
import { usePropertiesLogic } from './PropertyPanel.js'
const { form, selectedFeature, selectedType, save, handleDelete, submitting, isDeleting, errorMessage, getTypeName } = usePropertiesLogic()
</script>

<style scoped src="./PropertyPanel.css"></style>

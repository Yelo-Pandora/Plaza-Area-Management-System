<template>
  <div v-if="visible" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">新建区域</h3>
        <button class="modal-close" @click="close">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleCreate">
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <div class="form-group">
            <label class="form-label">区域类型</label>
            <select v-model="form.type" class="form-select">
              <option value="storearea">店铺区域</option>
              <option value="eventarea">活动区域</option>
              <option value="otherarea">其他区域</option>
              <!-- 设施一般为点，暂不支持形状模板，或者可加Point模板 -->
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">图形模板</label>
            <div class="shape-templates">
              <div
                v-for="tpl in shapeTemplates"
                :key="tpl.shape"
                :class="['shape-template', { selected: form.shape === tpl.shape }]"
                @click="form.shape = tpl.shape"
              >
                <span class="template-icon">{{ tpl.icon }}</span>
                <span class="template-label">{{ tpl.label }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">大小</label>
            <div class="size-control">
              <input
                v-model.number="form.size"
                type="range"
                min="10"
                max="100"
                class="size-slider"
              >
              <span class="size-value">{{ form.size }}</span>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="close">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="btn-spinner"></span>
              创建
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCreateModalLogic } from './CreateModel.js'
const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible'])

const { form, shapeTemplates, handleCreate, close, submitting, errorMessage } = useCreateModalLogic(props, emit)
</script>

<style scoped src="./CreateModel.css"></style>

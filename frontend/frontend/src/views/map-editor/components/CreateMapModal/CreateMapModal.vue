<template>
  <div v-if="visible" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">新建地图</h3>
        <button class="modal-close" @click="close">×</button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div v-if="error" class="error-message">{{ error }}</div>

          <!-- 1. 建筑选择 (暂硬编码，实际可调API) -->
          <div class="form-group">
            <label class="form-label">所属建筑</label>
              <select v-model="form.building_id" class="form-select" required>
                <option value="" disabled>请选择建筑</option>
                <!-- 对应数据库 ID 1 -->
                <option value="1">Benchmark Mega Mall</option>
              </select>
          </div>

          <!-- 2. 楼层输入 -->
          <div class="form-group">
            <label class="form-label">楼层号</label>
            <input
              v-model.number="form.floor_number"
              type="number"
              class="form-input"
              placeholder="例如: 1, 2, -1"
              required
            />
          </div>

          <!-- 3. 模式选择 -->
          <div class="form-group">
            <label class="form-label">创建方式</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="form.mode" value="manual" />
                <span>手动绘制 (空白)</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="form.mode" value="import" />
                <span>CAD 导入 (.dxf)</span>
              </label>
            </div>
          </div>

          <!-- 4. 文件上传 -->
          <div v-if="form.mode === 'import'" class="form-group">
            <label class="form-label">上传 DXF 文件</label>
            <input
              type="file"
              accept=".dxf"
              @change="handleFileChange"
              class="form-input file-input"
              required
            />

            <!-- 图层规范说明 -->
            <div class="layer-guide">
              <p class="guide-title">CAD 图层规范 (需闭合线，单位: mm)</p>
              <ul class="guide-list">
                <li><span class="tag floor">FLOOR_OUTLINE</span> 地板轮廓</li>
                <li><span class="tag void">VOIDS</span> 中庭/镂空</li>
                <li><span class="tag store">AREA_STORE</span> 店铺区域</li>
                <li><span class="tag event">AREA_EVENT</span> 活动区域</li>
                <li><span class="tag other">AREA_OTHER</span> 其他区域</li>
                <li><span class="tag fac">FACILITIES</span> 设施(点/圆)</li>
              </ul>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="close">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="btn-spinner"></span>
              {{ form.mode === 'import' ? '导入并解析' : '创建空白地图' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCreateMapLogic } from './CreateMapModal.js'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible'])

const {
  form,
  submitting,
  error,
  close,
  handleFileChange,
  handleSubmit
} = useCreateMapLogic(props, emit)
</script>

<style scoped src="./CreateMapModal.css"></style>

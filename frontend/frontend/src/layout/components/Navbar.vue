<script setup>
const props = defineProps({
  projectName: {
    type: String,
    default: ''
  },
  username: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['logout'])

function onLogoutClick() {
  emit('logout')
}
</script>

<template>
  <header class="navbar">
    <div class="navbar-left">
      <span class="navbar-title">{{ props.projectName }}</span>
    </div>
    <div class="navbar-right">
      <span class="navbar-username">当前用户：{{ props.username || '未登录' }}</span>
      <button class="navbar-btn" type="button" @click="onLogoutClick">
        退出登录
      </button>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  background-color: #111827;
  color: #f9fafb;
}

.navbar-title {
  font-size: 18px;
  font-weight: 600;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.navbar-username {
  opacity: 0.85;
}

.navbar-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #f97316;
  background-color: #f97316;
  color: #ffffff;
  cursor: pointer;
  font-size: 13px;
}

.navbar-btn:hover {
  background-color: #ea580c;
}
</style>



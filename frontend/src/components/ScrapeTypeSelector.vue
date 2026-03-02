<template>
  <div class="scrape-type-selector mt-4">
    <label class="selector-label">Chọn chế độ cào dữ liệu</label>
    
    <div style="display: flex; gap: 0.75rem; margin-top: 0.75rem">
      <div 
        class="mode-card"
        :class="{ 'mode-selected': modelValue === 'info' }"
        @click="selectMode('info')"
      >
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem">
          <i class="pi pi-info-circle" style="font-size: 1.25rem; color: var(--blue-500)"></i>
          <strong style="flex: 1">Cào thông tin</strong>
          <i v-if="modelValue === 'info'" class="pi pi-check-circle" style="color: var(--green-500)"></i>
        </div>
        <p class="mode-description">
          Lấy đầy đủ thông tin chi tiết về khách sạn và phòng
        </p>
       
      </div>

      <div 
        class="mode-card"
        :class="{ 'mode-selected': modelValue === 'price' }"
        @click="selectMode('price')"
      >
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem">
          <i class="pi pi-dollar" style="font-size: 1.25rem; color: var(--green-500)"></i>
          <strong style="flex: 1">Cào giá</strong>
          <i v-if="modelValue === 'price'" class="pi pi-check-circle" style="color: var(--green-500)"></i>
        </div>
        <p class="mode-description">
          Chỉ lấy thông tin về giá và khuyến mãi
        </p>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: 'info' | 'price' | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: 'info' | 'price'): void
}>()

function selectMode(mode: 'info' | 'price') {
  emit('update:modelValue', mode)
}
</script>

<style scoped>
.selector-label {
  font-weight: 600;
  color: var(--text-color);
  display: block;
}

.mode-card {
  flex: 1;
  padding: 1rem;
  border: 2px solid var(--surface-200);
  background: var(--surface-50);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-card:hover {
  border-color: var(--primary-color);
  background: var(--surface-100);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.mode-selected {
  border-color: var(--primary-color);
  background: var(--primary-50);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.15);
}

.mode-description {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.mode-includes {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  line-height: 1.4;
}
</style>

<template>
  <div class="config-view">
    <Card>
      <template #title>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 2rem;">
          <span><i class="pi pi-cog mr-2"></i>Quản lý Config</span>
          <Button label="Thêm Config" icon="pi pi-plus" @click="openCreateDialog" severity="primary" />
        </div>
      </template>
      <template #content>
        <TabView v-model:activeIndex="activeTab">
          <TabPanel header="Market" :value="0">
            <DataTable :value="getConfigsByCategory('market')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          <TabPanel header="Cluster" :value="1">
            <DataTable :value="getConfigsByCategory('cluster')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          <TabPanel header="Level đối thủ" :value="2">
            <DataTable :value="getConfigsByCategory('competitor_level')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          <TabPanel header="Bữa sáng" :value="3">
            <DataTable :value="getConfigsByCategory('breakfast')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          <TabPanel header="Nhóm hạng phòng" :value="4">
            <DataTable :value="getConfigsByCategory('room_group')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          <TabPanel header="Level" :value="5">
            <DataTable :value="getConfigsByCategory('level')" responsiveLayout="scroll">
              <Column field="config_key" header="Code" style="width: 30%"></Column>
              <Column field="config_value" header="Value" style="width: 60%"></Column>
              <Column header="Thao tác" style="width: 10%">
                <template #body="slotProps">
                  <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editConfig(slotProps.data)" />
                    <Button icon="pi pi-trash" class="p-button-sm" severity="danger" @click="deleteConfig(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
        </TabView>
      </template>
    </Card>

    <!-- Dialog for Config Items -->
    <Dialog v-model:visible="showDialog" :header="dialogMode === 'create' ? 'Thêm Config' : 'Sửa Config'" :style="{ width: '500px' }" modal>
      <div class="p-fluid">
        <div class="field" v-if="dialogMode === 'create'">
          <div class="flex align-items-center gap-2 mb-3">
            <Checkbox v-model="bulkAddMode" inputId="bulkMode" binary />
            <label for="bulkMode" style="cursor: pointer">Thêm nhiều config cùng lúc</label>
          </div>
        </div>
        
        <div class="field">
          <label for="category">Loại</label>
          <Dropdown 
            v-model="formData.category" 
            :options="categoryOptions" 
            optionLabel="label" 
            optionValue="value" 
            placeholder="Chọn loại" 
            :disabled="dialogMode === 'edit'"
          />
        </div>
        
        <template v-if="!bulkAddMode">
          <div class="field">
            <label for="key">Code</label>
            <InputText v-model="formData.config_key" placeholder="Nhập code (ví dụ: A, 1, 0)" style="width: 100%" />
          </div>
          <div class="field">
            <label for="value">Value</label>
            <InputText v-model="formData.config_value" placeholder="Nhập value" style="width: 100%" />
          </div>
        </template>
        
        <template v-else>
          <div class="field">
            <label for="bulkData">Nhập nhiều config</label>
            <small class="block mb-2" style="color: var(--text-color-secondary)">
              Nhập mỗi config trên một dòng theo format: <strong>code,value</strong><br/>
              Ví dụ: A,Level đối thủ cao
            </small>
            <Textarea 
              v-model="bulkData" 
              rows="10" 
              placeholder="A,Level đối thủ cao&#10;B,Level đối thủ trung bình&#10;C,Level đối thủ thấp"
              style="font-family: monospace"
            />
          </div>
        </template>
      </div>
      <template #footer>
        <Button label="Hủy" icon="pi pi-times" @click="showDialog = false" severity="secondary" text />
        <Button label="Lưu" icon="pi pi-check" @click="saveConfig" :loading="saving" severity="primary" />
      </template>
    </Dialog>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'
import Card from 'primevue/card'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import Toast from 'primevue/toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const toast = useToast()

interface ConfigItem {
  id: number
  category: string
  config_key: string
  config_value: string
}

const allConfigs = ref<Record<string, ConfigItem[]>>({})
const activeTab = ref(0)
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const saving = ref(false)
const bulkAddMode = ref(false)
const bulkData = ref('')

const formData = ref({
  id: null as number | null,
  category: 'market',
  config_key: '',
  config_value: ''
})

const categoryOptions = [
  { label: 'Market', value: 'market' },
  { label: 'Cluster', value: 'cluster' },
  { label: 'Level đối thủ', value: 'competitor_level' },
  { label: 'Bữa sáng', value: 'breakfast' },
  { label: 'Nhóm hạng phòng', value: 'room_group' },
  { label: 'Level', value: 'level' }
]

async function loadConfigs() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/config`)
    allConfigs.value = response.data
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể tải configs',
      life: 3000
    })
  }
}

function getConfigsByCategory(category: string) {
  return allConfigs.value[category] || []
}

function openCreateDialog() {
  dialogMode.value = 'create'
  formData.value = {
    id: null,
    category: categoryOptions[activeTab.value]?.value || 'competitor_level',
    config_key: '',
    config_value: ''
  }
  bulkAddMode.value = false
  bulkData.value = ''
  showDialog.value = true
}

function editConfig(config: ConfigItem) {
  dialogMode.value = 'edit'
  formData.value = {
    id: config.id,
    category: config.category,
    config_key: config.config_key,
    config_value: config.config_value
  }
  showDialog.value = true
}

async function saveConfig() {
  // Bulk add mode
  if (bulkAddMode.value && dialogMode.value === 'create') {
    if (!bulkData.value.trim()) {
      toast.add({
        severity: 'warn',
        summary: 'Cảnh báo',
        detail: 'Vui lòng nhập dữ liệu',
        life: 3000
      })
      return
    }

    saving.value = true
    try {
      const lines = bulkData.value.split('\n').filter(line => line.trim())
      let successCount = 0
      let errorCount = 0

      for (const line of lines) {
        const parts = line.split(',').map(p => p.trim())
        if (parts.length >= 2) {
          const [code, value] = parts
          try {
            await axios.post(`${API_BASE_URL}/api/config`, {
              category: formData.value.category,
              config_key: code,
              config_value: value
            })
            successCount++
          } catch (error) {
            errorCount++
            console.error(`Failed to add config: ${line}`, error)
          }
        }
      }

      toast.add({
        severity: successCount > 0 ? 'success' : 'error',
        summary: 'Kết quả',
        detail: `Đã thêm ${successCount} config${errorCount > 0 ? `, ${errorCount} lỗi` : ''}`,
        life: 3000
      })

      showDialog.value = false
      bulkData.value = ''
      bulkAddMode.value = false
      await loadConfigs()
    } catch (error: any) {
      toast.add({
        severity: 'error',
        summary: 'Lỗi',
        detail: 'Không thể lưu config',
        life: 3000
      })
    } finally {
      saving.value = false
    }
    return
  }

  // Single add/edit mode
  if (!formData.value.config_key || !formData.value.config_value) {
    toast.add({
      severity: 'warn',
      summary: 'Cảnh báo',
      detail: 'Vui lòng điền đầy đủ thông tin',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await axios.post(`${API_BASE_URL}/api/config`, {
        category: formData.value.category,
        config_key: formData.value.config_key,
        config_value: formData.value.config_value
      })
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã thêm config',
        life: 3000
      })
    } else {
      await axios.put(`${API_BASE_URL}/api/config/${formData.value.id}`, {
        config_key: formData.value.config_key,
        config_value: formData.value.config_value
      })
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã cập nhật config',
        life: 3000
      })
    }
    showDialog.value = false
    await loadConfigs()
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể lưu config',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

async function deleteConfig(config: ConfigItem) {
  if (!confirm(`Xóa config "${config.config_key}: ${config.config_value}"?`)) return

  try {
    await axios.delete(`${API_BASE_URL}/api/config/${config.id}`)
    toast.add({
      severity: 'success',
      summary: 'Thành công',
      detail: 'Đã xóa config',
      life: 3000
    })
    await loadConfigs()
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể xóa config',
      life: 3000
    })
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.config-view {
  padding: 2rem 0;
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.field small {
  font-size: 0.875rem;
}

.p-fluid .field:last-child {
  margin-bottom: 0;
}
</style>

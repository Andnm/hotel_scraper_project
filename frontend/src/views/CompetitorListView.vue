<template>
  <div class="competitor-list-view">
    <Card>
      <template #title>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 2rem;">
          <span><i class="pi pi-users mr-2"></i>Competitor List</span>
          <div style="display: flex; gap: 1rem; align-items: center;">
            <Button label="Import Excel" icon="pi pi-upload" @click="triggerFileInput" severity="primary" />
            <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleFileUpload" style="display: none" />
            <Button label="Thêm mới" icon="pi pi-plus" @click="openCreateDialog" severity="primary" />
          </div>
        </div>
      </template>
      <template #content>
        <DataTable 
          :value="competitors" 
          :paginator="true" 
          :rows="20"
          :loading="loading"
          scrollable
          scrollHeight="600px"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
          :rowsPerPageOptions="[10,20,50]"
          filterDisplay="row"
          v-model:filters="filters"
        >
          <!-- 1. Tên khách sạn -->
          <Column field="hotel_name" header="Tên khách sạn" :frozen="true" style="min-width: 200px" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Tìm tên KS" class="p-column-filter" />
            </template>
          </Column>
          
          <!-- 2. Link khách sạn -->
          <Column field="hotel_link" header="Link khách sạn" style="min-width: 150px" :sortable="true">
            <template #body="slotProps">
              <a v-if="slotProps.data.hotel_link" :href="slotProps.data.hotel_link" target="_blank" class="text-primary" style="text-decoration: underline;">
                <i class="pi pi-external-link"></i> Link
              </a>
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Tìm link" class="p-column-filter" />
            </template>
          </Column>
          
          <!-- 3. Tên hạng phòng -->
          <Column field="room_type" header="Tên hạng phòng" style="min-width: 180px" :sortable="true">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Tìm hạng phòng" class="p-column-filter" />
            </template>
          </Column>
          
          <!-- 4. Số lượng người -->
          <Column field="num_people" header="Số người" style="width: 100px" :sortable="true"></Column>
          
          <!-- 5. Giường -->
          <Column field="bed_info" header="Giường" style="min-width: 150px" :sortable="true"></Column>
          
          <!-- 6. Diện tích phòng -->
          <Column field="room_area" header="Diện tích" style="width: 120px" :sortable="true"></Column>
          
          <!-- 7. Các lựa chọn -->
          <Column field="room_choices" header="Các lựa chọn" style="min-width: 200px" :sortable="true">
            <template #body="slotProps">
              <div style="max-height: 60px; overflow-y: auto;">{{ slotProps.data.room_choices }}</div>
            </template>
          </Column>
          
          <!-- 8. Các tiện nghi được ưa chuộng nhất -->
          <Column field="popular_facilities" header="Tiện nghi" style="min-width: 200px" :sortable="true">
            <template #body="slotProps">
              <div style="max-height: 60px; overflow-y: auto;">{{ slotProps.data.popular_facilities }}</div>
            </template>
          </Column>
          
          <!-- 9. Market -->
          <Column field="market" header="Market" style="width: 150px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(marketOptions, slotProps.data.market) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="marketOptions" optionLabel="label" optionValue="value" placeholder="Chọn market" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- 10. Cluster -->
          <Column field="cluster" header="Cluster" style="width: 150px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(clusterOptions, slotProps.data.cluster) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="clusterOptions" optionLabel="label" optionValue="value" placeholder="Chọn cluster" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- 11. Level đối thủ -->
          <Column field="competitor_level" header="Level ĐT" style="width: 150px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(competitorLevelOptions, slotProps.data.competitor_level) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="competitorLevelOptions" optionLabel="label" optionValue="value" placeholder="Chọn level" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- 12. Giá bao gồm bữa sáng -->
          <Column field="breakfast_included" header="Giá bao gồm bữa sáng" style="width: 180px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(breakfastOptions, slotProps.data.breakfast_included) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="breakfastOptions" optionLabel="label" optionValue="value" placeholder="Chọn" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- 13. Nhóm hạng phòng -->
          <Column field="room_group" header="Nhóm hạng phòng" style="width: 170px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(roomGroupOptions, slotProps.data.room_group) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="roomGroupOptions" optionLabel="label" optionValue="value" placeholder="Chọn nhóm" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- 14. Level -->
          <Column field="level" header="Level" style="width: 120px" :sortable="true">
            <template #body="slotProps">
              {{ getConfigLabel(levelOptions, slotProps.data.level) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <MultiSelect v-model="filterModel.value" @change="filterCallback()" :options="levelOptions" optionLabel="label" optionValue="value" placeholder="Chọn level" :maxSelectedLabels="1" class="p-column-filter" display="chip" />
            </template>
          </Column>
          
          <!-- Actions -->
          <Column header="Thao tác" style="width: 100px" :frozen="true" alignFrozen="right">
            <template #body="slotProps">
              <Button icon="pi pi-ellipsis-h" class="p-button-sm p-button-text" @click="toggleMenu($event, slotProps.data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Actions Menu -->
    <Menu ref="menu" :model="menuItems" :popup="true" />

    <!-- Create/Edit Dialog -->
    <Dialog v-model:visible="showDialog" :header="dialogMode === 'create' ? 'Thêm Competitor' : dialogMode === 'edit' ? 'Sửa Competitor' : 'Chi tiết Competitor'" :style="{ width: '800px' }" modal>
      <div class="p-fluid">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="market">Market</label>
              <Dropdown v-model="formData.market" :options="marketOptions" optionLabel="label" optionValue="value" placeholder="Chọn market" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="hotel_name">Tên khách sạn</label>
              <InputText v-model="formData.hotel_name" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="hotel_link">Link khách sạn</label>
              <InputText v-model="formData.hotel_link" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="room_type">Tên hạng phòng</label>
              <InputText v-model="formData.room_type" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="num_people">Số lượng người</label>
              <InputNumber v-model="formData.num_people" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="bed_info">Giường</label>
              <InputText v-model="formData.bed_info" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="room_area">Diện tích phòng</label>
              <InputText v-model="formData.room_area" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="room_choices">Các lựa chọn</label>
              <Textarea v-model="formData.room_choices" rows="2" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="popular_facilities">Các tiện nghi được ưa chuộng nhất</label>
              <Textarea v-model="formData.popular_facilities" rows="2" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="cluster">Cluster</label>
              <Dropdown v-model="formData.cluster" :options="clusterOptions" optionLabel="label" optionValue="value" placeholder="Chọn cluster" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="competitor_level">Level đối thủ</label>
              <Dropdown v-model="formData.competitor_level" :options="competitorLevelOptions" optionLabel="label" optionValue="value" placeholder="Chọn level" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="breakfast_included">Giá bao gồm bữa sáng</label>
              <Dropdown v-model="formData.breakfast_included" :options="breakfastOptions" optionLabel="label" optionValue="value" placeholder="Chọn" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="room_group">Nhóm hạng phòng</label>
              <Dropdown v-model="formData.room_group" :options="roomGroupOptions" optionLabel="label" optionValue="value" placeholder="Chọn nhóm" :disabled="dialogMode === 'view'" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="level">Level</label>
              <Dropdown v-model="formData.level" :options="levelOptions" optionLabel="label" optionValue="value" placeholder="Chọn level" :disabled="dialogMode === 'view'" />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Đóng" icon="pi pi-times" @click="showDialog = false" severity="secondary" text />
        <Button v-if="dialogMode !== 'view'" label="Lưu" icon="pi pi-check" @click="saveCompetitor" :loading="saving" severity="primary" />
      </template>
    </Dialog>

    <!-- Import Errors Dialog -->
    <Dialog v-model:visible="showErrorDialog" header="Lỗi Import" :style="{ width: '900px' }" modal>
      <DataTable :value="importErrors" scrollable scrollHeight="400px" responsiveLayout="scroll">
        <Column field="row" header="Hàng" style="width: 80px"></Column>
        <Column field="error" header="Lỗi" style="min-width: 300px"></Column>
      </DataTable>
      <template #footer>
        <Button label="Đóng" icon="pi pi-times" @click="showErrorDialog = false" severity="secondary" />
      </template>
    </Dialog>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Menu from 'primevue/menu'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const toast = useToast()
const confirm = useConfirm()
const router = useRouter()

interface CompetitorData {
  id?: number
  hotel_name?: string
  hotel_link?: string
  room_type?: string
  num_people?: number
  bed_info?: string
  room_area?: string
  room_choices?: string
  popular_facilities?: string
  market?: string
  cluster?: string
  competitor_level?: string
  breakfast_included?: string
  room_group?: string
  level?: string
}

const competitors = ref<CompetitorData[]>([])
const loading = ref(false)
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('create')
const saving = ref(false)
const fileInput = ref<HTMLInputElement>()
const showErrorDialog = ref(false)
const importErrors = ref<Array<{ row: number, error: string }>>([])
const menu = ref()
const selectedCompetitor = ref<CompetitorData | null>(null)

const menuItems = ref([
  {
    label: 'Xem chi tiết',
    icon: 'pi pi-eye',
    command: () => viewCompetitor()
  },
  {
    label: 'Chỉnh sửa',
    icon: 'pi pi-pencil',
    command: () => editCompetitor()
  },
  {
    separator: true
  },
  {
    label: 'Xóa',
    icon: 'pi pi-trash',
    class: 'text-danger',
    command: () => deleteCompetitor()
  }
])

const formData = ref<CompetitorData>({
  hotel_name: '',
  hotel_link: '',
  room_type: '',
  num_people: undefined,
  bed_info: '',
  room_area: '',
  room_choices: '',
  popular_facilities: '',
  market: '',
  cluster: '',
  competitor_level: '',
  breakfast_included: '',
  room_group: '',
  level: ''
})

const filters = ref({
  hotel_name: { value: null, matchMode: 'contains' },
  hotel_link: { value: null, matchMode: 'contains' },
  room_type: { value: null, matchMode: 'contains' },
  market: { value: null, matchMode: 'in' },
  cluster: { value: null, matchMode: 'in' },
  competitor_level: { value: null, matchMode: 'in' },
  breakfast_included: { value: null, matchMode: 'in' },
  room_group: { value: null, matchMode: 'in' },
  level: { value: null, matchMode: 'in' }
})

// Config options - will be loaded from API
const marketOptions = ref<Array<{ label: string, value: string }>>([])
const clusterOptions = ref<Array<{ label: string, value: string }>>([])
const competitorLevelOptions = ref<Array<{ label: string, value: string }>>([])
const breakfastOptions = ref<Array<{ label: string, value: string }>>([])
const roomGroupOptions = ref<Array<{ label: string, value: string }>>([])
const levelOptions = ref<Array<{ label: string, value: string }>>([])

async function loadConfigOptions() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/config`)
    const configs = response.data

    marketOptions.value = (configs.market || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
    clusterOptions.value = (configs.cluster || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
    competitorLevelOptions.value = (configs.competitor_level || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
    breakfastOptions.value = (configs.breakfast || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
    roomGroupOptions.value = (configs.room_group || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
    levelOptions.value = (configs.level || []).map((c: any) => ({ label: c.config_value, value: c.config_key }))
  } catch (error) {
    console.error('Failed to load config options:', error)
  }
}

function getConfigLabel(options: Array<{ label: string, value: string }>, value: string | undefined): string {
  if (!value) return ''
  const option = options.find(o => o.value === value)
  return option ? option.label : value
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function loadCompetitors() {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/competitors`, {
      params: { limit: 1000 }
    })
    competitors.value = response.data.data
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể tải danh sách competitor',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  dialogMode.value = 'create'
  formData.value = {
    hotel_name: '',
    hotel_link: '',
    room_type: '',
    num_people: undefined,
    bed_info: '',
    room_area: '',
    room_choices: '',
    popular_facilities: '',
    market: '',
    cluster: '',
    competitor_level: '',
    breakfast_included: '',
    room_group: '',
    level: ''
  }
  showDialog.value = true
}

function toggleMenu(event: Event, competitor: CompetitorData) {
  selectedCompetitor.value = competitor
  menu.value.toggle(event)
}

function viewCompetitor() {
  if (selectedCompetitor.value?.id) {
    router.push({ name: 'competitor-view', params: { id: selectedCompetitor.value.id } })
  }
}

function editCompetitor() {
  if (selectedCompetitor.value?.id) {
    router.push({ name: 'competitor-edit', params: { id: selectedCompetitor.value.id } })
  }
}

async function deleteCompetitor() {
  if (!selectedCompetitor.value) return

  confirm.require({
    message: `Bạn có chắc chắn muốn xóa competitor "${selectedCompetitor.value.hotel_name}"?`,
    header: 'Xác nhận xóa',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Xóa',
    rejectLabel: 'Hủy',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await axios.delete(`${API_BASE_URL}/api/competitors/${selectedCompetitor.value?.id}`)
        toast.add({
          severity: 'success',
          summary: 'Thành công',
          detail: 'Đã xóa competitor',
          life: 3000
        })
        await loadCompetitors()
      } catch (error: any) {
        toast.add({
          severity: 'error',
          summary: 'Lỗi',
          detail: 'Không thể xóa competitor',
          life: 3000
        })
      }
    }
  })
}

async function saveCompetitor() {
  if (!formData.value.hotel_name || !formData.value.room_type) {
    toast.add({
      severity: 'warn',
      summary: 'Cảnh báo',
      detail: 'Vui lòng nhập tên khách sạn và tên hạng phòng',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await axios.post(`${API_BASE_URL}/api/competitors`, formData.value)
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã thêm competitor',
        life: 3000
      })
    } else {
      await axios.put(`${API_BASE_URL}/api/competitors/${formData.value.id}`, formData.value)
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã cập nhật competitor',
        life: 3000
      })
    }
    showDialog.value = false
    await loadCompetitors()
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể lưu competitor',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  loading.value = true
  try {
    const response = await axios.post(`${API_BASE_URL}/api/competitors/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    const message = response.data.skipped > 0 
      ? `Đã tạo: ${response.data.created}, Cập nhật: ${response.data.updated}, Bỏ qua: ${response.data.skipped}`
      : `Đã tạo: ${response.data.created}, Cập nhật: ${response.data.updated}`

    toast.add({
      severity: response.data.errors && response.data.errors.length > 0 ? 'warn' : 'success',
      summary: 'Import hoàn tất',
      detail: message,
      life: 5000
    })

    if (response.data.errors && response.data.errors.length > 0) {
      // Errors now come as objects with row and error fields
      importErrors.value = response.data.errors.map((err: any) => {
        if (typeof err === 'object' && err.row && err.error) {
          return err
        } else if (typeof err === 'string') {
          // Fallback for old format
          const match = err.match(/Row (\d+): (.+)/)
          if (match) {
            return { row: parseInt(match[1]), error: match[2] }
          }
          return { row: 0, error: err }
        }
        return { row: 0, error: String(err) }
      })
      showErrorDialog.value = true
    }

    await loadCompetitors()
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể import file',
      life: 3000
    })
  } finally {
    loading.value = false
    // Reset file input
    target.value = ''
  }
}

onMounted(async () => {
  await loadConfigOptions()
  await loadCompetitors()
})
</script>

<style scoped>
.competitor-list-view {
  padding: 2rem 0;
}

:deep(.p-column-filter) {
  width: 100%;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  white-space: normal;
  word-wrap: break-word;
}

:deep(.text-primary) {
  color: #3b82f6;
  cursor: pointer;
}

:deep(.text-primary:hover) {
  color: #2563eb;
}
</style>

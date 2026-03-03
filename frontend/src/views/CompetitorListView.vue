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
          responsiveLayout="scroll"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
          :rowsPerPageOptions="[10,20,50]"
          filterDisplay="row"
          v-model:filters="filters"
        >
          <Column field="hotel_name" header="Tên KS" style="min-width: 200px">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Tìm tên KS" />
            </template>
          </Column>
          <Column field="market" header="Market" style="width: 100px"></Column>
          <Column field="cluster" header="Cluster" style="width: 120px"></Column>
          <Column field="competitor_level" header="Level ĐT" style="width: 100px"></Column>
          <Column header="Thao tác" style="width: 150px">
            <template #body="slotProps">
              <div style="display: flex; gap: 0.75rem; align-items: center;">
                <Button icon="pi pi-eye" class="p-button-sm" severity="primary" @click="viewCompetitor(slotProps.data)" v-tooltip.top="'Xem'" />
                <Button icon="pi pi-pencil" class="p-button-sm" severity="primary" @click="editCompetitor(slotProps.data)" v-tooltip.top="'Sửa'" />
                <Button icon="pi pi-trash" class="p-button-sm p-button-danger" @click="deleteCompetitor(slotProps.data)" v-tooltip.top="'Xóa'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

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

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const toast = useToast()

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
  hotel_name: { value: null, matchMode: 'contains' }
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

function viewCompetitor(competitor: CompetitorData) {
  dialogMode.value = 'view'
  formData.value = { ...competitor }
  showDialog.value = true
}

function editCompetitor(competitor: CompetitorData) {
  dialogMode.value = 'edit'
  formData.value = { ...competitor }
  showDialog.value = true
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

async function deleteCompetitor(competitor: CompetitorData) {
  if (!confirm(`Xóa competitor "${competitor.hotel_name}"?`)) return

  try {
    await axios.delete(`${API_BASE_URL}/api/competitors/${competitor.id}`)
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

    toast.add({
      severity: 'success',
      summary: 'Import thành công',
      detail: `Đã tạo: ${response.data.created}, Cập nhật: ${response.data.updated}`,
      life: 5000
    })

    if (response.data.errors && response.data.errors.length > 0) {
      console.error('Import errors:', response.data.errors)
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
</style>

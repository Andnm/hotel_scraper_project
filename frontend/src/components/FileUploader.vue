<template>
  <div class="file-uploader">
    <div class="upload-section">
      <div class="two-columns">
        <!-- Excel Upload Section -->
        <div class="column">
          <label class="section-label">📂 Tải lên file Excel</label>
          <FileUpload
            ref="fileUploadRef"
            mode="basic"
            name="file"
            accept=".xlsx,.xls"
            :maxFileSize="10000000"
            :auto="false"
            chooseLabel="Chọn file Excel"
            @select="handleFileSelect"
            style="margin-top: 0.75rem"
            :pt="{
              chooseButton: {
                root: { class: 'p-button-primary' }
              }
            }"
          />

          <div v-if="selectedFile" class="file-info-card">
           
            <div class="checkbox-wrapper">
              <Checkbox 
                v-model="saveForReuse"
                inputId="saveForReuse"
                binary
              />
              <label for="saveForReuse" class="checkbox-label">Lưu file này để sử dụng lại sau</label>
            </div>

            <div v-if="saveForReuse" style="margin-top: 0.75rem">
              <InputText
                v-model="sourceName"
                placeholder="Đặt tên cho nguồn dữ liệu này"
                class="w-full"
              />
            </div>

            <Button 
              label="Tải lên và xử lý" 
              icon="pi pi-upload"
              class="w-full"
              style="margin-top: 1rem"
              @click="uploadFile"
              :loading="uploading"
              :disabled="uploading"
            />
          </div>
        </div>

        <!-- Google Sheets Section -->
        <div class="column">
          <label class="section-label">🔗 Import từ Google Sheets</label>
          <InputText
            v-model="googleSheetUrl"
            placeholder="Nhập URL Google Sheet (ví dụ: https://docs.google.com/spreadsheets/d/...)"
            class="w-full"
            style="margin-top: 0.75rem"
          />

          <div v-if="googleSheetUrl" class="file-info-card">
            <div class="checkbox-wrapper">
              <Checkbox 
                v-model="saveSheetForReuse"
                inputId="saveSheetForReuse"
                binary
              />
              <label for="saveSheetForReuse" class="checkbox-label">Lưu nguồn này để sử dụng lại sau</label>
            </div>

            <div v-if="saveSheetForReuse" style="margin-top: 0.75rem">
              <InputText
                v-model="sheetSourceName"
                placeholder="Đặt tên cho nguồn Google Sheet này"
                class="w-full"
              />
            </div>

            <Button 
              label="Import từ Google Sheets" 
              icon="pi pi-link"
              class="w-full"
              style="margin-top: 1rem"
              @click="importFromGoogleSheet"
              :loading="uploading"
              :disabled="uploading"
            />
          </div>
        </div>
      </div>

      <div class="divider">
        <span>HOẶC</span>
      </div>

      <SavedSourcesManager @source-selected="handleSourceSelected" />
    </div>

    <div v-if="uploading" class="loading-section">
      <ProgressBar mode="indeterminate" />
      <p style="text-align: center; margin-top: 0.5rem; color: var(--text-color-secondary)">Đang xử lý file...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import Checkbox from 'primevue/checkbox'
import axios from 'axios'
import SavedSourcesManager from './SavedSourcesManager.vue'

interface UploadResult {
  markets: string[]
  links: any[]
  total_links: number
  source_id?: number
}

const emit = defineEmits<{
  (e: 'data-loaded', data: UploadResult): void
}>()

const toast = useToast()
const fileUploadRef = ref()
const selectedFile = ref<File | null>(null)
const saveForReuse = ref(false)
const sourceName = ref('')
const uploading = ref(false)

// Google Sheet state
const googleSheetUrl = ref('')
const saveSheetForReuse = ref(false)
const sheetSourceName = ref('')

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function handleFileSelect(event: any) {
  selectedFile.value = event.files[0] || null
  if (selectedFile.value) {
    sourceName.value = selectedFile.value.name.replace(/\.(xlsx|xls)$/i, '')
  }
}

async function uploadFile() {
  if (!selectedFile.value) return

  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('save_for_reuse', saveForReuse.value ? 'true' : 'false')
    
    if (saveForReuse.value && sourceName.value) {
      formData.append('name', sourceName.value)
    }

    const response = await axios.post(`${API_URL}/sources/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: `Đã tải ${response.data.total_links} links từ ${response.data.markets.length} markets`,
        life: 3000
      })

      emit('data-loaded', {
        markets: response.data.markets,
        links: response.data.links,
        total_links: response.data.total_links,
        source_id: response.data.source_id
      })

      // Reset form
      selectedFile.value = null
      saveForReuse.value = false
      sourceName.value = ''
      if (fileUploadRef.value) {
        fileUploadRef.value.clear()
      }
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể tải file lên',
      life: 5000
    })
  } finally {
    uploading.value = false
  }
}

async function importFromGoogleSheet() {
  if (!googleSheetUrl.value) return

  uploading.value = true
  
  try {
    const response = await axios.post(`${API_URL}/sources/import-google-sheet`, {
      url: googleSheetUrl.value,
      save_for_reuse: saveSheetForReuse.value,
      name: saveSheetForReuse.value ? sheetSourceName.value : undefined
    })

    if (response.data.success) {
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: `Đã import ${response.data.total_links} links từ ${response.data.markets.length} markets`,
        life: 3000
      })

      emit('data-loaded', {
        markets: response.data.markets,
        links: response.data.links,
        total_links: response.data.total_links,
        source_id: response.data.source_id
      })

      // Reset form
      googleSheetUrl.value = ''
      saveSheetForReuse.value = false
      sheetSourceName.value = ''
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.response?.data?.detail || 'Không thể import từ Google Sheet',
      life: 5000
    })
  } finally {
    uploading.value = false
  }
}

async function handleSourceSelected(sourceId: number) {
  uploading.value = true
  
  try {
    const response = await axios.get(`${API_URL}/sources/${sourceId}`)
    
    toast.add({
      severity: 'success',
      summary: 'Đã tải',
      detail: `Đã tải ${response.data.total_links} links từ nguồn đã lưu`,
      life: 3000
    })

    emit('data-loaded', {
      markets: response.data.markets,
      links: response.data.links,
      total_links: response.data.total_links,
      source_id: sourceId
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể tải dữ liệu từ nguồn đã lưu',
      life: 5000
    })
  } finally {
    uploading.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: start;
  position: relative;
}

.two-columns::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--surface-300);
  transform: translateX(-50%);
}

.column {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 0 1rem;
}

@media (max-width: 768px) {
  .two-columns {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .two-columns::before {
    display: none;
  }
  
  .column {
    padding: 0;
  }
}

.section-label {
  font-weight: 600;
  color: var(--text-color);
  display: block;
  margin-bottom: 0.75rem;
}

.file-info-card {
  padding: 1.25rem;
  padding-top: 0px;
  background: var(--surface-50);
  border: 2px solid var(--surface-200);
  border-radius: 8px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
}

.checkbox-label {
  cursor: pointer;
  user-select: none;
  color: var(--text-color);
  font-size: 0.9rem;
}

.divider {
  text-align: center;
  margin: 2rem 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--surface-300);
}

.divider span {
  background: var(--surface-0);
  padding: 0 1rem;
  position: relative;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  font-weight: 600;
}

.text-center {
  text-align: center;
}

.loading-section {
  margin-top: 2rem;
}

/* Override FileUpload button color to blue */
:deep(.p-fileupload-choose) {
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%) !important;
  border-color: #1e88e5 !important;
}

:deep(.p-fileupload-choose:hover) {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%) !important;
  border-color: #1565c0 !important;
}
</style>

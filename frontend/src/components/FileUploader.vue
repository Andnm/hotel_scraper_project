<template>
  <div class="file-uploader">
    <div class="upload-section">
      <div class="p-field">
        <label for="file">📂 Tải lên file Excel</label>
        <FileUpload
          mode="basic"
          name="file"
          accept=".xlsx,.xls"
          :maxFileSize="10000000"
          :auto="true"
          chooseLabel="Chọn file Excel"
          @select="handleFileSelect"
          class="mt-2"
        />
      </div>

      <div class="divider">
        <span>HOẶC</span>
      </div>

      <div class="p-field">
        <label for="url">🌐 Nhập link Google Sheets</label>
        <div class="flex gap-2 mt-2">
          <InputText
            id="url"
            v-model="googleSheetsUrl"
            placeholder="https://docs.google.com/spreadsheets/d/..."
            class="flex-1"
          />
          <Button 
            label="Tải" 
            icon="pi pi-download"
            @click="handleGoogleSheets"
            :disabled="!googleSheetsUrl || loading"
            :loading="loading"
          />
        </div>
        <small class="text-muted">Link phải ở chế độ "Anyone with the link can view"</small>
      </div>
    </div>

    <div v-if="loading" class="loading-section">
      <ProgressBar mode="indeterminate" />
      <p class="text-center mt-2">Đang tải dữ liệu...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { LinkInfo } from '@/types'
import * as XLSX from 'xlsx'

const emit = defineEmits<{
  (e: 'links-extracted', links: LinkInfo[]): void
}>()

const toast = useToast()
const googleSheetsUrl = ref('')
const loading = ref(false)

async function handleFileSelect(event: any) {
  const file = event.files[0]
  if (!file) return

  loading.value = true
  
  try {
    const data = await readExcelFile(file)
    const links = extractLinksFromData(data)
    
    if (links.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Cảnh báo',
        detail: 'Không tìm thấy link Booking.com trong file',
        life: 3000
      })
    } else {
      emit('links-extracted', links)
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: `Lỗi đọc file: ${error.message}`,
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

async function handleGoogleSheets() {
  if (!googleSheetsUrl.value) return

  loading.value = true
  
  try {
    // TODO: Implement Google Sheets loading
    toast.add({
      severity: 'warn',
      summary: 'Chức năng',
      detail: 'Tính năng Google Sheets đang được phát triển',
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message,
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

function readExcelFile(file: File): Promise<any[][]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e: any) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })
        resolve(jsonData as any[][])
      } catch (error) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(reader.error)
    reader.readAsArrayBuffer(file)
  })
}

function extractLinksFromData(data: any[][]): LinkInfo[] {
  const links: LinkInfo[] = []
  
  // Scan first 3 columns
  for (let rowIdx = 0; rowIdx < data.length; rowIdx++) {
    const row = data[rowIdx]
    
    for (let colIdx = 0; colIdx < Math.min(3, row.length); colIdx++) {
      const cell = row[colIdx]
      
      if (!cell) continue
      
      const cellStr = String(cell).trim()
      
      // Check if contains booking.com link
      if (cellStr.includes('booking.com/hotel/')) {
        const isValid = isBookingLink(cellStr)
        
        links.push({
          row: rowIdx + 1,
          col: String.fromCharCode(65 + colIdx),
          link: cellStr,
          cell_value: cellStr.substring(0, 100),
          is_valid: isValid,
          note: isValid ? '' : '⚠️ Link không hợp lệ'
        })
      }
    }
  }
  
  return links
}

function isBookingLink(text: string): boolean {
  if (!text) return false
  const str = text.toLowerCase().trim()
  return str.includes('booking.com/hotel/') && (str.startsWith('http://') || str.startsWith('https://'))
}
</script>

<style scoped>
.file-uploader {
  padding: 1rem;
}

.upload-section {
  max-width: 800px;
}

.p-field {
  margin-bottom: 1.5rem;
}

.p-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
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
  background: #dee2e6;
}

.divider span {
  background: white;
  padding: 0 1rem;
  position: relative;
  color: #6c757d;
  font-size: 0.875rem;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.gap-2 {
  gap: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.text-muted {
  color: #6c757d;
  font-size: 0.875rem;
}

.text-center {
  text-align: center;
}

.loading-section {
  margin-top: 2rem;
}
</style>

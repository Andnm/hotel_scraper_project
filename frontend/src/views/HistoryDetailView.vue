<template>
  <div class="history-detail-view">
    <Card>
      <template #title>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <Button icon="pi pi-arrow-left" text @click="router.back()" class="mr-2" />
            <span>Chi tiết lịch sử cào - ID: {{ route.params.id }}</span>
          </div>
          <div style="display: flex; gap: 1rem;">
            <Button label="Export Excel" icon="pi pi-file-excel" @click="handleExportExcel" severity="success" />
            <Button label="Get API" icon="pi pi-bolt" @click="copyApiLink" outlined />
          </div>
        </div>
      </template>
      <template #content>
        <div v-if="loading" class="text-center py-5">
          <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        </div>
        <div v-else>
          <!-- History Info -->
          <div v-if="historyStore.currentHistory" class="history-info-compact mb-3">
            <div class="info-item">
              <span class="info-label">NGUỒN</span>
              <Tag :severity="getSourceSeverity(historyStore.currentHistory.source)">
                {{ historyStore.currentHistory.source.toUpperCase() }}
              </Tag>
            </div>
            <div class="info-divider"></div>
            <div class="info-item">
              <span class="info-label">LOẠI CÀO</span>
              <Tag :severity="historyStore.currentHistory.scrape_type === 'info' ? 'info' : 'warning'">
                {{ historyStore.currentHistory.scrape_type === 'info' ? 'Thông tin' : 'Cào giá' }}
              </Tag>
            </div>
            <div class="info-divider"></div>
            <div class="info-item">
              <span class="info-label">TỔNG RECORDS</span>
              <span class="info-value">{{ historyStore.currentHistory.total_records }}</span>
            </div>
            <div class="info-divider"></div>
            <div class="info-item">
              <span class="info-label">NGÀY CÀO</span>
              <span class="info-value">{{ formatDate(historyStore.currentHistory.crawl_date) }}</span>
            </div>
            <div class="info-divider" v-if="historyStore.currentHistory.check_in"></div>
            <div class="info-item" v-if="historyStore.currentHistory.check_in">
              <span class="info-label">CHECK-IN</span>
              <span class="info-value" style="color: #10b981">{{ formatDate(historyStore.currentHistory.check_in) }}</span>
            </div>
            <div class="info-divider" v-if="historyStore.currentHistory.check_out"></div>
            <div class="info-item" v-if="historyStore.currentHistory.check_out">
              <span class="info-label">CHECK-OUT</span>
              <span class="info-value" style="color: #ef4444">{{ formatDate(historyStore.currentHistory.check_out) }}</span>
            </div>
          </div>

          <!-- Data Table -->
          <DataTable :value="historyStore.currentHistoryData" scrollable scrollHeight="600px" :loading="loadingData"
            responsiveLayout="scroll" showGridlines stripedRows paginator :rows="20"
            :rowsPerPageOptions="[20, 50, 100]">
            
            <!-- Info Mode Columns -->
            <template v-if="historyStore.currentHistory?.scrape_type === 'info'">
              <Column field="hotel_name" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
              <Column field="room_type" header="Loại phòng" :style="{ minWidth: '200px' }"></Column>
              <Column field="num_people" header="Số người" :style="{ width: '90px' }"></Column>
              <Column field="bed_info" header="Giường" :style="{ minWidth: '150px' }"></Column>
              <Column field="room_area" header="Diện tích" :style="{ width: '100px' }"></Column>
              <Column field="room_choices" header="Các lựa chọn" :style="{ minWidth: '250px' }">
                <template #body="slotProps">
                  <div class="text-ellipsis"
                    v-tooltip.top="slotProps.data.options?.facilities || slotProps.data.room_choices"
                    style="cursor: help;">
                    {{ slotProps.data.options?.facilities || slotProps.data.room_choices }}
                  </div>
                </template>
              </Column>
              <Column field="Market" header="Market" :style="{ width: '100px' }"></Column>
              <Column field="Cluster" header="Cluster" :style="{ width: '120px' }"></Column>
              <Column field="Level_doi_thu" header="Level ĐT" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Level đối thủ'] }}
                </template>
              </Column>
              <Column field="Gia_bao_gom_bua_sang" header="Bữa sáng" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Giá bao gồm bữa sáng'] }}
                </template>
              </Column>
              <Column field="Nhom_hang_phong" header="Nhóm HP" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Nhóm hạng phòng'] }}
                </template>
              </Column>
              <Column field="Level" header="Level" :style="{ width: '100px' }"></Column>
            </template>

            <!-- Price Mode Columns -->
            <template v-else>
              <Column field="hotel_name" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
              <Column field="room_type" header="Loại phòng" :style="{ minWidth: '200px' }"></Column>
              <Column field="num_people" header="Số người" :style="{ width: '90px' }"></Column>
              <Column field="price_after_discount" header="Giá sau giảm" :style="{ width: '140px' }">
                <template #body="slotProps">
                  {{ formatPrice(slotProps.data.price_after_discount) }}
                </template>
              </Column>
              <Column field="price_original" header="Giá gốc" :style="{ width: '140px' }">
                <template #body="slotProps">
                  {{ formatPrice(slotProps.data.price_original) }}
                </template>
              </Column>
              <Column field="discount_percent" header="Giảm giá" :style="{ width: '120px' }">
                <template #body="slotProps">
                  <Tag v-if="slotProps.data.discount_percent" severity="success">
                    {{ slotProps.data.discount_percent }}
                  </Tag>
                </template>
              </Column>
              <Column field="Market" header="Market" :style="{ width: '100px' }"></Column>
              <Column field="Cluster" header="Cluster" :style="{ width: '120px' }"></Column>
              <Column field="Level_doi_thu" header="Level ĐT" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Level đối thủ'] }}
                </template>
              </Column>
              <Column field="Gia_bao_gom_bua_sang" header="Bữa sáng" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Giá bao gồm bữa sáng'] }}
                </template>
              </Column>
              <Column field="Nhom_hang_phong" header="Nhóm HP" :style="{ width: '100px' }">
                <template #body="slotProps">
                  {{ slotProps.data['Nhóm hạng phòng'] }}
                </template>
              </Column>
              <Column field="Level" header="Level" :style="{ width: '100px' }"></Column>
              <Column field="hotel_link" header="Link" :style="{ width: '80px' }">
                <template #body="slotProps">
                  <a :href="slotProps.data.hotel_link" target="_blank" v-if="slotProps.data.hotel_link">
                    <Button icon="pi pi-external-link" text size="small" />
                  </a>
                </template>
              </Column>
            </template>
          </DataTable>
        </div>
      </template>
    </Card>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useHistoryStore } from '@/stores/history'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import * as XLSX from 'xlsx'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const historyStore = useHistoryStore()
const loading = ref(false)
const loadingData = ref(false)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getSourceSeverity(source: string) {
  if (source === 'agoda') return 'info'
  if (source === 'booking') return 'warning'
  return 'secondary'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN')
}

function formatPrice(price: number | null | undefined) {
  if (!price && price !== 0) return '-'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price)
}

async function loadHistoryDetail() {
  loading.value = true
  loadingData.value = true
  try {
    const historyId = Number(route.params.id)
    await historyStore.fetchHistoryDetail(historyId)
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể tải chi tiết lịch sử',
      life: 3000
    })
  } finally {
    loading.value = false
    loadingData.value = false
  }
}

async function handleExportExcel() {
  try {
    toast.add({
      severity: 'info',
      summary: 'Đang xử lý',
      detail: 'Đang tải dữ liệu và tạo file Excel...',
      life: 3000
    })

    const historyId = Number(route.params.id)
    const data = await historyStore.exportHistory(historyId)

    if (!data || data.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Thông báo',
        detail: 'Không có dữ liệu để export',
        life: 3000
      })
      return
    }

    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Data')

    const fileName = `history_${historyId}_${new Date().getTime()}.xlsx`
    XLSX.writeFile(wb, fileName)

    toast.add({
      severity: 'success',
      summary: 'Thành công',
      detail: `Đã tạo file ${fileName}`,
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể export Excel',
      life: 3000
    })
  }
}

function copyApiLink() {
  const historyId = route.params.id
  const apiUrl = `${API_BASE_URL}/api/history/public/${historyId}`
  
  navigator.clipboard.writeText(apiUrl).then(() => {
    toast.add({
      severity: 'success',
      summary: 'Đã copy',
      detail: 'Link API đã được copy vào clipboard',
      life: 3000
    })
  })
}

onMounted(async () => {
  await loadHistoryDetail()
})
</script>

<style scoped>
.history-detail-view {
  padding: 1.5rem 0;
}

.history-info-compact {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  color: white;
  flex-wrap: wrap;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
}

.info-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.3);
}

.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

:deep(.p-card) {
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

:deep(.p-card-title) {
  font-size: 1.5rem;
  font-weight: 600;
  padding: 1.5rem 1.5rem 0 1.5rem;
}

:deep(.p-card-content) {
  padding: 1.5rem;
}

:deep(.p-datatable) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.p-datatable-header) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 1rem;
}

:deep(.p-datatable-thead > tr > th) {
  background: #f1f5f9;
  color: #475569;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 1rem 0.75rem;
  border-color: #e2e8f0;
}

:deep(.p-datatable-tbody > tr > td) {
  padding: 0.875rem 0.75rem;
  border-color: #e2e8f0;
}

:deep(.p-datatable-tbody > tr:hover) {
  background: #f8fafc;
}

:deep(.p-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

:deep(.p-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
</style>

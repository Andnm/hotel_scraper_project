<template>
  <div class="history-list">
    <!-- Filters -->
    <Card class="filter-card mb-4">
      <template #content>
        <div class="filters">
          <div class="filter-item">
            <label>Nguồn</label>
            <Dropdown 
              v-model="filters.source" 
              :options="sourceOptions" 
              placeholder="Tất cả"
              class="w-full"
            />
          </div>

          <div class="filter-item">
            <label>Từ ngày</label>
            <Calendar 
              v-model="filters.dateFrom" 
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
            />
          </div>

          <div class="filter-item">
            <label>Đến ngày</label>
            <Calendar 
              v-model="filters.dateTo" 
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
            />
          </div>

          <div class="filter-item align-end">
            <Button 
              label="🔍 Tìm kiếm" 
              @click="loadHistories"
              :loading="historyStore.loading"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Histories Table -->
    <Card>
      <template #title>
        Danh sách phiên cào (Tổng: {{ historyStore.totalCount }})
      </template>
      <template #content>
        <DataTable 
          :value="historyStore.histories" 
          :loading="historyStore.loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} / {totalRecords} phiên"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column field="id" header="ID" :style="{ width: '80px' }"></Column>
          <Column field="source" header="Nguồn" :style="{ width: '120px' }">
            <template #body="slotProps">
              <Tag :severity="getSourceSeverity(slotProps.data.source)">
                {{ slotProps.data.source.toUpperCase() }}
              </Tag>
            </template>
          </Column>
          <Column field="crawl_date" header="Ngày cào" :style="{ width: '140px' }">
            <template #body="slotProps">
              {{ formatDate(slotProps.data.crawl_date) }}
            </template>
          </Column>
          <Column field="created_at" header="Thời điểm lưu" :style="{ width: '180px' }">
            <template #body="slotProps">
              {{ formatDateTime(slotProps.data.created_at) }}
            </template>
          </Column>
          <Column field="total_records" header="Records" :style="{ width: '100px' }"></Column>
          <Column field="crawl_target" header="Các ngày cần cào">
            <template #body="slotProps">
              {{ slotProps.data.crawl_target || '-' }}
            </template>
          </Column>
          <Column header="Thao tác" :style="{ width: '150px' }">
            <template #body="slotProps">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-sm p-button-info"
                  v-tooltip.top="'Xem chi tiết'"
                  @click="viewDetail(slotProps.data.id)"
                />
                <Button 
                  icon="pi pi-download" 
                  class="p-button-sm p-button-success"
                  v-tooltip.top="'Xuất Excel'"
                  @click="exportExcel(slotProps.data.id)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-sm p-button-danger"
                  v-tooltip.top="'Xóa'"
                  @click="confirmDelete(slotProps.data.id)"
                />
              </div>
            </template>
          </Column>
        </DataTable>

        <!-- Pagination -->
        <Paginator
          v-if="historyStore.totalPages > 1"
          :rows="historyStore.pageSize"
          :totalRecords="historyStore.totalCount"
          :first="(historyStore.currentPage - 1) * historyStore.pageSize"
          @page="onPageChange"
          class="mt-3"
        />
      </template>
    </Card>

    <!-- Detail Dialog -->
    <Dialog 
      v-model:visible="showDetailDialog" 
      :header="`Chi tiết phiên cào #${selectedHistoryId}`"
      :modal="true"
      :style="{ width: '90vw' }"
    >
      <div v-if="historyStore.currentHistory">
        <div class="detail-info mb-4">
          <div class="info-item">
            <strong>Ngày cào:</strong> {{ formatDate(historyStore.currentHistory.crawl_date) }}
          </div>
          <div class="info-item">
            <strong>Nguồn:</strong> {{ historyStore.currentHistory.source.toUpperCase() }}
          </div>
          <div class="info-item">
            <strong>Tổng records:</strong> {{ historyStore.currentHistory.total_records }}
          </div>
        </div>

        <DataTable 
          :value="historyStore.currentHistoryData" 
          :paginator="true"
          :rows="20"
          :rowsPerPageOptions="[20, 50, 100]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} / {totalRecords} dòng"
          responsiveLayout="scroll"
        >
          <Column field="hotel_name" header="Khách sạn"></Column>
          <Column field="room_type" header="Loại phòng"></Column>
          <Column field="price_after_discount" header="Giá">
            <template #body="slotProps">
              {{ formatPrice(slotProps.data.price_after_discount) }}
            </template>
          </Column>
          <Column field="review_score" header="Điểm"></Column>
        </DataTable>
      </div>
    </Dialog>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useHistoryStore } from '@/stores/history'

const historyStore = useHistoryStore()
const toast = useToast()
const confirm = useConfirm()

const filters = ref({
  source: 'Tất cả',
  dateFrom: null as Date | null,
  dateTo: null as Date | null
})

const sourceOptions = ['Tất cả', 'Booking', 'Agoda']
const showDetailDialog = ref(false)
const selectedHistoryId = ref<number | null>(null)

onMounted(() => {
  loadHistories()
})

async function loadHistories() {
  try {
    const dateFrom = filters.value.dateFrom 
      ? formatDateToString(filters.value.dateFrom) 
      : undefined
    const dateTo = filters.value.dateTo 
      ? formatDateToString(filters.value.dateTo) 
      : undefined
    
    await historyStore.fetchHistories(
      1,
      filters.value.source === 'Tất cả' ? undefined : filters.value.source,
      dateFrom,
      dateTo
    )
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message || 'Không thể tải lịch sử',
      life: 3000
    })
  }
}

async function viewDetail(historyId: number) {
  try {
    selectedHistoryId.value = historyId
    await historyStore.fetchHistoryDetail(historyId)
    showDetailDialog.value = true
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể tải chi tiết',
      life: 3000
    })
  }
}

function exportExcel(historyId: number) {
  toast.add({
    severity: 'info',
    summary: 'Tính năng',
    detail: 'Tính năng xuất Excel đang được phát triển',
    life: 3000
  })
}

function confirmDelete(historyId: number) {
  confirm.require({
    message: 'Bạn có chắc muốn xóa lịch sử này?',
    header: 'Xác nhận xóa',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Xóa',
    rejectLabel: 'Hủy',
    accept: () => deleteHistory(historyId)
  })
}

async function deleteHistory(historyId: number) {
  try {
    await historyStore.deleteHistory(historyId)
    toast.add({
      severity: 'success',
      summary: 'Thành công',
      detail: 'Đã xóa lịch sử',
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể xóa lịch sử',
      life: 3000
    })
  }
}

function onPageChange(event: any) {
  const page = event.page + 1
  loadHistories()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN')
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('vi-VN')
}

function formatDateToString(date: Date): string {
  if (!date) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatPrice(price: any): string {
  if (!price) return 'N/A'
  return parseFloat(price).toLocaleString('vi-VN') + ' VND'
}

function getSourceSeverity(source: string): string {
  return source === 'booking' ? 'info' : 'warning'
}
</script>

<style scoped>
.history-list {
  min-height: 400px;
}

.filter-card {
  background: #f8f9fa;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-item {
  display: flex;
  flex-direction: column;
}

.filter-item label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.align-end {
  align-items: flex-end;
}

.w-full {
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.info-item {
  font-size: 0.875rem;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>

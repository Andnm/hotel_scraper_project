<template>
  <div class="booking-tab">
    <!-- Upload Section -->
    <Card class="mb-4">
      <template #title>📂 Chọn nguồn dữ liệu</template>
      <template #content>
        <FileUploader @links-extracted="handleLinksExtracted" />
      </template>
    </Card>

    <!-- Links Display -->
    <Card v-if="scraperStore.links.length > 0" class="mb-4">
      <template #title>
        📋 Danh sách link ({{ validLinksCount }} hợp lệ, {{ invalidLinksCount }} không hợp lệ)
      </template>
      <template #content>
        <DataTable :value="scraperStore.links" :paginator="true" :rows="10" responsiveLayout="scroll">
          <Column field="row" header="Hàng" :style="{ width: '80px' }"></Column>
          <Column field="cell_value" header="Tên/Giá trị">
            <template #body="slotProps">
              {{ truncate(slotProps.data.cell_value, 60) }}
            </template>
          </Column>
          <Column field="link" header="Link">
            <template #body="slotProps">
              <a :href="slotProps.data.link" target="_blank" class="link-text">
                {{ truncate(slotProps.data.link, 80) }}
              </a>
            </template>
          </Column>
          <Column field="status" header="Trạng thái" :style="{ width: '150px' }">
            <template #body="slotProps">
              <Tag v-if="!slotProps.data.is_valid" severity="danger">❌ Không hợp lệ</Tag>
              <Tag v-else-if="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)">
                {{ slotProps.data.status }}
              </Tag>
              <Tag v-else severity="info">Chưa cào</Tag>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Date Range Picker -->
    <Card v-if="scraperStore.links.length > 0" class="mb-4">
      <template #title>📅 Chọn ngày nhận phòng và trả phòng</template>
      <template #content>
        <DateRangePicker @date-ranges-updated="handleDateRangesUpdated" />
      </template>
    </Card>

    <!-- Scrape Button -->
    <div v-if="scraperStore.links.length > 0 && scraperStore.dateRanges.length > 0" class="mb-4">
      <Button 
        label="Bắt đầu cào dữ liệu" 
        icon="pi pi-play"
        class="p-button-lg w-full"
        :disabled="scraperStore.isScraing"
        @click="startScraping"
      />
    </div>

    <!-- Progress Display -->
    <ProgressDisplay v-if="scraperStore.isScraing || scraperStore.results.length > 0" />

    <!-- Results Display -->
    <Card v-if="scraperStore.results.length > 0 && !scraperStore.isScraing" class="mb-4">
      <template #title>
        ✅ Kết quả ({{ scraperStore.successCount }} thành công, {{ scraperStore.errorCount }} lỗi)
      </template>
      <template #content>
        <DataTable :value="scraperStore.results" :paginator="true" :rows="20" responsiveLayout="scroll" scrollable scrollHeight="600px">
          <Column field="Ngày cào" header="Ngày cào" :style="{ width: '120px' }" frozen></Column>
          <Column field="Ngày cần cào" header="Ngày cần cào" :style="{ width: '180px' }"></Column>
          <Column field="Tên khách sạn" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
          <Column field="Tên hạng phòng" header="Loại phòng" :style="{ minWidth: '200px' }"></Column>
          <Column field="Giá sau giảm" header="Giá sau giảm" :style="{ width: '130px' }">
            <template #body="slotProps">
              {{ formatPrice(slotProps.data['Giá sau giảm']) }}
            </template>
          </Column>
          <Column field="Giá gốc" header="Giá gốc" :style="{ width: '130px' }">
            <template #body="slotProps">
              {{ formatPrice(slotProps.data['Giá gốc']) }}
            </template>
          </Column>
          <Column field="Số lượng review" header="Số review" :style="{ width: '100px' }"></Column>
          <Column field="Điểm review" header="Điểm" :style="{ width: '80px' }"></Column>
          <Column field="Số lượng người" header="Số người" :style="{ width: '90px' }"></Column>
          <Column field="Giường" header="Giường" :style="{ minWidth: '150px' }"></Column>
          <Column field="Diện tích phòng" header="Diện tích" :style="{ width: '100px' }"></Column>
          <Column field="Các lựa chọn" header="Các lựa chọn" :style="{ minWidth: '250px' }">
            <template #body="slotProps">
              <div style="white-space: pre-wrap;">{{ slotProps.data['Các lựa chọn'] }}</div>
            </template>
          </Column>
        </DataTable>

        <div class="mt-4 flex gap-2">
          <Button 
            label="Tải xuống Excel" 
            icon="pi pi-download"
            @click="downloadExcel"
            class="p-button-success"
          />
          <Button 
            label="💾 Lưu lịch sử" 
            icon="pi pi-save"
            @click="saveHistory"
            severity="primary"
            v-if="scraperStore.historyId === null"
          />
          <Button 
            v-else
            label="Đã lưu vào database" 
            icon="pi pi-check"
            disabled
            severity="success"
          />
        </div>
      </template>
    </Card>

    <!-- Errors Display -->
    <Card v-if="scraperStore.errors.length > 0 && !scraperStore.isScraing" class="mb-4">
      <template #title>❌ Danh sách lỗi ({{ scraperStore.errorCount }})</template>
      <template #content>
        <DataTable :value="scraperStore.errors" responsiveLayout="scroll">
          <Column field="Hàng" header="Hàng" :style="{ width: '80px' }"></Column>
          <Column field="Tên" header="Tên"></Column>
          <Column field="Link" header="Link">
            <template #body="slotProps">
              <a :href="slotProps.data.Link" target="_blank" class="link-text">
                {{ truncate(slotProps.data.Link, 80) }}
              </a>
            </template>
          </Column>
          <Column field="Lỗi" header="Lỗi"></Column>
        </DataTable>
      </template>
    </Card>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useScraperStore } from '@/stores/scraper'
import { scraperWebSocket } from '@/services/websocket'
import type { LinkInfo, DateRange } from '@/types'
import FileUploader from './FileUploader.vue'
import DateRangePicker from './DateRangePicker.vue'
import ProgressDisplay from './ProgressDisplay.vue'

const scraperStore = useScraperStore()
const toast = useToast()

const validLinksCount = computed(() => 
  scraperStore.links.filter(l => l.is_valid).length
)

const invalidLinksCount = computed(() => 
  scraperStore.links.filter(l => !l.is_valid).length
)

function handleLinksExtracted(links: LinkInfo[]) {
  scraperStore.setLinks(links)
  toast.add({
    severity: 'success',
    summary: 'Thành công',
    detail: `Tìm thấy ${links.length} link`,
    life: 3000
  })
}

function handleDateRangesUpdated(ranges: DateRange[]) {
  scraperStore.setDateRanges(ranges)
}

async function startScraping() {
  try {
    const validLinks = scraperStore.links.filter(l => l.is_valid)
    
    if (validLinks.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Cảnh báo',
        detail: 'Không có link hợp lệ để cào',
        life: 3000
      })
      return
    }

    if (scraperStore.dateRanges.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Cảnh báo',
        detail: 'Vui lòng chọn ít nhất một cặp ngày',
        life: 3000
      })
      return
    }

    scraperStore.reset()

    if (!scraperWebSocket.isConnected()) {
      await scraperWebSocket.connect()
    }

    scraperWebSocket.onMessage((data) => {
      scraperStore.updateProgress(data)

      if (data.type === 'completed') {
        toast.add({
          severity: 'success',
          summary: 'Hoàn thành',
          detail: `Đã cào xong ${data.total_success} hotels`,
          life: 5000
        })
      }
    })

    const request = {
      links: validLinks,
      date_ranges: scraperStore.dateRanges,
      source: scraperStore.selectedSource
    }

    scraperWebSocket.send(request)

    toast.add({
      severity: 'info',
      summary: 'Bắt đầu',
      detail: 'Đang kết nối và bắt đầu cào dữ liệu...',
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message || 'Không thể kết nối WebSocket',
      life: 5000
    })
  }
}

function downloadExcel() {
  // TODO: Implement Excel export
  toast.add({
    severity: 'info',
    summary: 'Tính năng',
    detail: 'Tính năng xuất Excel đang được phát triển',
    life: 3000
  })
}

function saveHistory() {
  // TODO: Implement save to database
  toast.add({
    severity: 'info',
    summary: 'Tính năng',
    detail: 'Tính năng lưu lịch sử đang được phát triển',
    life: 3000
  })
}

function truncate(text: string, length: number): string {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

function formatPrice(price: any): string {
  if (!price || price === 'N/A') return 'N/A'
  const num = parseInt(price.toString().replace(/\D/g, ''))
  return num ? num.toLocaleString('vi-VN') + ' VND' : 'N/A'
}

function getStatusSeverity(status: string): string {
  if (status.includes('✅')) return 'success'
  if (status.includes('❌')) return 'danger'
  if (status.includes('🔄')) return 'info'
  return 'info'
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 1.5rem;
}

.mt-4 {
  margin-top: 1.5rem;
}

.w-full {
  width: 100%;
}

.flex {
  display: flex;
}

.gap-2 {
  gap: 0.5rem;
}

.link-text {
  color: #3b82f6;
  text-decoration: none;
}

.link-text:hover {
  text-decoration: underline;
}
</style>

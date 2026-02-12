<template>
  <div class="booking-tab-container">
    <!-- Floating Menu Button -->
    <Button 
      icon="pi pi-bars" 
      @click="sidebarVisible = true"
      class="menu-button" 
      severity="primary"
      rounded
      aria-label="Menu"
      v-tooltip.right="'Xem quy trình'"
    />

    <!-- Sidebar Overlay -->
    <Sidebar v-model:visible="sidebarVisible" :baseZIndex="1000">
      <template #header>
        <h3 style="margin: 0; font-size: 1.1rem; color: var(--text-color)">📋 Quy trình cào dữ liệu</h3>
      </template>
      
      <div 
        v-for="step in steps" 
        :key="step.id"
        class="step-item"
        :class="{ 
          'step-active': currentStep === step.id,
          'step-completed': isStepCompleted(step.id),
          'step-disabled': !isStepAccessible(step.id)
        }"
        @click="scrollToStep(step.id)"
      >
        <div class="step-icon">
          <i v-if="isStepCompleted(step.id)" class="pi pi-check-circle" style="color: var(--green-500)"></i>
          <i v-else-if="currentStep === step.id" class="pi pi-spin pi-spinner" style="color: var(--primary-color)"></i>
          <i v-else :class="step.icon" style="color: var(--text-color-secondary)"></i>
        </div>
        <div class="step-content">
          <div class="step-number">Bước {{ step.id }}</div>
          <div class="step-title">{{ step.title }}</div>
        </div>
      </div>
    </Sidebar>

    <!-- Main Content -->
      <div class="booking-tab">
        <!-- Step 1: Upload/Load Data -->
        <Card class="mb-4" ref="step1">
          <template #title>📂 Bước 1: Chọn nguồn dữ liệu</template>
          <template #content>
            <FileUploader @data-loaded="handleDataLoaded" />
          </template>
        </Card>

        <!-- Step 2: Select Market & Scrape Type -->
        <Card v-if="markets.length > 0" class="mb-4" ref="step2">
          <template #title>⚙️ Bước 2: Hình thức cào</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <MarketSelector 
                  :markets="markets"
                  :linksByMarket="linksByMarket"
                  v-model="selectedMarket"
                />
              </div>
              <div class="col-12 md:col-6">
                <ScrapeTypeSelector v-model="scrapeType" />
              </div>
            </div>
          </template>
        </Card>

        <!-- Step 3: Links Display -->
        <Card v-if="displayLinks.length > 0" class="mb-4" ref="step3">
          <template #title>
            📋 Bước 3: Xem trước links ({{ validLinksCount }} hợp lệ, {{ invalidLinksCount }} không hợp lệ)
            <span v-if="selectedMarket" class="ml-2">
              <Tag severity="info">Market: {{ selectedMarket }}</Tag>
            </span>
          </template>
      <template #content>
        <DataTable 
          :value="displayLinks" 
          :paginator="true" 
          :rows="10" 
          :rowsPerPageOptions="[10, 25, 50, 100]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} / {totalRecords} links"
          responsiveLayout="scroll"
        >
          <Column field="row" header="Hàng" :style="{ width: '80px' }"></Column>
          <Column field="market" header="Market" :style="{ width: '120px' }">
            <template #body="slotProps">
              <Tag severity="info">{{ slotProps.data.market }}</Tag>
            </template>
          </Column>
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

    <!-- Step 4: Date Range Picker -->
    <Card v-if="displayLinks.length > 0" class="mb-4" ref="step4">
      <template #title>📅 Bước 4: Chọn ngày nhận phòng và trả phòng</template>
      <template #content>
        <DateRangePicker @date-ranges-updated="handleDateRangesUpdated" />
      </template>
    </Card>

    <!-- Step 5: Scrape Button -->
    <div v-if="displayLinks.length > 0 && scraperStore.dateRanges.length > 0" class="mb-4" ref="step5">
      <Button 
        :label="isStarting ? 'Đang kết nối...' : `Bắt đầu ${scrapeType === 'info' ? 'cào thông tin' : 'cào giá'}`"
        :icon="isStarting ? 'pi pi-spinner pi-spin' : 'pi pi-play'"
        class="p-button-lg w-full"
        :disabled="scraperStore.isScraing || isStarting"
        @click="startScraping"
      />
    </div>

    <!-- Progress Display -->
    <ProgressDisplay v-if="scraperStore.isScraing || scraperStore.results.length > 0" />

    <!-- Results Display -->
    <Card v-if="scraperStore.results.length > 0 && !scraperStore.isScraing" class="mb-4" ref="step6">
      <template #title>
        ✅ Kết quả ({{ scraperStore.successCount }} thành công, {{ scraperStore.errorCount }} lỗi)
      </template>
      <template #content>
        <DataTable 
          :value="scraperStore.results" 
          :paginator="true" 
          :rows="20" 
          :rowsPerPageOptions="[20, 50, 100, 200]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} / {totalRecords} kết quả"
          responsiveLayout="scroll" 
          scrollable 
          scrollHeight="600px"
        >
          <!-- Info Mode Columns -->
          <template v-if="scrapeType === 'info'">
            <Column field="Ngày cào" header="Ngày cào" :style="{ width: '110px' }" frozen></Column>
            <Column field="Giờ cào" header="Giờ cào" :style="{ width: '100px' }" frozen></Column>
            <Column field="Check in" header="Check in" :style="{ width: '110px' }"></Column>
            <Column field="Check out" header="Check out" :style="{ width: '110px' }"></Column>
            <Column field="Tên khách sạn" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
            <Column field="Link khách sạn" header="Link" :style="{ width: '100px' }">
              <template #body="slotProps">
                <a :href="slotProps.data['Link khách sạn']" target="_blank">
                  <Button icon="pi pi-external-link" text size="small" />
                </a>
              </template>
            </Column>
            <Column field="Số lượng review" header="Số review" :style="{ width: '100px' }"></Column>
            <Column field="Điểm review" header="Điểm" :style="{ width: '80px' }"></Column>
            <Column field="Các tiện nghi được ưa chuộng nhất" header="Tiện nghi" :style="{ minWidth: '200px' }">
              <template #body="slotProps">
                <div 
                  class="text-ellipsis" 
                  v-tooltip.top="slotProps.data['Các tiện nghi được ưa chuộng nhất']"
                  style="cursor: help;"
                >
                  {{ slotProps.data['Các tiện nghi được ưa chuộng nhất'] }}
                </div>
              </template>
            </Column>
            <Column field="Tên hạng phòng" header="Loại phòng" :style="{ minWidth: '200px' }"></Column>
            <Column field="Số lượng người" header="Số người" :style="{ width: '90px' }"></Column>
            <Column field="Giường" header="Giường" :style="{ minWidth: '150px' }"></Column>
            <Column field="Diện tích phòng" header="Diện tích" :style="{ width: '100px' }"></Column>
            <Column field="Các lựa chọn" header="Các lựa chọn" :style="{ minWidth: '250px' }">
              <template #body="slotProps">
                <div 
                  class="text-ellipsis" 
                  v-tooltip.top="slotProps.data['Các lựa chọn']"
                  style="cursor: help;"
                >
                  {{ slotProps.data['Các lựa chọn'] }}
                </div>
              </template>
            </Column>
          </template>

          <!-- Price Mode Columns -->
          <template v-else>
            <Column field="Ngày cào" header="Ngày cào" :style="{ width: '110px' }" frozen></Column>
            <Column field="Giờ cào" header="Giờ cào" :style="{ width: '100px' }" frozen></Column>
            <Column field="Check in" header="Check in" :style="{ width: '110px' }"></Column>
            <Column field="Check out" header="Check out" :style="{ width: '110px' }"></Column>
            <Column field="Tên khách sạn" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
            <Column field="Tên hạng phòng" header="Loại phòng" :style="{ minWidth: '200px' }"></Column>
            <Column field="Số lượng người" header="Số người" :style="{ width: '90px' }"></Column>
            <Column field="Giá sau giảm" header="Giá sau giảm" :style="{ width: '140px' }">
              <template #body="slotProps">
                {{ formatPrice(slotProps.data['Giá sau giảm']) }}
              </template>
            </Column>
            <Column field="Giá gốc" header="Giá gốc" :style="{ width: '140px' }">
              <template #body="slotProps">
                {{ formatPrice(slotProps.data['Giá gốc']) }}
              </template>
            </Column>
            <Column field="Giảm giá" header="Giảm giá" :style="{ width: '100px' }">
              <template #body="slotProps">
                <Tag v-if="slotProps.data['Giảm giá']" severity="success">
                  {{ slotProps.data['Giảm giá'] }}
                </Tag>
              </template>
            </Column>
          </template>
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

    </div>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useScraperStore } from '@/stores/scraper'
import { scraperWebSocket } from '@/services/websocket'
import type { LinkInfo, DateRange } from '@/types'
import Sidebar from 'primevue/sidebar'
import FileUploader from './FileUploader.vue'
import DateRangePicker from './DateRangePicker.vue'
import ProgressDisplay from './ProgressDisplay.vue'
import SavedSourcesManager from './SavedSourcesManager.vue'
import ScrapeTypeSelector from './ScrapeTypeSelector.vue'
import MarketSelector from './MarketSelector.vue'

const scraperStore = useScraperStore()
const toast = useToast()

// Sidebar visibility
const sidebarVisible = ref(false)

// Loading state for immediate UI feedback
const isStarting = ref(false)

// Sidebar navigation
const currentStep = ref(1)
const step1 = ref()
const step2 = ref()
const step3 = ref()
const step4 = ref()
const step5 = ref()
const step6 = ref()

const steps = [
  { id: 1, title: 'Chọn nguồn dữ liệu', icon: 'pi pi-folder' },
  { id: 2, title: 'Hình thức cào', icon: 'pi pi-cog' },
  { id: 3, title: 'Xem trước links', icon: 'pi pi-list' },
  { id: 4, title: 'Chọn ngày', icon: 'pi pi-calendar' },
  { id: 5, title: 'Bắt đầu cào', icon: 'pi pi-play' },
  { id: 6, title: 'Kết quả', icon: 'pi pi-check' }
]

function isStepCompleted(stepId: number): boolean {
  if (stepId === 1) return allLinks.value.length > 0
  if (stepId === 2) return markets.value.length > 0 && selectedMarket.value !== null
  if (stepId === 3) return displayLinks.value.length > 0
  if (stepId === 4) return scraperStore.dateRanges.length > 0
  if (stepId === 5) return scraperStore.results.length > 0 || scraperStore.isScraing
  if (stepId === 6) return scraperStore.results.length > 0 && !scraperStore.isScraing
  return false
}

function isStepAccessible(stepId: number): boolean {
  if (stepId === 1) return true
  if (stepId === 2) return allLinks.value.length > 0
  if (stepId === 3) return markets.value.length > 0
  if (stepId === 4) return displayLinks.value.length > 0
  if (stepId === 5) return scraperStore.dateRanges.length > 0
  if (stepId === 6) return scraperStore.results.length > 0
  return false
}

function scrollToStep(stepId: number) {
  if (!isStepAccessible(stepId)) return
  
  currentStep.value = stepId
  const stepRefs: Record<number, any> = {
    1: step1,
    2: step2,
    3: step3,
    4: step4,
    5: step5,
    6: step6
  }
  
  const element = stepRefs[stepId]?.value?.$el || stepRefs[stepId]?.value
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    // Close sidebar after clicking a step
    sidebarVisible.value = false
  }
}

// New state for markets and scrape type
const allLinks = ref<LinkInfo[]>([])
const markets = ref<string[]>([])
const selectedMarket = ref<string | null>(null)
const scrapeType = ref<'info' | 'price'>('info')
const linksByMarket = ref<Record<string, number>>({})
const currentSourceId = ref<number | null>(null)

// Computed links based on selected market
const displayLinks = computed(() => {
  if (!selectedMarket.value || selectedMarket.value === 'all') {
    return allLinks.value
  }
  return allLinks.value.filter(link => link.market === selectedMarket.value)
})

const validLinksCount = computed(() => 
  displayLinks.value.filter(l => l.is_valid).length
)

const invalidLinksCount = computed(() => 
  displayLinks.value.filter(l => !l.is_valid).length
)

function handleDataLoaded(data: { markets: string[], links: LinkInfo[], total_links: number, source_id?: number }) {
  // Store all links and markets
  allLinks.value = data.links
  markets.value = data.markets
  currentSourceId.value = data.source_id || null
  
  // Calculate links by market
  linksByMarket.value = {}
  markets.value.forEach(market => {
    linksByMarket.value[market] = data.links.filter(l => l.market === market).length
  })
  
  // Reset selection
  selectedMarket.value = markets.value.length > 1 ? null : markets.value[0]
  
  // Update store links (for backward compatibility)
  scraperStore.setLinks(data.links)
  
  toast.add({
    severity: 'success',
    summary: 'Thành công',
    detail: `Tìm thấy ${data.total_links} link từ ${markets.value.length} market(s)`,
    life: 3000
  })
}

function handleDateRangesUpdated(ranges: DateRange[]) {
  scraperStore.setDateRanges(ranges)
}

async function startScraping() {
  try {
    const validLinks = displayLinks.value.filter(l => l.is_valid)
    
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

    // Set loading state immediately for better UX
    isStarting.value = true
    scraperStore.reset()

    if (!scraperWebSocket.isConnected()) {
      await scraperWebSocket.connect()
    }

    scraperWebSocket.onMessage((data) => {
      scraperStore.updateProgress(data)
      
      // Clear starting state when scraping actually begins or completes
      if (data.type === 'started' || data.type === 'completed') {
        isStarting.value = false
      }

      if (data.type === 'completed') {
        toast.add({
          severity: 'success',
          summary: 'Hoàn thành',
          detail: `Đã cào xong ${data.total_success} hotels (Mode: ${scrapeType.value === 'info' ? 'Thông tin' : 'Giá'})`,
          life: 5000
        })
      }
    })

    const request = {
      links: validLinks,
      date_ranges: scraperStore.dateRanges,
      source: scraperStore.selectedSource,
      scrape_type: scrapeType.value,
      market: selectedMarket.value === 'all' ? null : selectedMarket.value
    }

    scraperWebSocket.send(request)

    const modeText = scrapeType.value === 'info' ? 'thông tin' : 'giá'
    const marketText = selectedMarket.value && selectedMarket.value !== 'all' 
      ? ` (Market: ${selectedMarket.value})` 
      : ''
    
    toast.add({
      severity: 'info',
      summary: 'Bắt đầu',
      detail: `Đang cào ${modeText}${marketText}...`,
      life: 3000
    })
  } catch (error: any) {
    // Clear starting state on error
    isStarting.value = false
    
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message || 'Không thể kết nối WebSocket',
      life: 5000
    })
  }
}

function downloadExcel() {
  try {
    import('xlsx').then((XLSX) => {
      let filteredResults = [];

      if (scrapeType.value === 'info') {
        const columns = [
          'Ngày cào', 'Giờ cào', 'Check in', 'Check out', 
          'Tên khách sạn', 'Link khách sạn', 
          'Số lượng review', 'Điểm review', 'Các tiện nghi được ưa chuộng nhất',
          'Tên hạng phòng', 'Số lượng người', 'Giường', 'Diện tích phòng', 'Các lựa chọn'
        ];
        
        filteredResults = scraperStore.results.map(item => {
            const newItem: any = {};
            columns.forEach(col => newItem[col] = item[col]);
            return newItem;
        });
      } else {
        // Price mode
        const columns = [
          'Ngày cào', 'Giờ cào', 'Check in', 'Check out',
          'Tên khách sạn', 'Tên hạng phòng', 'Số lượng người',
          'Giá sau giảm', 'Giá gốc', 'Giảm giá'
        ];

        filteredResults = scraperStore.results.map(item => {
            const newItem: any = {};
            columns.forEach(col => newItem[col] = item[col]);
            return newItem;
        });
      }

      // Tạo worksheet từ results
      const ws = XLSX.utils.json_to_sheet(filteredResults)
      
      // Tạo workbook
      const wb = XLSX.utils.book_new()
      const sheetName = scrapeType.value === 'info' ? 'Thông tin KS' : 'Giá phòng'
      XLSX.utils.book_append_sheet(wb, ws, sheetName)
      
      // Tạo filename với timestamp và mode
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      const mode = scrapeType.value === 'info' ? 'info' : 'price'
      const market = selectedMarket.value && selectedMarket.value !== 'all' ? `_${selectedMarket.value}` : ''
      const filename = `booking_${mode}${market}_${timestamp}.xlsx`
      
      // Download file
      XLSX.writeFile(wb, filename)
      
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã tải xuống file Excel',
        life: 3000
      })
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể tải xuống Excel: ' + error.message,
      life: 5000
    })
  }
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
  if (!price || price === 'N/A') return ''
  const num = parseInt(price.toString().replace(/\D/g, ''))
  return num ? num.toLocaleString('vi-VN') + ' VND' : ''
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

.text-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  word-break: break-word;
}

/* Sidebar Layout */
.booking-tab-container {
  position: relative;
  padding: 1rem;
}

.menu-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 3.5rem;
  height: 3.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 999;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.step-item:hover {
  background: var(--surface-100);
  border-color: var(--primary-color);
}

.step-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.step-active {
  background: var(--primary-50);
  border-color: var(--primary-color);
}

.step-completed {
  background: var(--green-50);
}

.step-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-number {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.125rem;
}

.step-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

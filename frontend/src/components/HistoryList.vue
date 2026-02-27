<template>
  <div class="history-list">
    <Card class="filter-card mb-4">
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Công cụ lọc</span>
          <Button label="Lấy API dữ liệu mới nhất" icon="pi pi-bolt" class="p-button-outlined"
            @click="showLatestApiDialog = true" />
        </div>
      </template>
      <template #content>
        <div class="filters">
          <div class="filter-item">
            <label>Nguồn</label>
            <Dropdown v-model="filters.source" :options="sourceOptions" placeholder="Tất cả" class="w-full" />
          </div>

          <div class="filter-item"> <label>Loại cào</label>
            <Dropdown v-model="filters.scrapeType" :options="scrapeTypeOptions" optionLabel="label" optionValue="value"
              placeholder="Chọn loại cào" class="w-full" />
          </div>

          <div class="filter-item">
            <label>Market</label>
            <InputText v-model="filters.market" placeholder="Nhập market (ví dụ: VN, US)" class="w-full"
              @keyup.enter="loadHistories" />
          </div>

          <div class="filter-item">
            <label>Từ ngày</label>
            <Calendar v-model="filters.dateFrom" dateFormat="yy-mm-dd" showIcon class="w-full"
              @keyup.enter="loadHistories" />
          </div>

          <div class="filter-item">
            <label>Đến ngày</label>
            <Calendar v-model="filters.dateTo" dateFormat="yy-mm-dd" showIcon class="w-full"
              @keyup.enter="loadHistories" />
          </div>

          <div class="filter-item">
            <label style="visibility: hidden">Thao tác</label>
            <Button label="🔍 Tìm kiếm" @click="loadHistories" :loading="historyStore.loading" class="w-full" />
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
        <DataTable :value="historyStore.histories" :loading="historyStore.loading" responsiveLayout="scroll"
          class="p-datatable-sm" showGridlines stripedRows>
          <Column field="id" header="ID" :style="{ width: '70px' }" sortable></Column>
          <Column field="source" header="Nguồn" :style="{ width: '90px' }">
            <template #body="slotProps">
              <Tag :severity="getSourceSeverity(slotProps.data.source)">
                {{ slotProps.data.source.toUpperCase() }}
              </Tag>
            </template>
          </Column>
          <Column field="scrape_type" header="Loại cào" :style="{ width: '100px' }">
            <template #body="slotProps">
              <Tag :severity="slotProps.data.scrape_type === 'info' ? 'info' : 'warning'">
                {{ slotProps.data.scrape_type === 'info' ? 'Thông tin' : 'Cào giá' }}
              </Tag>
            </template>
          </Column>
          <Column field="market" header="Market" :style="{ width: '90px' }">
            <template #body="slotProps">
              <Tag v-if="slotProps.data.market" severity="secondary">
                {{ slotProps.data.market }}
              </Tag>
              <span v-else style="color: #999">All</span>
            </template>
          </Column>
          <Column field="crawl_date" header="Ngày cào" :style="{ width: '105px' }" sortable>
            <template #body="slotProps">
              {{ formatDate(slotProps.data.crawl_date) }}
            </template>
          </Column>
          <Column header="Check-in → Check-out" :style="{ width: '190px' }">
            <template #body="slotProps">
              <div v-if="slotProps.data.check_in && slotProps.data.check_out" style="font-size: 0.9em">
                <span style="color: #10b981">{{ formatDate(slotProps.data.check_in) }}</span>
                <span style="color: #999"> → </span>
                <span style="color: #ef4444">{{ formatDate(slotProps.data.check_out) }}</span>
              </div>
              <span v-else style="color: #999">-</span>
            </template>
          </Column>
          <Column field="created_at" header="Lưu lúc" :style="{ width: '145px' }" sortable>
            <template #body="slotProps">
              {{ formatDateTime(slotProps.data.created_at) }}
            </template>
          </Column>
          <Column field="total_records" header="Records" :style="{ width: '90px' }" sortable>
            <template #body="slotProps">
              <Tag :severity="slotProps.data.total_records > 0 ? 'success' : 'danger'">
                {{ slotProps.data.total_records }}
              </Tag>
            </template>
          </Column>
          <Column header="Thao tác" :style="{ width: '80px' }">
            <template #body="slotProps">
              <Button icon="pi pi-ellipsis-h" class="p-button-sm p-button-text" 
                @click="toggleMenu($event, slotProps.data.id)" />
              <Menu :ref="(el) => setMenuRef(el, slotProps.data.id)" :model="getMenuItems(slotProps.data.id)" :popup="true" />
            </template>
          </Column>
        </DataTable>

        <!-- Server-side Pagination -->
        <Paginator v-if="historyStore.totalCount > 0" :rows="historyStore.pageSize"
          :totalRecords="historyStore.totalCount" :first="(historyStore.currentPage - 1) * historyStore.pageSize"
          :rowsPerPageOptions="[10, 20, 50, 100]" @page="onPageChange"
          template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} trên tổng {totalRecords} phiên"
          class="mt-3" />
      </template>
    </Card>

    <!-- Latest API Dialog -->
    <Dialog v-model:visible="showLatestApiDialog" header="Lấy API Dữ liệu mới nhất" :modal="true"
      :style="{ width: '500px' }">
      <div class="flex flex-column gap-4">
        <p class="m-0 line-height-3">
          API này luôn trả về dữ liệu của <strong>phiên cào mới nhất</strong> theo loại bạn chọn.<br>
          Bạn có thể dán link này vào PowerBI (Web Source), Google Sheets, hoặc Excel và dữ liệu sẽ tự động cập nhật khi
          bạn
          Refresh.
        </p>

        <div class="grid formgrid p-fluid">
          <div class="col-6">
            <Button label="API Cào Giá" style="margin-top: 5px" class="p-button-warning"
              @click="copyLatestApiLink('price')" />
          </div>
          <div class="col-6">
            <Button label="API Cào Thông tin" style="margin-top: 5px" class="p-button-info"
              @click="copyLatestApiLink('info')" />
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Detail Dialog -->
    <Dialog v-model:visible="showDetailDialog" :header="`Chi tiết phiên cào #${selectedHistoryId}`" :modal="true"
      :style="{ width: '90vw' }">
      <div v-if="historyStore.currentHistory">
        <div class="detail-info mb-4">
          <div class="info-item">
            <strong>Ngày cào:</strong> {{ formatDate(historyStore.currentHistory.crawl_date) }}
          </div>
          <div class="info-item">
            <strong>Nguồn:</strong> {{ historyStore.currentHistory.source.toUpperCase() }}
          </div>
          <div class="info-item">
            <strong>Loại cào:</strong>
            <Tag :severity="historyStore.currentHistory.scrape_type === 'info' ? 'info' : 'warning'"
              style="margin-left: 0.5rem">
              {{ historyStore.currentHistory.scrape_type === 'info' ? 'Thông tin' : 'Cào giá' }}
            </Tag>
          </div>
          <div class="info-item" v-if="historyStore.currentHistory.market">
            <strong>Market:</strong> {{ historyStore.currentHistory.market }}
          </div>
          <div class="info-item">
            <strong>Tổng records:</strong> {{ historyStore.currentHistory.total_records }}
          </div>
        </div>

        <DataTable :value="historyStore.currentHistoryData" :paginator="true" :rows="20"
          :rowsPerPageOptions="[20, 50, 100]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageInput CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Trang {currentPage}/{totalPages} | Hiển thị {first}-{last} / {totalRecords} dòng"
          responsiveLayout="scroll" showGridlines>
          <!-- Info Mode Columns -->
          <template v-if="historyStore.currentHistory.scrape_type === 'info'">
            <Column field="hotel_name" header="Khách sạn" :style="{ minWidth: '200px' }"></Column>
            <Column field="hotel_link" header="Link" :style="{ width: '80px' }">
              <template #body="slotProps">
                <a :href="slotProps.data.hotel_link" target="_blank" v-if="slotProps.data.hotel_link">
                  <Button icon="pi pi-external-link" text size="small" />
                </a>
              </template>
            </Column>
            <Column field="review_count" header="Số review" :style="{ width: '100px' }"></Column>
            <Column field="review_score" header="Điểm" :style="{ width: '80px' }"></Column>
            <Column field="popular_facilities" header="Tiện nghi" :style="{ minWidth: '200px' }">
              <template #body="slotProps">
                <div class="text-ellipsis" v-tooltip.top="slotProps.data.popular_facilities" style="cursor: help;">
                  {{ slotProps.data.popular_facilities }}
                </div>
              </template>
            </Column>
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
            <Column field="Market" header="Market" :style="{ width: '100px' }">
              <template #body="slotProps">
                <Tag v-if="slotProps.data.market" severity="secondary">
                  {{ slotProps.data.market }}
                </Tag>
                <span v-else style="color: #999">-</span>
              </template>
            </Column>
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
            <Column field="hotel_link" header="Link" :style="{ width: '80px' }">
              <template #body="slotProps">
                <a :href="slotProps.data.hotel_link" target="_blank" v-if="slotProps.data.hotel_link">
                  <Button icon="pi pi-external-link" text size="small" />
                </a>
              </template>
            </Column>
            <Column field="Market" header="Market" :style="{ width: '100px' }">
              <template #body="slotProps">
                <Tag v-if="slotProps.data.market" severity="secondary">
                  {{ slotProps.data.market }}
                </Tag>
                <span v-else style="color: #999">-</span>
              </template>
            </Column>
          </template>
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
import Menu from 'primevue/menu'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const historyStore = useHistoryStore()
const toast = useToast()
const confirm = useConfirm()

const filters = ref({
  source: 'Tất cả',
  dateFrom: null as Date | null,
  dateTo: null as Date | null,
  scrapeType: 'all',
  market: ''
})

const sourceOptions = ['Tất cả', 'Booking', 'Agoda']
const scrapeTypeOptions = [
  { label: 'Tất cả', value: 'all' },
  { label: 'Thông tin', value: 'info' },
  { label: 'Cào giá', value: 'price' }
]

const showDetailDialog = ref(false)
const showLatestApiDialog = ref(false)
const selectedHistoryId = ref<number | null>(null)

// Menu management
const menuRefs = ref<Record<number, any>>({})

function setMenuRef(el: any, historyId: number) {
  if (el) {
    menuRefs.value[historyId] = el
  }
}

function toggleMenu(event: Event, historyId: number) {
  const menu = menuRefs.value[historyId]
  if (menu) {
    menu.toggle(event)
  }
}

function getMenuItems(historyId: number) {
  return [
    {
      label: 'Xem chi tiết',
      icon: 'pi pi-eye',
      command: () => viewDetail(historyId)
    },
    {
      label: 'Tải xuống Excel',
      icon: 'pi pi-download',
      command: () => exportExcel(historyId)
    },
    {
      label: 'Tạo danh sách Com...',
      icon: 'pi pi-list',
      command: () => exportCompetitorsList(historyId)
    },
    {
      label: 'Lấy API Link',
      icon: 'pi pi-link',
      command: () => copyApiLink(historyId)
    },
    {
      separator: true
    },
    {
      label: 'Xóa',
      icon: 'pi pi-trash',
      command: () => confirmDelete(historyId),
      class: 'text-red-500'
    }
  ]
}

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
      dateTo,
      filters.value.scrapeType,
      filters.value.market
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

function copyApiLink(historyId: number) {
  const url = `${API_BASE_URL}/public/history/${historyId}`
  
  // Try modern clipboard API first (HTTPS only)
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã copy link API Public vào clipboard',
        life: 3000
      })
    }).catch(() => {
      fallbackCopyToClipboard(url)
    })
  } else {
    fallbackCopyToClipboard(url)
  }
}

function copyLatestApiLink(type: 'price' | 'info') {
  const url = `${API_BASE_URL}/public/latest?scrape_type=${type}`
  
  // Try modern clipboard API first (HTTPS only)
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: `Đã copy link API (${type}) mới nhất`,
        life: 3000
      })
      showLatestApiDialog.value = false
    }).catch(() => {
      fallbackCopyToClipboard(url, type)
    })
  } else {
    fallbackCopyToClipboard(url, type)
  }
}

// Fallback copy method for HTTP (legacy browsers or non-HTTPS)
function fallbackCopyToClipboard(url: string, type?: 'price' | 'info') {
  try {
    const textArea = document.createElement('textarea')
    textArea.value = url
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    
    if (successful) {
      const detail = type ? `Đã copy link API (${type}) mới nhất` : 'Đã copy link API Public vào clipboard'
      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: detail,
        life: 3000
      })
      if (type) showLatestApiDialog.value = false
    } else {
      throw new Error('Copy command failed')
    }
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: 'Không thể copy link. Vui lòng copy thủ công từ URL: ' + url,
      life: 5000
    })
    console.error('Fallback copy failed: ', err)
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

async function exportExcel(historyId: number) {
  try {
    toast.add({
      severity: 'info',
      summary: 'Đang xử lý',
      detail: 'Đang tải dữ liệu và tạo file Excel...',
      life: 3000
    })

    const data = await historyStore.exportHistory(historyId)

    if (!data || data.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Thông báo',
        detail: 'Không có dữ liệu để xuất',
        life: 3000
      })
      return
    }

    const scrapeType = data.length > 0 ? data[0].scrape_type : 'info';

    // Define columns to match Main UI exactly
    const infoColumns = [
      'Ngày cào', 'Giờ cào', 'Check in', 'Check out',
      'Tên khách sạn', 'Link khách sạn',
      'Số lượng review', 'Điểm review', 'Các tiện nghi được ưa chuộng nhất',
      'Tên hạng phòng', 'Số lượng người', 'Giường', 'Diện tích phòng', 'Các lựa chọn', 'Market'
    ];

    const priceColumns = [
      'Ngày cào', 'Giờ cào', 'Check in', 'Check out',
      'Tên khách sạn', 'Tên hạng phòng', 'Số lượng người',
      'Giá sau giảm', 'Giá gốc', 'Giảm giá', 'Market'
    ];

    const targetColumns = scrapeType === 'price' ? priceColumns : infoColumns;

    // Filter and order data
    const filteredData = data.map((item: any) => {
      const newItem: any = {};
      targetColumns.forEach(col => {
        // Use existing value or empty string if N/A to keep Excel clean, or keep N/A if preferred. 
        // User UI often shows text, so let's keep original values.
        newItem[col] = item[col];
      });
      return newItem;
    });

    import('xlsx').then((XLSX) => {
      const ws = XLSX.utils.json_to_sheet(filteredData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, "Data")
      const filename = `history_export_${historyId}_${new Date().toISOString().slice(0, 10)}.xlsx`
      XLSX.writeFile(wb, filename)

      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã xuất file Excel',
        life: 3000
      })
    })

  } catch (error: any) {
    console.error(error)
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message || 'Không thể xuất Excel',
      life: 3000
    })
  }
}

async function exportCompetitorsList(historyId: number) {
  try {
    toast.add({
      severity: 'info',
      summary: 'Đang xử lý',
      detail: 'Đang tạo danh sách đối thủ...',
      life: 3000
    })

    const data = await historyStore.exportHistory(historyId)

    if (!data || data.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Thông báo',
        detail: 'Không có dữ liệu để xuất',
        life: 3000
      })
      return
    }

    // Define columns for Competitors List
    const competitorsColumns = [
      'Tên khách sạn',
      'Link khách sạn',
      'Tên hạng phòng',
      'Số lượng người',
      'Giường',
      'Diện tích phòng',
      'Các lựa chọn',
      'Các tiện nghi được ưa chuộng nhất',
      'Market',
      'Level đối thủ',
      'Giá bao gồm bữa sáng',
      'Nhóm hạng phòng',
      'Level'
    ];

    // Map data with empty columns for manual fields
    const competitorsData = data.map((item: any) => {
      return {
        'Tên khách sạn': item['Tên khách sạn'] || '',
        'Link khách sạn': item['Link khách sạn'] || '',
        'Tên hạng phòng': item['Tên hạng phòng'] || '',
        'Số lượng người': item['Số lượng người'] || '',
        'Giường': item['Giường'] || '',
        'Diện tích phòng': item['Diện tích phòng'] || '',
        'Các lựa chọn': item['Các lựa chọn'] || '',
        'Các tiện nghi được ưa chuộng nhất': item['Các tiện nghi được ưa chuộng nhất'] || '',
        'Market': item['Market'] || '',
        'Level đối thủ': '',
        'Giá bao gồm bữa sáng': '',
        'Nhóm hạng phòng': '',
        'Level': ''
      };
    });

    import('xlsx').then((XLSX) => {
      const ws = XLSX.utils.json_to_sheet(competitorsData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, "Competitors")
      const filename = `competitors_list_${historyId}_${new Date().toISOString().slice(0, 10)}.xlsx`
      XLSX.writeFile(wb, filename)

      toast.add({
        severity: 'success',
        summary: 'Thành công',
        detail: 'Đã tạo Competitors List',
        life: 3000
      })
    })

  } catch (error: any) {
    console.error(error)
    toast.add({
      severity: 'error',
      summary: 'Lỗi',
      detail: error.message || 'Không thể tạo Competitors List',
      life: 3000
    })
  }
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

  // Update page size if changed
  if (event.rows && event.rows !== historyStore.pageSize) {
    historyStore.pageSize = event.rows
  }

  // Load data for the new page
  const dateFrom = filters.value.dateFrom
    ? formatDateToString(filters.value.dateFrom)
    : undefined
  const dateTo = filters.value.dateTo
    ? formatDateToString(filters.value.dateTo)
    : undefined

  historyStore.fetchHistories(
    page,
    filters.value.source === 'Tất cả' ? undefined : filters.value.source,
    dateFrom,
    dateTo
  )
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

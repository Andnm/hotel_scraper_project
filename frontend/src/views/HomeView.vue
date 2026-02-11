<template>
  <div class="home-view">
    <Card>
      <template #title>
        <i class="pi pi-download"></i> Cào dữ liệu khách sạn
      </template>
      <template #content>
        <TabView>
          <TabPanel header="Booking.com">
            <BookingTab />
          </TabPanel>
          <TabPanel header="Agoda.com" :disabled="true">
            <p class="text-muted">Tính năng đang phát triển...</p>
          </TabPanel>
        </TabView>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import BookingTab from '@/components/BookingTab.vue'
</script>
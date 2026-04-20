
<template>
  <div :class="['bento-card', $attrs.class]" class="flex flex-col items-start">
    <p class="text-gray-400 text-sm mb-1 font-sans">{{ label }}</p>
    <h3 class="text-3xl font-extrabold mb-2 font-sans tracking-tight text-white">{{ value }}</h3>
    <apexchart v-if="series && options" type="bar" height="80" :options="options" :series="series" />
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import ApexChart from 'vue3-apexcharts';

defineProps({
  label: String,
  value: [String, Number],
  series: Array,
  options: Object
});
</script>

<style scoped>
.apexcharts-canvas {
  width: 100% !important;
}
</style>

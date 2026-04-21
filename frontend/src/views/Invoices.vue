<template>
  <div class="space-y-8 bg-[#09090b] min-h-screen text-white">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Invoices</h1>
        <p class="text-slate-400 mt-1">Manage and generate client billing documents.</p>
      </div>
    </header>

    <div class="border border-white/5 rounded-3xl shadow-2xl min-h-[400px]">
      <!-- The InvoicesTable component handles its own fetching, Create modal, and empty states! -->
      <InvoicesTable />
    </div>
  </div>
</template>

<script setup>
import InvoicesTable from '../components/InvoicesTable.vue';
</script>
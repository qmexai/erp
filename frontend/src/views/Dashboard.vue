<template>
  <div class="dashboard">
    <!-- Loading Skeleton Impact -->
    <div v-if="loading" class="w-full min-h-screen pt-4">
      <div class="animate-pulse space-y-6">
        <!-- Header Skeleton -->
        <div class="flex justify-between items-start">
          <div class="space-y-3">
            <div class="h-10 w-72 bg-white/5 rounded-lg border border-white/5"></div>
            <div class="h-4 w-48 bg-white/5 rounded-md"></div>
          </div>
          <div class="h-16 w-32 bg-white/5 rounded-2xl border border-white/5"></div>
        </div>
        <!-- Stats Row Skeleton -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="n in 4" :key="n" class="h-32 bg-[var(--qx-bg1)] rounded-[14px] border border-[var(--qx-border)] p-4 flex flex-col justify-between">
             <div class="h-3 w-20 bg-white/10 rounded"></div>
             <div class="h-8 w-32 bg-white/10 rounded"></div>
             <div class="h-6 w-full bg-white/5 rounded-t tracking-wider"></div>
          </div>
        </div>
        <!-- Mid Grid Skeleton -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="h-[400px] bg-[var(--qx-bg1)] rounded-[14px] border border-[var(--qx-border)] p-5"></div>
          <div class="lg:col-span-2 h-[400px] bg-[var(--qx-bg1)] rounded-[14px] border border-[var(--qx-border)] p-5"></div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="w-full relative">
      <!-- Error -->
      <div v-if="error" class="error-banner">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="8" cy="8" r="6"/><path d="M8 5v3M8 11v.5"/>
        </svg>
        {{ error }}
        <button class="retry-btn" @click="fetchAll">Retry</button>
      </div>

    <!-- Page header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Good {{ timeOfDay }}, {{ auth.user?.first_name }}</h1>
        <div class="page-sub">
          <span>{{ todayLabel }}</span>
          <span class="status-chip">All systems operational</span>
        </div>
      </div>
      <div v-if="isCeoOrHr" class="active-pill">
        <div class="pulse-wrap">
          <div class="pulse-ring" />
          <div class="pulse-dot" />
        </div>
        <div>
          <div class="active-count">{{ dashboardStats.active_now || 0 }}</div>
          <div class="active-label">active now</div>
        </div>
      </div>
    </div>

    <!-- ── Stat cards – CEO / HR ─────────────────────────── -->
    <div v-if="isCeoOrHr" class="stats-grid stats-grid--4">
      <div class="stat-card blue">
        <div class="stat-label">Total Revenue</div>
        <div class="stat-value">{{ formatCurrency(dashboardStats.total_revenue) }}</div>
        <div class="stat-footer"><span class="up">+12.4%</span> vs last month</div>
        <div class="sparkline">
          <div v-for="(h, i) in revenueBars" :key="i" class="bar" :style="{ height: h + '%' }" />
        </div>
        <div class="glow" />
      </div>

      <div class="stat-card green">
        <div class="stat-label">Active Projects</div>
        <div class="stat-value">{{ activeProjectCount }}</div>
        <div class="stat-footer"><span class="up">{{ completedProjectCount }} completed</span></div>
        <div class="sparkline">
          <div v-for="(h, i) in projectBars" :key="i" class="bar" :style="{ height: h + '%' }" />
        </div>
        <div class="glow" />
      </div>

      <div class="stat-card amber">
        <div class="stat-label">Open Leads</div>
        <div class="stat-value">{{ openLeadCount }}</div>
        <div class="stat-footer"><span class="neutral">{{ leads.length }} total</span></div>
        <div class="sparkline">
          <div v-for="(h, i) in leadBars" :key="i" class="bar" :style="{ height: h + '%' }" />
        </div>
        <div class="glow" />
      </div>

      <div class="stat-card violet">
        <div class="stat-label">Finance Expenses</div>
        <div class="stat-value">{{ formatCurrency(dashboardStats.total_expenses) }}</div>
        <div class="stat-footer"><span class="neutral">This period</span></div>
        <div class="sparkline">
          <div v-for="(h, i) in activityBars" :key="i" class="bar" :style="{ height: h + '%' }" />
        </div>
        <div class="glow" />
      </div>
    </div>

    <!-- ── Stat cards – Employee ─────────────────────────── -->
    <div v-else-if="auth.user" class="stats-grid stats-grid--3">
      <div class="stat-card blue">
        <div class="stat-label">Assigned Projects</div>
        <div class="stat-value">{{ dashboardStats.assigned_projects || 0 }}</div>
        <div class="stat-footer"><span class="up">Currently assigned</span></div>
        <div class="glow" />
      </div>
      <div class="stat-card green">
        <div class="stat-label">Active Tasks</div>
        <div class="stat-value">{{ dashboardStats.active_tasks || 0 }}</div>
        <div class="stat-footer"><span class="up">In progress</span></div>
        <div class="glow" />
      </div>
      <div class="stat-card amber">
        <div class="stat-label">Completed Tasks</div>
        <div class="stat-value">{{ dashboardStats.completed_tasks || 0 }}</div>
        <div class="stat-footer"><span class="up">All time</span></div>
        <div class="glow" />
      </div>
    </div>

    <!-- ── Mid row: pipeline + activity ─────────────────── -->
    <div class="mid-grid">

      <!-- Lead Kanban -->
      <div class="panel">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent blue" />Lead pipeline</div>
          <button class="panel-btn">+ Add lead</button>
        </div>
        <div class="panel-bd">
          <div v-if="leads.length" class="kban">
            <div v-for="col in kanbanCols" :key="col.key" class="kban-col">
              <div class="kban-head">
                {{ col.label }}
                <span class="kban-ct">{{ col.items.length }}</span>
              </div>
              <div
                v-for="lead in col.items"
                :key="lead.id"
                class="lead-card"
              >
                <div class="lead-name">{{ lead.client_name || lead.company_name }}</div>
                <div class="lead-meta">
                  <span :class="['tag', tempClass(lead)]">{{ lead.status || 'Normal' }}</span>
                  <span class="lead-src">{{ lead.field || '' }}</span>
                </div>
                <div v-if="lead.value || lead.deal_value" class="lead-amt">
                  ₹{{ Number(lead.value || lead.deal_value).toLocaleString('en-IN') }}
                </div>
              </div>
              <div v-if="!col.items.length" class="kban-empty">No leads</div>
            </div>
          </div>
          <div v-else class="empty">No active leads to display.</div>
        </div>
      </div>

      <!-- Activity feed -->
      <div class="panel">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent violet" />Recent activity</div>
          <button class="panel-btn">View all</button>
        </div>
        <div class="panel-bd" style="padding-top: 4px">
          <div v-for="(item, i) in activityFeed" :key="i" class="act-item">
            <div :class="['act-dot', item.color]" />
            <div>
              <div class="act-text" v-html="item.text" />
              <div class="act-time">{{ item.time }}</div>
            </div>
          </div>
          <div v-if="!activityFeed.length" class="empty">No recent activity.</div>
        </div>
      </div>
    </div>

    <!-- ── Bottom row ────────────────────────────────────── -->
    <div class="bot-grid">

      <!-- Projects table -->
      <div class="panel">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent green" />Projects</div>
          <button class="panel-btn">View all</button>
        </div>
        <div class="panel-bd">
          <table class="tbl">
            <thead><tr><th>Project</th><th>Status</th><th>Progress</th><th>Due</th></tr></thead>
            <tbody>
              <tr v-for="p in projects.slice(0, 6)" :key="p.id">
                <td class="fw">{{ p.name }}</td>
                <td><span :class="['badge', statusCls(p.status)]">{{ p.status }}</span></td>
                <td>
                  <div class="prog-wrap">
                    <div :class="['prog', progColor(p.status)]" :style="{ width: (p.progress || estProgress(p.status)) + '%' }" />
                  </div>
                </td>
                <td class="mono">{{ fmtDate(p.due_date || p.end_date) }}</td>
              </tr>
              <tr v-if="!projects.length"><td colspan="4" class="empty-cell">No projects found.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Finance table — CEO only -->
      <div v-if="auth.user?.role === 'CEO'" class="panel">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent amber" />Finance records</div>
          <button class="panel-btn">View all</button>
        </div>
        <div class="panel-bd">
          <table class="tbl">
            <thead><tr><th>Description</th><th>Type</th><th>Amount</th><th>Date</th></tr></thead>
            <tbody>
              <tr v-for="r in finance.slice(0, 6)" :key="r.id">
                <td class="fw">{{ r.description || r.title }}</td>
                <td>
                  <span :class="['badge', r.type === 'income' || r.type === 'revenue' ? 'active' : 'leave']">
                    {{ r.type }}
                  </span>
                </td>
                <td class="mono">₹{{ Number(r.amount).toLocaleString('en-IN') }}</td>
                <td class="mono">{{ fmtDate(r.date || r.created_at) }}</td>
              </tr>
              <tr v-if="!finance.length"><td colspan="4" class="empty-cell">No records found.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- HR: leave + tasks panels -->
      <div v-else-if="isCeoOrHr" class="panel">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent red" />Leave requests</div>
        </div>
        <div class="panel-bd"><LeaveRequestsTable /></div>
      </div>
    </div>

    <!-- ── Tasks + Calendar ──────────────────────────────── -->
    <div class="bot-grid" style="margin-top: 16px">
      <div class="panel">
        <div class="panel-hd"><div class="panel-title"><span class="accent violet" />Tasks</div></div>
        <div class="panel-bd"><TasksTable /></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><div class="panel-title"><span class="accent blue" />Meetings calendar</div></div>
        <div class="panel-bd"><MeetingsCalendar /></div>
      </div>
    </div>

    <!-- ── Staff management — CEO / HR ──────────────────── -->
    <div v-if="isCeoOrHr" class="panel" style="margin-top: 16px">
      <div class="panel-hd">
        <div class="panel-title"><span class="accent blue" />Staff management</div>
      </div>
      <div class="panel-bd"><AddEmployee /></div>
    </div>

    <!-- ── Leads + Projects tables — CEO / HR ───────────── -->
    <template v-if="isCeoOrHr">
      <div class="panel" style="margin-top: 16px">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent amber" />All leads</div>
          <button class="panel-btn">Export</button>
        </div>
        <div class="panel-bd"><LeadsTable :leads="leads" /></div>
      </div>
      <div class="panel" style="margin-top: 16px">
        <div class="panel-hd">
          <div class="panel-title"><span class="accent green" />All projects</div>
          <button class="panel-btn">Export</button>
        </div>
        <div class="panel-bd"><ProjectsTable :hideCompanyPhone="true" /></div>
      </div>
    </template>

    </div> <!-- Close Main Content wrapper -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import apiClient from '../api'
import { formatCurrency, fmtDateShort as fmtDate } from '../utils/formatters'

import AddEmployee        from '../components/AddEmployee.vue'
import LeadsTable         from '../components/LeadsTable.vue'
import ProjectsTable      from '../components/ProjectsTable.vue'
import FinanceTable       from '../components/FinanceTable.vue'
import LeaveRequestsTable from '../components/LeaveRequestsTable.vue'
import TasksTable         from '../components/TasksTable.vue'
import MeetingsCalendar   from '../components/MeetingsCalendar.vue'

const auth            = useAuthStore()
const loading         = ref(true)
const error           = ref('')
const dashboardStats  = ref({})
const leads           = ref([])
const projects        = ref([])
const finance         = ref([])

/* ── Computed ────────────────────────────────────────────── */
const isCeoOrHr = computed(() =>
  auth.user?.role === 'CEO' || auth.user?.role === 'HR'
)

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening'
})

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
)

const activeProjectCount    = computed(() => projects.value.filter(p => p.status === 'Active').length)
const completedProjectCount = computed(() => projects.value.filter(p => p.status === 'Completed').length)
const openLeadCount         = computed(() => leads.value.filter(l => ['Open', 'Not Started'].includes(l.status)).length)

const kanbanCols = computed(() => [
  { key: 'new',      label: 'New & Open',       items: leads.value.filter(l => ['Not Started','Open','open'].includes(l.status)) },
  { key: 'followup', label: 'In Progress/Interested', items: leads.value.filter(l => !['Not Started','Open','open','Closed','Not Interested'].includes(l.status)) },
  { key: 'closed',   label: 'Completed/Closed',  items: leads.value.filter(l => ['Closed', 'Not Interested'].includes(l.status)) },
])

const activityFeed = computed(() => {
  const items = []
  projects.value.slice(0, 3).forEach(p =>
    items.push({ color: 'blue',  text: `<strong>${p.name}</strong> — ${p.status}`,                                    time: fmtDate(p.updated_at || p.created_at) })
  )
  finance.value.slice(0, 2).forEach(f =>
    items.push({ color: f.type === 'income' || f.type === 'revenue' ? 'green' : 'red',
                 text: `<strong>${f.description || f.title}</strong> ₹${Number(f.amount).toLocaleString('en-IN')}`, time: fmtDate(f.date || f.created_at) })
  )
  leads.value.slice(0, 2).forEach(l =>
    items.push({ color: 'amber', text: `Lead <strong>${l.client_name || l.company_name}</strong> — ${l.status}`,               time: fmtDate(l.updated_at || l.created_at) })
  )
  return items.slice(0, 8)
})

/* Sparkline data (decorative) */
const revenueBars  = [40,55,45,70,60,80,75,100]
const projectBars  = [30,50,40,60,55,70,65,100]
const leadBars     = [80,60,90,75,100,70,55,60]
const activityBars = [50,40,70,55,65,80,60,100]

/* ── Data fetch ──────────────────────────────────────────── */
const fetchAll = async () => {
  loading.value = true
  error.value   = ''
  try {
    const calls = [
      apiClient.get('/dashboard/stats/'),
      apiClient.get('/projects/'),
      apiClient.get('/leads/'),
    ]
    if (isCeoOrHr.value) calls.push(apiClient.get('/finance/'))

    const results = await Promise.allSettled(calls)

    dashboardStats.value = results[0].status === 'fulfilled' ? results[0].value.data : {}
    projects.value       = results[1].status === 'fulfilled' ? results[1].value.data : []
    leads.value          = results[2].status === 'fulfilled' ? results[2].value.data : []
    finance.value        = results[3]?.status === 'fulfilled' ? results[3].value.data : []

    if (results.some(r => r.status === 'rejected'))
      error.value = 'Some data could not be loaded. Showing partial results.'
  } catch (e) {
    error.value = 'Failed to load dashboard. Please try again.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)

/* ── Helpers ─────────────────────────────────────────────── */
function statusCls(s) {
  return { Active:'active', Completed:'closed', 'In Review':'review', Pending:'pending', 'On Hold':'review', Cancelled:'leave' }[s] || 'pending'
}
function progColor(s) {
  return { Active:'blue', 'In Review':'amber', Completed:'green', Pending:'violet' }[s] || 'blue'
}
function estProgress(s) {
  return { Active:50, 'In Review':80, Completed:100, Pending:10, 'On Hold':30 }[s] || 40
}
function tempClass(lead) {
  const s = (lead.status || '').toLowerCase()
  if (s === 'open')   return 'hot'
  if (s === 'not started') return 'warm'
  return 'cold'
}
</script>

<style scoped>
/* All tokens from MainLayout :root are available here via CSS vars */

.dashboard {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* ── Loading ─────────────────────────────────────────────── */
.loading-overlay {
  position: fixed; inset: 0;
  background: var(--qx-bg0);
  display: flex; align-items: center; justify-content: center;
  gap: 12px; color: var(--qx-text3); font-size: 13px; z-index: 200;
}
.spinner {
  width: 20px; height: 20px; border-radius: 50%;
  border: 2px solid var(--qx-border2);
  border-top-color: var(--qx-blue);
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-banner {
  display: flex; align-items: center; gap: 8px;
  background: var(--qx-red-d); border: 1px solid var(--qx-red);
  color: var(--qx-red); padding: 10px 14px; border-radius: 10px;
  font-size: 13px; margin-bottom: 16px;
}
.retry-btn {
  margin-left: auto; background: transparent;
  border: 1px solid var(--qx-red); color: var(--qx-red);
  padding: 3px 10px; border-radius: 6px; cursor: pointer; font-size: 12px;
}

/* ── Header ──────────────────────────────────────────────── */
.page-header {
  display: flex; align-items: flex-start;
  justify-content: space-between; margin-bottom: 24px;
}
.page-title {
  font-size: 22px; font-weight: 600;
  letter-spacing: -.5px; color: var(--qx-text1);
}
.page-sub {
  font-size: 13px; color: var(--qx-text3);
  margin-top: 5px; display: flex; align-items: center; gap: 10px;
}
.status-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--qx-green-d); color: var(--qx-green);
  font-size: 10px; font-weight: 500; padding: 2px 8px; border-radius: 5px;
}
.status-chip::before {
  content: ''; width: 5px; height: 5px;
  background: var(--qx-green); border-radius: 50%;
}
.active-pill {
  display: flex; align-items: center; gap: 10px;
  background: var(--qx-bg1); border: 1px solid var(--qx-border2);
  padding: 10px 16px; border-radius: 12px;
}
.pulse-wrap {
  position: relative; width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
}
.pulse-ring {
  position: absolute; width: 26px; height: 26px;
  border-radius: 50%; border: 1.5px solid var(--qx-green);
  animation: pulse 2s ease-out infinite;
}
@keyframes pulse { 0%{transform:scale(.7);opacity:.7} 100%{transform:scale(1.4);opacity:0} }
.pulse-dot {
  width: 10px; height: 10px;
  background: var(--qx-green); border-radius: 50%;
}
.active-count { font-size: 20px; font-weight: 600; font-family:'DM Mono',monospace; line-height:1; }
.active-label { font-size: 10px; color: var(--qx-text3); }

/* ── Stat cards ──────────────────────────────────────────── */
.stats-grid {
  display: grid; gap: 12px; margin-bottom: 20px;
}
.stats-grid--4 { grid-template-columns: repeat(4, 1fr); }
.stats-grid--3 { grid-template-columns: repeat(3, 1fr); }

.stat-card {
  background: var(--qx-bg1); border: 1px solid var(--qx-border);
  border-radius: 14px; padding: 18px 20px;
  position: relative; overflow: hidden; transition: border-color .2s;
}
.stat-card:hover { border-color: var(--qx-border2); }
.stat-label {
  font-size: 10.5px; font-weight: 500; color: var(--qx-text3);
  letter-spacing: .4px; text-transform: uppercase; margin-bottom: 8px;
}
.stat-value {
  font-size: 26px; font-weight: 600; letter-spacing: -1px;
  font-family: 'DM Mono', monospace; color: var(--qx-text1);
}
.stat-footer { margin-top: 6px; font-size: 12px; color: var(--qx-text3); }
.up      { color: var(--qx-green); font-weight: 500; }
.down    { color: var(--qx-red);   font-weight: 500; }
.neutral { color: var(--qx-text2); }
.sparkline {
  display: flex; align-items: flex-end; gap: 3px;
  height: 28px; margin-top: 10px;
}
.bar { flex: 1; border-radius: 2px 2px 0 0; min-height: 3px; }
.stat-card.blue   .bar { background: var(--qx-blue);   opacity: .45; }
.stat-card.green  .bar { background: var(--qx-green);  opacity: .45; }
.stat-card.amber  .bar { background: var(--qx-amber);  opacity: .45; }
.stat-card.violet .bar { background: var(--qx-violet); opacity: .45; }
.stat-card.blue   .bar:last-child,
.stat-card.green  .bar:last-child,
.stat-card.amber  .bar:last-child,
.stat-card.violet .bar:last-child { opacity: 1; }
.glow {
  position: absolute; bottom: 0; right: 0; width: 70px; height: 50px;
}
.stat-card.blue   .glow { background: radial-gradient(circle at 100% 100%, var(--qx-blue)   0%, transparent 70%); opacity: .25; }
.stat-card.green  .glow { background: radial-gradient(circle at 100% 100%, var(--qx-green)  0%, transparent 70%); opacity: .25; }
.stat-card.amber  .glow { background: radial-gradient(circle at 100% 100%, var(--qx-amber)  0%, transparent 70%); opacity: .25; }
.stat-card.violet .glow { background: radial-gradient(circle at 100% 100%, var(--qx-violet) 0%, transparent 70%); opacity: .25; }

/* ── Mid grid ────────────────────────────────────────────── */
.mid-grid {
  display: grid; grid-template-columns: 1fr 300px;
  gap: 16px; margin-bottom: 16px;
}

/* ── Bot grid ────────────────────────────────────────────── */
.bot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* ── Panel ───────────────────────────────────────────────── */
.panel {
  background: var(--qx-bg1); border: 1px solid var(--qx-border);
  border-radius: 14px; overflow: hidden;
}
.panel-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--qx-border);
}
.panel-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: var(--qx-text1);
}
.accent {
  display: block; width: 3px; height: 14px;
  border-radius: 2px; flex-shrink: 0;
}
.accent.blue   { background: var(--qx-blue); }
.accent.green  { background: var(--qx-green); }
.accent.amber  { background: var(--qx-amber); }
.accent.violet { background: var(--qx-violet); }
.accent.red    { background: var(--qx-red); }
.panel-btn {
  font-size: 12px; color: var(--qx-text3); cursor: pointer;
  padding: 4px 9px; border-radius: 6px;
  border: 1px solid var(--qx-border); background: transparent;
  transition: all .15s;
}
.panel-btn:hover { color: var(--qx-text1); border-color: var(--qx-border2); }
.panel-bd { padding: 16px 18px; }

/* ── Kanban ──────────────────────────────────────────────── */
.kban { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.kban-head {
  font-size: 10.5px; font-weight: 500; color: var(--qx-text3);
  letter-spacing: .4px; text-transform: uppercase;
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.kban-ct {
  background: var(--qx-bg3); border-radius: 4px;
  padding: 1px 6px; font-family:'DM Mono',monospace; font-size: 10px;
}
.lead-card {
  background: var(--qx-bg2); border: 1px solid var(--qx-border);
  border-radius: 10px; padding: 11px 12px; margin-bottom: 8px;
  cursor: pointer; transition: all .15s;
}
.lead-card:hover { border-color: var(--qx-border3); transform: translateY(-1px); }
.lead-name { font-size: 13px; font-weight: 500; color: var(--qx-text1); margin-bottom: 5px; }
.lead-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.lead-src  { font-size: 11px; color: var(--qx-text3); }
.tag {
  font-size: 10px; font-weight: 500; padding: 2px 7px; border-radius: 4px;
}
.tag.hot  { background: var(--qx-red-d);   color: var(--qx-red); }
.tag.warm { background: var(--qx-amber-d); color: var(--qx-amber); }
.tag.cold { background: var(--qx-blue-d);  color: var(--qx-blue); }
.lead-amt {
  font-family:'DM Mono',monospace; font-size: 11px;
  color: var(--qx-text2); margin-top: 7px;
}
.kban-empty { font-size: 12px; color: var(--qx-text3); text-align: center; padding: 16px 0; }

/* ── Activity ────────────────────────────────────────────── */
.act-item {
  display: flex; align-items: flex-start; gap: 11px;
  padding: 11px 0; border-bottom: 1px solid var(--qx-border);
}
.act-item:last-child { border-bottom: none; }
.act-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0; margin-top: 4px;
}
.act-dot.blue   { background: var(--qx-blue); }
.act-dot.green  { background: var(--qx-green); }
.act-dot.amber  { background: var(--qx-amber); }
.act-dot.red    { background: var(--qx-red); }
.act-text { font-size: 13px; color: var(--qx-text2); line-height: 1.5; }
.act-text :deep(strong) { color: var(--qx-text1); font-weight: 500; }
.act-time { font-size: 11px; color: var(--qx-text3); font-family:'DM Mono',monospace; margin-top: 2px; }

/* ── Table ───────────────────────────────────────────────── */
.tbl { width: 100%; border-collapse: collapse; }
.tbl th {
  font-size: 10.5px; font-weight: 500; color: var(--qx-text3);
  letter-spacing: .4px; text-transform: uppercase;
  padding: 0 0 10px; border-bottom: 1px solid var(--qx-border); text-align: left;
}
.tbl td {
  padding: 9px 0; border-bottom: 1px solid var(--qx-border);
  font-size: 13px; color: var(--qx-text2); vertical-align: middle;
}
.tbl tr:last-child td { border-bottom: none; }
.tbl tr:hover td { color: var(--qx-text1); }
.fw   { color: var(--qx-text1) !important; font-weight: 500; }
.mono { font-family:'DM Mono',monospace; font-size: 12px; }
.empty-cell { color: var(--qx-text3); font-style: italic; padding: 16px 0 !important; }

.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 500; padding: 2px 8px; border-radius: 5px;
}
.badge::before { content: ''; width: 4px; height: 4px; border-radius: 50%; }
.badge.active  { background:var(--qx-green-d); color:var(--qx-green);  } .badge.active::before  { background:var(--qx-green);  }
.badge.review  { background:var(--qx-amber-d); color:var(--qx-amber);  } .badge.review::before  { background:var(--qx-amber);  }
.badge.pending { background:var(--qx-violet-d);color:var(--qx-violet); } .badge.pending::before { background:var(--qx-violet); }
.badge.closed  { background:var(--qx-bg3);     color:var(--qx-text3);  } .badge.closed::before  { background:var(--qx-text3);  }
.badge.open    { background:var(--qx-blue-d);  color:var(--qx-blue);   } .badge.open::before    { background:var(--qx-blue);   }
.badge.leave   { background:var(--qx-red-d);   color:var(--qx-red);    } .badge.leave::before   { background:var(--qx-red);    }

.prog-wrap { width: 80px; height: 4px; background: var(--qx-bg3); border-radius: 2px; overflow: hidden; }
.prog { height: 100%; border-radius: 2px; transition: width .4s; }
.prog.blue   { background: var(--qx-blue); }
.prog.green  { background: var(--qx-green); }
.prog.amber  { background: var(--qx-amber); }
.prog.violet { background: var(--qx-violet); }

.empty { font-size: 13px; color: var(--qx-text3); font-style: italic; text-align: center; padding: 24px 0; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 1100px) {
  .stats-grid--4 { grid-template-columns: repeat(2, 1fr); }
  .mid-grid      { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .stats-grid--4,
  .stats-grid--3 { grid-template-columns: 1fr 1fr; }
  .bot-grid      { grid-template-columns: 1fr; }
  .kban          { grid-template-columns: 1fr; }
}
</style>
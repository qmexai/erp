<template>
  <div class="qx-root">

    <!-- ── Sidebar ─────────────────────────────────────────── -->
    <aside class="qx-sidebar">

      <!-- Logo -->
      <div class="qx-logo">
        <div class="logo-mark">Qx</div>
        <div class="logo-text">
          <span class="logo-name">Qmexai</span>
          <span class="logo-tag">ERP</span>
        </div>
      </div>

      <!-- Nav -->
      <nav class="qx-nav">
        <div class="nav-section">Main</div>
        <SidebarItem icon="dashboard" label="Dashboard"  to="/app/dashboard" />

        <template v-if="isCEOOrHR">
          <SidebarItem icon="leads"    label="Leads"      to="/app/leads" />
          <SidebarItem icon="projects" label="Projects"   to="/app/projects" />
          <SidebarItem icon="finance"  label="Finance"    to="/app/finance" />
          <SidebarItem icon="invoices" label="Invoices"   to="/app/invoices" />
        </template>
        <template v-else>
          <SidebarItem icon="projects" label="Projects"   to="/app/projects" />
        </template>

        <div class="nav-section">Workspace</div>
        <SidebarItem icon="tasks"      label="Tasks"          to="/app/tasks" />
        <SidebarItem icon="calendar"   label="Meetings"       to="/app/meetings" />
        <SidebarItem icon="log-out"    label="Leave Requests" to="/app/leave-requests" />

        <template v-if="isCEOOrHR">
          <div class="nav-section">Admin</div>
          <SidebarItem icon="logs"     label="Activity Log"   to="/app/activity-log" />
        </template>
      </nav>

      <!-- Bottom -->
      <div class="sidebar-footer">
        <SidebarItem icon="settings" label="Settings" to="/app/settings" />
        <div class="sidebar-user">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-info">
            <div class="user-name">{{ auth.user?.name || auth.user?.email }}</div>
            <div class="user-role">{{ auth.user?.role }}</div>
          </div>
          <button class="logout-btn" title="Logout" @click="handleLogout">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- ── Main area ────────────────────────────────────────── -->
    <div class="qx-main-wrap">

      <!-- Topbar -->
      <header class="qx-topbar">
        <!-- Mobile hamburger -->
        <button class="mobile-menu-btn" @click="mobileOpen = !mobileOpen">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6"  x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <!-- Page title (derived from route) -->
        <div class="topbar-title">{{ pageTitle }}</div>

        <div class="topbar-right">
          <!-- Search -->
          <button class="icon-btn" title="Search">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="7" cy="7" r="4"/>
              <path d="M10.5 10.5L14 14"/>
            </svg>
          </button>

          <!-- Notifications -->
          <button class="icon-btn notif" title="Notifications">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M8 2a4 4 0 0 1 4 4v2l1 2H3l1-2V6a4 4 0 0 1 4-4z"/>
              <path d="M6.5 12.5a1.5 1.5 0 0 0 3 0"/>
            </svg>
          </button>

          <!-- User chip -->
          <div class="topbar-user">
            <div class="topbar-avatar">{{ userInitials }}</div>
            <div class="topbar-user-info">
              <div class="topbar-name">{{ auth.user?.name || auth.user?.email || 'User' }}</div>
              <div class="topbar-role">{{ auth.user?.role }}</div>
            </div>
          </div>
        </div>
      </header>

      <!-- Mobile drawer overlay -->
      <transition name="drawer">
        <div v-if="mobileOpen" class="mobile-overlay" @click="mobileOpen = false">
          <aside class="mobile-drawer" @click.stop>
            <div class="qx-logo" style="padding: 20px 16px 16px">
              <div class="logo-mark">Qx</div>
              <div class="logo-text">
                <span class="logo-name">Qmexai</span>
                <span class="logo-tag">ERP</span>
              </div>
            </div>
            <nav style="padding: 0 10px; display: flex; flex-direction: column; gap: 2px;">
              <SidebarItem icon="dashboard" label="Dashboard"      to="/app/dashboard"     @click="mobileOpen=false" />
              <template v-if="isCEOOrHR">
                <SidebarItem icon="leads"    label="Leads"          to="/app/leads"         @click="mobileOpen=false" />
                <SidebarItem icon="projects" label="Projects"       to="/app/projects"      @click="mobileOpen=false" />
                <SidebarItem icon="finance"  label="Finance"        to="/app/finance"       @click="mobileOpen=false" />
                <SidebarItem icon="invoices" label="Invoices"       to="/app/invoices"      @click="mobileOpen=false" />
              </template>
              <template v-else>
                <SidebarItem icon="projects" label="Projects"       to="/app/projects"      @click="mobileOpen=false" />
              </template>
              <SidebarItem icon="tasks"      label="Tasks"          to="/app/tasks"         @click="mobileOpen=false" />
              <SidebarItem icon="calendar"   label="Meetings"       to="/app/meetings"      @click="mobileOpen=false" />
              <SidebarItem icon="log-out"    label="Leave Requests" to="/app/leave-requests" @click="mobileOpen=false" />
              <template v-if="isCEOOrHR">
                <SidebarItem icon="logs"     label="Activity Log"   to="/app/activity-log"  @click="mobileOpen=false" />
              </template>
              <SidebarItem icon="settings"   label="Settings"       to="/app/settings"      @click="mobileOpen=false" />
            </nav>
          </aside>
        </div>
      </transition>

      <!-- Router view -->
      <main class="qx-page">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import SidebarItem from '../components/SidebarItem.vue'

const auth    = useAuthStore()
const router  = useRouter()
const route   = useRoute()

const mobileOpen = ref(false)

const isCEOOrHR = computed(() =>
  auth.user?.role === 'CEO' || auth.user?.role === 'HR'
)

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return ((u.first_name?.[0] || '') + (u.last_name?.[0] || '')).toUpperCase()
    || u.name?.[0]?.toUpperCase()
    || u.email?.[0]?.toUpperCase()
    || '?'
})

const pageTitle = computed(() => {
  const map = {
    '/app/dashboard':     'Dashboard',
    '/app/leads':         'Leads',
    '/app/projects':      'Projects',
    '/app/finance':       'Finance',
    '/app/invoices':      'Invoices',
    '/app/tasks':         'Tasks',
    '/app/meetings':      'Meetings',
    '/app/leave-requests':'Leave Requests',
    '/app/activity-log':  'Activity Log',
    '/app/settings':      'Settings',
  }
  for (const [path, label] of Object.entries(map)) {
    if (route.path.startsWith(path)) return label
  }
  return 'Enterprise Operations'
})

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Global CSS vars injected at root so SidebarItem.vue can use them ── */
:root {
  --qx-bg0:     #070709;
  --qx-bg1:     #0f0f16;
  --qx-bg2:     #171722;
  --qx-bg3:     #1f1f2e;
  --qx-border:  rgba(255, 255, 255, 0.05);
  --qx-border2: rgba(255, 255, 255, 0.09);
  --qx-border3: rgba(255, 255, 255, 0.16);
  --qx-text1:   #f8fafc;
  --qx-text2:   #94a3b8;
  --qx-text3:   #64748b;
  --qx-blue:    #6366f1;
  --qx-blue-d:  rgba(99, 102, 241, 0.12);
  --qx-blue-g:  rgba(99, 102, 241, 0.24);
  --qx-green:   #10b981;
  --qx-green-d: rgba(16, 185, 129, 0.12);
  --qx-amber:   #f59e0b;
  --qx-amber-d: rgba(245, 158, 11, 0.12);
  --qx-red:     #f43f5e;
  --qx-red-d:   rgba(244, 63, 94, 0.12);
  --qx-violet:  #a855f7;
  --qx-violet-d:rgba(168, 85, 247, 0.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--qx-bg0);
  color: var(--qx-text1);
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
}
</style>

<style scoped>
/* ── Root layout ─────────────────────────────────────────── */
.qx-root {
  display: flex;
  min-height: 100vh;
  background: var(--qx-bg0);
  font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ─────────────────────────────────────────────── */
.qx-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--qx-bg0);
  border-right: 1px solid var(--qx-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 40;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Logo */
.qx-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 22px 20px 16px;
  border-bottom: 1px solid var(--qx-border);
}
.logo-mark {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, #4f8ef7, #a78bfa);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #fff; letter-spacing: -.5px;
  flex-shrink: 0;
}
.logo-text { display: flex; align-items: baseline; gap: 5px; }
.logo-name { font-size: 15px; font-weight: 700; letter-spacing: -.3px; color: var(--qx-text1); }
.logo-tag  { font-size: 9px; font-weight: 500; color: var(--qx-text3); letter-spacing: .6px; text-transform: uppercase; }

/* Nav */
.qx-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.nav-section {
  font-size: 9.5px; font-weight: 500; color: var(--qx-text3);
  letter-spacing: .7px; text-transform: uppercase;
  padding: 14px 10px 5px;
}

/* Footer */
.sidebar-footer {
  padding: 10px;
  border-top: 1px solid var(--qx-border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--qx-bg1);
  border: 1px solid var(--qx-border);
  margin-top: 2px;
}
.user-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(135deg, #4f8ef7, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.user-info { flex: 1; min-width: 0; }
.user-name { font-size: 12px; font-weight: 500; color: var(--qx-text1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 10px; color: var(--qx-blue); font-weight: 500; text-transform: uppercase; letter-spacing: .3px; margin-top: 1px; }
.logout-btn {
  width: 26px; height: 26px; border-radius: 7px; flex-shrink: 0;
  background: transparent; border: 1px solid var(--qx-border2);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--qx-text3); transition: all .15s;
}
.logout-btn:hover { background: var(--qx-red-d); border-color: var(--qx-red); color: var(--qx-red); }

/* ── Main wrap ───────────────────────────────────────────── */
.qx-main-wrap {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Topbar ──────────────────────────────────────────────── */
.qx-topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  border-bottom: 1px solid var(--qx-border);
  background: var(--qx-bg0);
  position: sticky;
  top: 0;
  z-index: 30;
  gap: 12px;
}
.topbar-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--qx-text3);
  letter-spacing: .06em;
  text-transform: uppercase;
  flex: 1;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.icon-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--qx-bg2); border: 1px solid var(--qx-border2);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all .15s; color: var(--qx-text2);
}
.icon-btn:hover { border-color: var(--qx-border3); color: var(--qx-text1); }
.notif { position: relative; }
.notif::after {
  content: ''; position: absolute; top: 6px; right: 6px;
  width: 5px; height: 5px; background: var(--qx-blue);
  border-radius: 50%; border: 1.5px solid var(--qx-bg0);
}
.topbar-user {
  display: flex; align-items: center; gap: 9px;
  padding: 5px 10px 5px 5px;
  background: var(--qx-bg2); border: 1px solid var(--qx-border2);
  border-radius: 10px; cursor: pointer;
  transition: border-color .15s;
}
.topbar-user:hover { border-color: var(--qx-border3); }
.topbar-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #4f8ef7, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #fff;
}
.topbar-name { font-size: 12px; font-weight: 500; color: var(--qx-text1); line-height: 1.2; }
.topbar-role { font-size: 10px; color: var(--qx-blue); font-weight: 500; text-transform: uppercase; letter-spacing: .3px; }

/* ── Page content ────────────────────────────────────────── */
.qx-page {
  flex: 1;
  padding: 28px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

/* ── Mobile hamburger ────────────────────────────────────── */
.mobile-menu-btn {
  display: none;
  width: 34px; height: 34px; border-radius: 8px;
  background: var(--qx-bg2); border: 1px solid var(--qx-border2);
  align-items: center; justify-content: center;
  cursor: pointer; color: var(--qx-text2);
}

/* ── Mobile drawer ───────────────────────────────────────── */
.mobile-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.6);
  backdrop-filter: blur(4px);
  z-index: 50;
}
.mobile-drawer {
  width: 240px; height: 100%;
  background: var(--qx-bg1);
  border-right: 1px solid var(--qx-border2);
  overflow-y: auto;
}
.drawer-enter-active, .drawer-leave-active { transition: opacity .2s; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 768px) {
  .qx-sidebar     { display: none; }
  .qx-main-wrap   { margin-left: 0; }
  .mobile-menu-btn { display: flex; }
  .qx-page        { padding: 16px; }
  .topbar-title   { font-size: 12px; }
}
</style>
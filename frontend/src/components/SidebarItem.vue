<template>
  <router-link
    :to="to"
    class="sidebar-link"
    :class="{ 'is-active': isActive }"
  >
    <div class="link-icon">
      <component :is="iconComponent" :stroke-width="isActive ? 2.2 : 1.8" class="icon" />
    </div>
    <span class="link-label">{{ label }}</span>
    <div v-if="badge" class="link-badge">{{ badge }}</div>
    <div v-if="isActive" class="active-indicator" />
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  LayoutDashboard,
  Users,
  FolderKanban,
  Wallet,
  FileText,
  CheckCircle2,
  History,
  Settings,
  Calendar,
  LogOut,
  Circle,
  Home,
  Briefcase,
  CreditCard,
  List,
  CheckSquare,
} from 'lucide-vue-next'

const props = defineProps({
  icon:   { type: String, default: '' },
  label:  { type: String, default: '' },
  to:     { type: String, default: '/' },
  badge:  { type: [String, Number], default: null },
  mobile: { type: Boolean, default: false },
})

const route = useRoute()

const isActive = computed(() => {
  if (props.to === '/app/dashboard') return route.path === props.to
  return route.path.startsWith(props.to)
})

const iconMap = {
  dashboard:      LayoutDashboard,
  home:           Home,
  leads:          Users,
  users:          Users,
  projects:       FolderKanban,
  briefcase:      Briefcase,
  finance:        Wallet,
  'credit-card':  CreditCard,
  invoices:       FileText,
  'file-text':    FileText,
  tasks:          CheckCircle2,
  'check-square': CheckSquare,
  logs:           History,
  list:           List,
  settings:       Settings,
  calendar:       Calendar,
  meetings:       Calendar,
  'log-out':      LogOut,
  leave:          LogOut,
}

const iconComponent = computed(() => iconMap[props.icon] || Circle)
</script>

<style scoped>
.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--qx-text2);
  font-size: 13px;
  font-weight: 400;
  transition: all .2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  overflow: hidden;
}

.sidebar-link:hover {
  background: var(--qx-bg2);
  color: var(--qx-text1);
  transform: translateX(2px);
}

.sidebar-link.is-active {
  background: linear-gradient(135deg, var(--qx-blue-d), rgba(79, 142, 247, 0.08));
  color: var(--qx-blue);
  font-weight: 500;
}

.link-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
  transition: all .2s;
}

.sidebar-link.is-active .link-icon {
  background: var(--qx-blue-d);
  box-shadow: 0 0 12px rgba(79, 142, 247, 0.3);
}

.icon {
  width: 15px;
  height: 15px;
  transition: transform .3s ease;
}

.sidebar-link.is-active .icon {
  animation: iconBounce 0.5s ease;
}

@keyframes iconBounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.link-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.link-badge {
  background: var(--qx-bg3);
  border-radius: 5px;
  padding: 1px 7px;
  font-size: 10px;
  font-family: 'DM Mono', monospace;
  color: var(--qx-text3);
  flex-shrink: 0;
  animation: badgePop .3s ease;
}

.sidebar-link.is-active .link-badge {
  background: var(--qx-blue-d);
  color: var(--qx-blue);
}

@keyframes badgePop {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  background: var(--qx-blue);
  border-radius: 0 3px 3px 0;
  box-shadow: 2px 0 12px rgba(79, 142, 247, 0.4);
  animation: indicatorSlide .3s ease;
}

@keyframes indicatorSlide {
  from { transform: translateY(-50%) scaleY(0); }
  to { transform: translateY(-50%) scaleY(1); }
}

.sidebar-link:active {
  transform: scale(0.97);
}
</style>
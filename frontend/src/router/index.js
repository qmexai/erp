import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
  { 
    path: '/', 
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guestOnly: true }
  },
  { 
    path: '/app',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { 
        path: 'dashboard', 
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('../views/Projects.vue')
      },
      {
        path: 'leads',
        name: 'Leads',
        component: () => import('../views/Leads.vue'),
        meta: { roles: ['CEO', 'HR'] }
      },
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/Finance.vue'),
        meta: { roles: ['CEO'] }
      },
      {
        // ADDED: This fixes the blank Tasks page
        path: 'tasks', 
        name: 'Tasks',
        component: () => import('../views/Tasks.vue')
      },
      {
        path: 'invoices',
        name: 'Invoices',
        component: () => import('../views/Invoices.vue'),
        meta: { roles: ['CEO', 'HR'] }
      },
      {
        path: 'activity-log',
        name: 'ActivityLog',
        component: () => import('../views/ActivityLog.vue'),
        meta: { roles: ['CEO', 'HR'] }
      },
      {
        path: 'meetings',
        name: 'Meetings',
        component: () => import('../views/Meetings.vue'),
        meta: { roles: ['CEO', 'Manager', 'Employee'] }
      },
      {
        path: 'leave-requests',
        name: 'LeaveRequests',
        component: () => import('../views/LeaveRequests.vue'),
        meta: { roles: ['CEO', 'Manager', 'Employee'] }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue')
      }
    ]
  },
  // Redirects for better UX
  {
    path: '/dashboard',
    redirect: '/app/dashboard'
  },
  {
    path: '/tasks',
    redirect: '/app/tasks'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  const token = localStorage.getItem('token');
  const userRole = auth.user?.role;

  // 1. Guard for Protected Routes
  if (to.meta.requiresAuth && !token) {
    return { name: 'Login' };
  }

  // 2. Guard for Authenticated Users on Login Page
  if (to.meta.guestOnly && token) {
    return { name: 'Dashboard' };
  }

  // 3. Role-Based Access Control (RBAC)
  if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    console.warn(`Access denied for role: ${userRole}`);
    return { name: 'Dashboard' };
  }
});

export default router;
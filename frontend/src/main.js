import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' // This looks for index.js in the router folder
import './assets/css/style.css'
import VueApexCharts from 'vue3-apexcharts'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(VueApexCharts)

// Global error handler for Vue
app.config.errorHandler = (err, vm, info) => {
	// eslint-disable-next-line no-console
	console.error('Vue error:', err, info)
}

window.addEventListener('error', function (event) {
	// eslint-disable-next-line no-console
	console.error('Global JS error:', event.error)
})

window.addEventListener('unhandledrejection', function (event) {
	// eslint-disable-next-line no-console
	console.error('Unhandled promise rejection:', event.reason)
})

app.mount('#app')
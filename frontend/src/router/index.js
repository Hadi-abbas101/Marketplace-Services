import { createRouter, createWebHistory } from 'vue-router'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'
import DashboardView from '../views/DashboardView.vue'
import PublishServiceView from '../views/PublishServiceView.vue'
import ServiceDetailView from '../views/ServiceDetailView.vue'
import CategoryServicesView from '../views/CategoryServicesView.vue'
import MessagesView from '../views/MessagesView.vue'
import ConversationView from '../views/ConversationView.vue'
import SearchResultsView from '../views/SearchResultsView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tableau-de-bord',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/services/publier',
    name: 'PublishService',
    component: PublishServiceView,
    meta: { requiresAuth: true }
  },
  {
    path: '/recherche',
    name: 'SearchResults',
    component: SearchResultsView
  },
  {
    path: '/services/:category(maison|informatique|creation|marketing|redaction|administration)',
    name: 'CategoryServices',
    component: CategoryServicesView
  },
  {
    path: '/services/:id',
    name: 'ServiceDetail',
    component: ServiceDetailView,
    meta: {requiresAuth: true}
  },
  {
    path: '/services/:id/edit',
    name: 'EditService',
    component: PublishServiceView,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: MessagesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/:id',
    name: 'Conversation',
    component: ConversationView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) return '/register'
  if (to.path === '/register' && token) return '/'
})

export default router

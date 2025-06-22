import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/',
      component: Layout,
      redirect: '/query',
      children: [
        {
          path: 'query',
          name: 'query',
          component: () => import('../views/sub-pages/CommentQuery.vue')
        },
        {
          path: 'structure',
          name: 'structure',
          component: () => import('../views/sub-pages/AiStructure.vue')
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('../views/sub-pages/HistoryManagement.vue')
        },
        {
          path: 'analysis',
          name: 'analysis',
          component: () => import('../views/sub-pages/UserAnalysis.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  // 白名单，包含不需要认证的路由名称
  const publicPages = ['login', 'register'];
  const authRequired = !publicPages.includes(to.name as string);

  if (authRequired && !authStore.isAuthenticated) {
    next({ name: 'login' });
  } else {
    next();
  }
});

export default router

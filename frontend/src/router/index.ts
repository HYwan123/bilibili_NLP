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
      redirect: '/home',
      children: [
        {
          path: 'home',
          name: 'home',
          component: () => import('../views/Home.vue')
        },
        {
          path: 'query',
          name: 'query',
          component: () => import('../views/sub-pages/CommentQuery.vue')
        },
        {
          path: 'comment-analysis',
          name: 'comment-analysis',
          component: () => import('../views/sub-pages/CommentAnalysis.vue'),
          meta: { title: '评论分析', requiresAuth: true }
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
          path: 'user-analysis',
          name: 'user-analysis',
          component: () => import('../views/sub-pages/UserAnalysis.vue')
        },
        {
          path: 'user-portrait',
          name: 'UserPortrait',
          component: () => import('@/views/sub-pages/UserPortrait.vue'),
          meta: { title: '用户画像分析', requiresAuth: true }
        },
        {
          path: 'analysis-history',
          name: 'AnalysisHistory',
          component: () => import('@/views/sub-pages/AnalysisHistory.vue'),
          meta: { title: '分析记录', requiresAuth: true }
        },
        {
          path: 'content-recommendation',
          name: 'ContentRecommendation',
          component: () => import('@/views/sub-pages/ContentRecommendation.vue'),
          meta: { title: '内容推荐', requiresAuth: true }
        },
        {
          path: 'new-recommendation',
          name: 'NewRecommendation',
          component: () => import('@/views/sub-pages/NewRecommendation.vue'),
          meta: { title: '新版推荐', requiresAuth: true }
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

import { route } from 'quasar/wrappers'
import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import DocumentPage from '../pages/DocumentPage.vue'
import DocumentStatistics from '../pages/DocumentStatistics.vue'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

// 기존 routes에 통계 페이지 라우트 추가
const documentRoutes = [
  {
    path: '/document',
    name: 'Document',
    component: DocumentPage
  },
  {
    path: '/document/statistics',
    name: 'DocumentStatistics',
    component: DocumentStatistics
  }
]

// 기존 routes와 통계 페이지 라우트 병합
const allRoutes = [...routes, ...documentRoutes]

const router = createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes: allRoutes,
  history: createWebHistory()
})

export default route(function (/* { store, ssrContext } */) {
  return router
})

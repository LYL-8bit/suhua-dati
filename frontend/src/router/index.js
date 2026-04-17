import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('../views/Login.vue') },

    // 教师端
    {
      path: '/teacher',
      component: () => import('../layouts/TeacherLayout.vue'),
      meta: { role: 'teacher' },
      children: [
        { path: '', redirect: '/teacher/dashboard' },
        { path: 'dashboard', component: () => import('../views/teacher/Dashboard.vue') },
        { path: 'classes', component: () => import('../views/teacher/Classes.vue') },
        { path: 'questions', component: () => import('../views/teacher/Questions.vue') },
        { path: 'assignments', component: () => import('../views/teacher/Assignments.vue') },
        { path: 'classroom', component: () => import('../views/teacher/Classroom.vue') },
        { path: 'analysis', component: () => import('../views/teacher/Analysis.vue') },
      ],
    },

    // 学生端
    {
      path: '/student',
      component: () => import('../layouts/StudentLayout.vue'),
      meta: { role: 'student' },
      children: [
        { path: '', redirect: '/student/home' },
        { path: 'home', component: () => import('../views/student/Home.vue') },
        { path: 'assignment/:id', component: () => import('../views/student/DoAssignment.vue') },
        { path: 'wrong-book', component: () => import('../views/student/WrongBook.vue') },
        { path: 'analysis', component: () => import('../views/student/MyAnalysis.vue') },
      ],
    },

    // 课堂扫码答题（无需登录）
    { path: '/classroom/join/:token', component: () => import('../views/classroom/Join.vue') },
  ],
})

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (to.meta.role && (!user || user.role !== to.meta.role)) {
    next('/login')
  } else {
    next()
  }
})

export default router

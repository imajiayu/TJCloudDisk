import { createRouter, createWebHashHistory } from 'vue-router'
import axios from "axios"
import { ElSkeleton } from 'element-plus'

const routes = [
    {
        path: '/',
        name: '/',
        component: () => import('../components/UserSpace.vue'),
        meta: {
            requireAuth: true,
        }
    }, {
        path: '/UserSpace',
        name: 'UserSpace',
        component: () => import('../components/UserSpace.vue'),
        meta: {
            requireAuth: true,
        }
    },{
        path: '/Share/:token',
        name: 'ShareSpace',
        component: () => import('../components/ShareSpace.vue'),
        meta: {
            requireAuth: true,
        }
    }, {
        path: '/Login',
        name: 'Login',
        component: () => import('../components/Login.vue'),
        meta: {
            requireAuth: false,
        }
    }, {
        path: '/Register',
        name: 'Register',
        component: () => import('../components/Register.vue'),
        meta: {
            requireAuth: false,
        }
    }, {
        path: '/ForgetPassword',
        name: 'ForgetPassword',
        component: () => import('../components/ForgetPassword.vue'),
        meta: {
            requireAuth: false,
        }
    },
    {
        path: '/Revise',
        name: 'Revise',
        component: () => import('../components/Revise.vue'),
        meta: {
            requireAuth: true,
        }
    },
    {
        path: '/:catchAll(.*)',
        name: 'NotFound',
        component: () => import('../components/404.vue'),
        meta: {
            requireAuth: false
        }
    },

]


const router = createRouter({
    //history: createWebHistory(process.env.BASE_URL),
    history: createWebHashHistory(),
    routes: routes,
})

router.beforeEach((to, from, next) => {
    if (to.meta.requireAuth == false) {
        next();
    } else {
        axios.get("api/accounts/getIdentity").then((response) => {
            if (response.data.isLogin === "False") {
                next("/Login")
            }
            else {
                next()
            }
        })
    }
})

export default router
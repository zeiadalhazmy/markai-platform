import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole, ensureProfileDefaultRole } from "../lib/profile";

import AppShell from "../layouts/AppShell.vue";

// Auth
import LoginView from "../views/LoginView.vue"; // غيّره لو اسم ملفك مختلف

// Client
import ClientHome from "../views/client/HomeView.vue";
import ClientProducts from "../views/client/ProductsView.vue";
import ClientOrders from "../views/client/OrdersView.vue";

// Merchant
import MerchantHome from "../views/merchant/HomeView.vue";
import MerchantProducts from "../views/merchant/ProductsView.vue";
import MerchantOrders from "../views/merchant/OrdersView.vue";

// Courier
import CourierHome from "../views/courier/HomeView.vue";
import CourierTasks from "../views/courier/TasksView.vue";

// Admin (تقدر توصلها لاحقاً)
import AdminHome from "../views/admin/HomeView.vue";

import "./assets/theme.css";
import "./assets/ui.css";




const routes = [
  { path: "/", redirect: "/auth" },
  { path: "/auth", component: LoginView },

  // كل التطبيق داخل AppShell
  {
    path: "/",
    component: AppShell,
    meta: { requiresAuth: true },
    children: [
      { path: "client", component: ClientHome, meta: { role: ["customer"] } },
      { path: "client/products", component: ClientProducts, meta: { role: ["customer"] } },
      { path: "client/orders", component: ClientOrders, meta: { role: ["customer"] } },

      { path: "merchant", component: MerchantHome, meta: { role: ["merchant"] } },
      { path: "merchant/products", component: MerchantProducts, meta: { role: ["merchant"] } },
      { path: "merchant/orders", component: MerchantOrders, meta: { role: ["merchant"] } },

      { path: "courier", component: CourierHome, meta: { role: ["courier"] } },
      { path: "courier/tasks", component: CourierTasks, meta: { role: ["courier"] } },

      { path: "admin", component: AdminHome, meta: { role: ["admin"] } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth);
  const roleNeeded = to.meta?.role;

  const { data } = await supabase.auth.getSession();
  const session = data.session;

  if (requiresAuth && !session) return "/auth";

  if (session) {
    // أنشئ profile افتراضي (customer) أول مرة
    await ensureProfileDefaultRole();
  }

  if (session && roleNeeded?.length) {
    const role = await getUserRole();
    if (!roleNeeded.includes(role)) {
      // رده لصفحته الصحيحة
      if (role === "merchant") return "/merchant";
      if (role === "courier") return "/courier";
      if (role === "admin") return "/admin";
      return "/client";
    }
  }

  return true;
});

export default router;

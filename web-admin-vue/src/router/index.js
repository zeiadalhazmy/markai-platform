import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole, ensureProfileDefaultRole } from "../lib/profile";

import AppShell from "../layouts/AppShell.vue";

// Auth
import AuthView from "../views/auth/AuthView.vue";
import VerifyOtpView from "../views/auth/VerifyOtpView.vue";
import RolePickView from "../views/auth/RolePickView.vue";

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

// Admin
import AdminHome from "../views/admin/HomeView.vue";

const routes = [
  { path: "/", redirect: "/auth" },

  { path: "/auth", component: AuthView },
  { path: "/auth/verify", component: VerifyOtpView },
  { path: "/auth/role", component: RolePickView },

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

function roleHome(role){
  if (role === "merchant") return "/merchant";
  if (role === "courier") return "/courier";
  if (role === "admin") return "/admin";
  return "/client";
}

router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth);
  const roleNeeded = to.meta?.role;

  const { data } = await supabase.auth.getSession();
  const session = data.session;

  // لو صفحة محمية ومش مسجل
  if (requiresAuth && !session) return "/auth";

  // لو مسجل وواقف على auth، وده للهوم
  if (session && to.path.startsWith("/auth")) {
    try{
      await ensureProfileDefaultRole();
      const role = await getUserRole();
      return role ? roleHome(role) : "/auth/role";
    }catch{
      return "/auth/role";
    }
  }

  if (session) {
    await ensureProfileDefaultRole();
  }

  // تحقق الصلاحية
  if (session && roleNeeded?.length) {
    const role = await getUserRole();
    if (!roleNeeded.includes(role)) return roleHome(role);
  }

  return true;
});

export default router;

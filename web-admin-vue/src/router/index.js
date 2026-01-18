import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole, ensureProfileDefaultRole } from "../lib/profile";

import AppShell from "../layouts/AppShell.vue";

// Auth
import LoginView from "../views/auth/LoginView.vue";
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
import MerchantInventory from "../views/merchant/InventoryView.vue";

// Courier
import CourierHome from "../views/courier/HomeView.vue";
import CourierTasks from "../views/courier/TasksView.vue";

// Admin
import AdminHome from "../views/admin/HomeView.vue";

const routes = [
  { path: "/", redirect: "/auth" },

  // دعم الرابط القديم
  { path: "/login", redirect: "/auth" },

  // Auth
  { path: "/auth", component: LoginView },
  { path: "/auth/verify", component: VerifyOtpView },
  { path: "/auth/role", component: RolePickView, meta: { requiresAuth: true } },

  // AppShell (داخلها صفحات الأدوار)
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
      { path: "merchant/inventory", component: MerchantInventory, meta: { role: ["merchant"] } },

      { path: "courier", component: CourierHome, meta: { role: ["courier"] } },
      { path: "courier/tasks", component: CourierTasks, meta: { role: ["courier"] } },

      { path: "admin", component: AdminHome, meta: { role: ["admin"] } },
    ],
  },

  // أي شيء غلط → رجّعه للـ auth
  { path: "/:pathMatch(.*)*", redirect: "/auth" },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some((r) => r.meta?.requiresAuth);
  const roleNeeded = to.meta?.role;

  const { data } = await supabase.auth.getSession();
  const session = data.session;

  if (requiresAuth && !session) return "/auth";

  if (session) {
    await ensureProfileDefaultRole();
  }

  // إن كانت صفحة تطلب Role محدد
  if (session && roleNeeded?.length) {
    const role = await getUserRole();

    // لو ما عنده role مضبوط → خليه يختار Role أول مرة
    if (!role) return "/auth/role";

    if (!roleNeeded.includes(role)) {
      if (role === "merchant") return "/merchant";
      if (role === "courier") return "/courier";
      if (role === "admin") return "/admin";
      return "/client";
    }
  }

  return true;
});

export default router;

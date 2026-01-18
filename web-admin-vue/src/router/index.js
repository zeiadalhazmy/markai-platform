import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";

import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import OrdersMeView from "../views/OrdersMeView.vue";
import ProductsView from "../views/ProductsView.vue";

const routes = [
  { path: "/login", component: LoginView },
  { path: "/", component: DashboardView, meta: { requiresAuth: true } },
  { path: "/orders-me", component: OrdersMeView, meta: { requiresAuth: true } },
  { path: "/products", component: ProductsView }, // public endpoint
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true;

  const { data } = await supabase.auth.getSession();
  if (!data.session) return "/login";
  return true;
});

export default router;


import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";

import VendorsAdminView from "../views/VendorsAdminView.vue";
import BranchesAdminView from "../views/BranchesAdminView.vue";
import ProductsAdminView from "../views/ProductsAdminView.vue";
import OrdersAdminView from "../views/OrdersAdminView.vue";
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import OrdersMeView from "../views/OrdersMeView.vue";
import ProductsView from "../views/ProductsView.vue";

const routes = [
  { path: "/login", component: LoginView },
  { path: "/", component: DashboardView, meta: { requiresAuth: true } },
  { path: "/orders-me", component: OrdersMeView, meta: { requiresAuth: true } },
  { path: "/products", component: ProductsView }, // public endpoint
  {
  path: "/admin/vendors",
  name: "AdminVendors",
  component: VendorsAdminView,
},
{
  path: "/admin/branches",
  name: "AdminBranches",
  component: BranchesAdminView,
},
{
  path: "/admin/products",
  name: "AdminProducts",
  component: ProductsAdminView,
},
{
  path: "/admin/orders",
  name: "AdminOrders",
  component: OrdersAdminView,
},
{
  path: "/admin/vendors",
  name: "admin-vendors",
  component: () => import("../views/AdminVendorsView.vue"),
},
{
  path: "/admin/branches",
  name: "admin-branches",
  component: () => import("../views/AdminBranchesView.vue"),
},
{
  path: "/admin/products",
  name: "admin-products",
  component: () => import("../views/AdminProductsView.vue"),
},



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


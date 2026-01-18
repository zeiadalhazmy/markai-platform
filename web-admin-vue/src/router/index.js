import { createRouter, createWebHistory } from "vue-router";
import { supabase } from "../lib/supabase";

import LoginView from "../views/auth/LoginView.vue";
import VerifyOtpView from "../views/auth/VerifyOtpView.vue";
import RolePickView from "../views/RolePickView.vue";

import ClientHome from "../views/client/ClientHome.vue";
import MerchantHome from "../views/merchant/MerchantHome.vue";
import CourierHome from "../views/courier/CourierHome.vue";
import AdminHome from "../views/admin/AdminHome.vue";

// (لو عندك صفحات الأدمن القديمة)
import ProductsView from "../views/ProductsView.vue";
import OrdersMeView from "../views/OrdersMeView.vue";




async function getMyRole(){
  const { data } = await supabase.auth.getUser();
  const user = data?.user;
  if(!user) return null;

  const { data: profile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .maybeSingle();

  return profile?.role || null;
}

const routes = [
  { path: "/auth", component: LoginView },
  { path: "/auth/verify", component: VerifyOtpView },

  { path: "/role", component: RolePickView, meta: { requiresAuth: true } },

  { path: "/client", component: ClientHome, meta: { requiresAuth: true, roles: ["client"] } },
  { path: "/merchant", component: MerchantHome, meta: { requiresAuth: true, roles: ["merchant"] } },
  { path: "/courier", component: CourierHome, meta: { requiresAuth: true, roles: ["courier"] } },

  { path: "/admin", component: AdminHome, meta: { requiresAuth: true, roles: ["admin"] } },

  // صفحات أدمن موجودة عندك (لو تبغاها تحت /admin)
  { path: "/admin/products", component: ProductsView, meta: { requiresAuth: true, roles: ["admin"] } },
  { path: "/admin/orders", component: OrdersMeView, meta: { requiresAuth: true, roles: ["admin"] } },

  

  { path: "/", redirect: "/auth" }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const { data } = await supabase.auth.getSession();
  const session = data.session;

  if(to.meta.requiresAuth && !session){
    return "/auth";
  }

  if(to.meta.requiresAuth && to.meta.roles){
    const role = await getMyRole();
    if(!role) return "/role";
    if(!to.meta.roles.includes(role)) return "/role";
  }
});

export default router;

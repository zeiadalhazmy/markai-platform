import { supabase } from "./supabase";

const CORE = import.meta.env.VITE_CORE_API_URL; // ✅ لازم في Vercel
if (!CORE) console.warn("VITE_CORE_API_URL is missing");

async function authHeader() {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, { method="GET", body=null, auth=false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) Object.assign(headers, await authHeader());

  const res = await fetch(`${CORE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const txt = await res.text();
  let data;
  try { data = txt ? JSON.parse(txt) : null; } catch { data = txt; }

  if (!res.ok) {
    const msg = data?.detail || data?.message || JSON.stringify(data);
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return data;
}

// Client
export const apiListProducts = (params={}) => {
  const usp = new URLSearchParams();
  if (params.q) usp.set("q", params.q);
  return request(`/v1/products?${usp.toString()}`);
};
export const apiMyOrders = () => request("/v1/orders/me", { auth: true });
export const apiCreateOrder = (payload) => request("/v1/orders", { method:"POST", body: payload, auth:true });

// Merchant
export const apiVendorListProducts = () => request("/v1/vendor-admin/products", { auth:true });
export const apiVendorCreateProduct = (payload) => request("/v1/vendor-admin/products", { method:"POST", body: payload, auth:true });
export const apiVendorOrders = () => request("/v1/vendor-admin/orders", { auth:true });
export const apiUpdateOrderStatus = (orderId, status) =>
  request(`/v1/orders/${orderId}/status`, { method:"PATCH", body:{ status }, auth:true });

// Courier
export const apiCourierAvailable = () => request("/v1/service-requests/available", { auth:true });
export const apiCourierAccept = (id) => request(`/v1/service-requests/${id}/accept`, { method:"POST", auth:true });
export const apiCourierComplete = (id) => request(`/v1/service-requests/${id}/complete`, { method:"POST", auth:true });

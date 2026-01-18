import { supabase } from "./supabase";
import { ROLES } from "./roles";

export async function getCurrentUser() {
  const { data } = await supabase.auth.getUser();
  return data?.user || null;
}

export async function ensureProfileDefaultRole() {
  const user = await getCurrentUser();
  if (!user) return null;

  // 1) جرّب جدول profiles
  const { data: prof, error } = await supabase
    .from("profiles")
    .select("id, role")
    .eq("id", user.id)
    .maybeSingle();

  if (!error && prof) return prof;

  // لو ما في سجل -> أنشئه كـ customer
  await supabase.from("profiles").upsert({
    id: user.id,
    role: ROLES.CUSTOMER,
  });

  return { id: user.id, role: ROLES.CUSTOMER };
}

export async function getUserRole() {
  const user = await getCurrentUser();
  if (!user) return null;

  // profiles أولاً
  const { data: prof } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .maybeSingle();

  if (prof?.role) return prof.role;

  // fallback metadata
  const metaRole = user?.user_metadata?.role || user?.app_metadata?.role;
  return metaRole || ROLES.CUSTOMER;
}

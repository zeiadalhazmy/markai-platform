import { supabase } from "./supabase";
import { ROLES } from "./roles";

export async function getUserRole() {
  const { data: s } = await supabase.auth.getSession();
  const uid = s.session?.user?.id;
  if (!uid) return null;

  const { data, error } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", uid)
    .single();

  if (error) return null;
  return data?.role || null;
}

export async function ensureProfileDefaultRole() {
  const { data: s } = await supabase.auth.getSession();
  const user = s.session?.user;
  if (!user) return;

  // إذا ما عنده profile، أنشئه بـ customer
  const { data } = await supabase
    .from("profiles")
    .select("id, role")
    .eq("id", user.id)
    .maybeSingle();

  if (!data) {
    await supabase.from("profiles").insert({
      id: user.id,
      role: ROLES.CUSTOMER,
      email: user.email ?? null,
      phone: user.phone ?? null,
    });
  }
}

export async function setUserRole(role) {
  const { data: s } = await supabase.auth.getSession();
  const uid = s.session?.user?.id;
  if (!uid) throw new Error("No session");

  const { error } = await supabase.from("profiles").upsert({
    id: uid,
    role,
  });

  if (error) throw error;
}

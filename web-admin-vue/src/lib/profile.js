import { supabase } from "./supabase";

export async function getUserRole() {
  const { data: s } = await supabase.auth.getSession();
  const userId = s.session?.user?.id;
  if (!userId) return null;

  const { data, error } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", userId)
    .single();

  if (error) return null;
  return data?.role ?? null;
}

export async function ensureProfileDefaultRole() {
  const { data: s } = await supabase.auth.getSession();
  const userId = s.session?.user?.id;
  if (!userId) return;

  const { data } = await supabase
    .from("profiles")
    .select("id, role")
    .eq("id", userId)
    .single();

  // لو ما لقا سجل (لسبب ما) أنشئه
  if (!data?.id) {
    await supabase.from("profiles").insert({ id: userId, role: "customer" });
    return;
  }

  // لو role فاضي
  if (!data.role) {
    await supabase.from("profiles").update({ role: "customer" }).eq("id", userId);
  }
}

export async function setMyRole(role) {
  const { data: s } = await supabase.auth.getSession();
  const userId = s.session?.user?.id;
  if (!userId) throw new Error("No session");

  const { error } = await supabase
    .from("profiles")
    .update({ role })
    .eq("id", userId);

  if (error) throw error;
}

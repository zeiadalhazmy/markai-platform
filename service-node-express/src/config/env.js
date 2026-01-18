import "dotenv/config";

function required(name) {
  const v = process.env[name];
  if (!v) throw new Error(`${name} is missing`);
  return v;
}

export const env = {
  PORT: process.env.PORT || "3000",
  CORE_API_URL: required("CORE_API_URL").replace(/\/+$/, ""),
  SUPABASE_URL: required("SUPABASE_URL").replace(/\/+$/, ""),
  CORS_ORIGINS: (process.env.CORS_ORIGINS || "*")
    .split(",")
    .map(s => s.trim())
    .filter(Boolean)
};

import { createRemoteJWKSet, jwtVerify } from "jose";
import { env } from "../config/env.js";

const jwks = createRemoteJWKSet(
  new URL(`${env.SUPABASE_URL}/auth/v1/.well-known/jwks.json`)
);

export async function optionalAuth(req, _res, next) {
  const auth = req.headers.authorization || "";
  if (!auth.startsWith("Bearer ")) return next();

  const token = auth.slice("Bearer ".length).trim();
  try {
    const { payload } = await jwtVerify(token, jwks, {
      // لا نقيّد issuer/audience حالياً لتفادي مشاكل اختلاف الإعدادات
      // (لو تبغى نقيّدها لاحقاً نضبطها بناء على توكنك)
    });
    req.user = { id: payload.sub, payload };
  } catch {
    // لو التوكن غلط نخليه بدون user (اختياري)
  }
  next();
}

export async function requireAuth(req, res, next) {
  const auth = req.headers.authorization || "";
  if (!auth.startsWith("Bearer ")) {
    return res.status(401).json({ detail: "Missing Bearer token" });
  }
  const token = auth.slice("Bearer ".length).trim();

  try {
    const { payload } = await jwtVerify(token, jwks, {});
    req.user = { id: payload.sub, payload };
    next();
  } catch (e) {
    return res.status(401).json({ detail: `Invalid token: ${e?.message || e}` });
  }
}

import express from "express";
import cors from "cors";
import morgan from "morgan";
import axios from "axios";
import { env } from "./config/env.js";
import { optionalAuth } from "./middlewares/auth.js";

const app = express();

app.use(express.json({ limit: "2mb" }));
app.use(morgan("tiny"));

app.use(
  cors({
    origin: env.CORS_ORIGINS.includes("*") ? true : env.CORS_ORIGINS,
    credentials: true
  })
);

app.get("/", (_req, res) => res.json({ message: "MarkAi Node Gateway", health: "/health" }));
app.get("/health", (_req, res) => res.json({ status: "ok" }));

const core = axios.create({
  baseURL: env.CORE_API_URL,
  timeout: 20000
});

// مرّر أي شيء يبدأ بـ /v1 إلى FastAPI
app.all("/v1/*", optionalAuth, async (req, res) => {
  try {
    const headers = {
      // مرّر Authorization كما هو
      authorization: req.headers.authorization || "",
      "content-type": req.headers["content-type"] || "application/json"
    };

    const r = await core.request({
      url: req.originalUrl,        // نفس المسار /v1/...
      method: req.method,
      headers,
      params: req.query,
      data: req.body
    });

    return res.status(r.status).json(r.data);
  } catch (e) {
    const status = e?.response?.status || 500;
    const data = e?.response?.data || { detail: e?.message || "Gateway error" };
    return res.status(status).json(data);
  }
});

const port = Number(env.PORT);
app.listen(port, "0.0.0.0", () => {
  console.log(`Node Gateway listening on :${port}`);
});

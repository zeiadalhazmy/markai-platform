const express = require("express");
const cors = require("cors");
const { createProxyMiddleware } = require("http-proxy-middleware");
require("dotenv").config();

const app = express();

const CORE_API_URL = process.env.CORE_API_URL;
if (!CORE_API_URL) {
  console.error("CORE_API_URL is missing");
  process.exit(1);
}

const origins = (process.env.CORS_ORIGINS || "")
  .split(",")
  .map(s => s.trim())
  .filter(Boolean);

app.use(cors({
  origin: function (origin, cb) {
    if (!origin) return cb(null, true);
    if (origins.length === 0) return cb(null, true);
    if (origins.includes(origin)) return cb(null, true);
    return cb(new Error("Not allowed by CORS"));
  },
  credentials: true
}));

app.get("/", (req, res) => {
  res.json({ message: "MarkAi Node Gateway", health: "/health" });
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.use("/v1", createProxyMiddleware({
  target: CORE_API_URL,
  changeOrigin: true,
}));

const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => {
  console.log("Node Gateway running on port", port);
});

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// ✅ خلي استيراد CSS هنا (مش داخل router)
import "./assets/theme.css";
import "./assets/ui.css";

createApp(App).use(router).mount("#app");

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles/theme.css";
import "./assets/theme.css";
import "./assets/ui.css";




createApp(App).use(router).mount("#app");

import { createRouter, createWebHistory } from "vue-router";

import { useSession } from "../session";
import LoginView from "../views/LoginView.vue";
import NewTicketView from "../views/NewTicketView.vue";
import TicketDetailView from "../views/TicketDetailView.vue";
import TicketListView from "../views/TicketListView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/", name: "tickets", component: TicketListView },
    { path: "/tickets/new", name: "new-ticket", component: NewTicketView },
    { path: "/tickets/:id", name: "ticket", component: TicketDetailView, props: true },
  ],
});

router.beforeEach(async (to) => {
  const { loadMe } = useSession();
  const user = await loadMe();
  if (!to.meta.public && !user) return { name: "login" };
  if (to.name === "login" && user) return { name: "tickets" };
  return true;
});

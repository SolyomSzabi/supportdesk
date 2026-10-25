import { computed, ref } from "vue";

import { clearTokens, fetchMe, hasToken, login as apiLogin } from "./api/client";
import type { Me } from "./api/types";

// One shared, reactive "who is logged in" for the whole app.
const me = ref<Me | null>(null);

const loadMe = async (): Promise<Me | null> => {
  if (me.value) return me.value;
  if (!hasToken()) return null;
  try {
    me.value = await fetchMe();
  } catch {
    clearTokens();
    me.value = null;
  }
  return me.value;
};

const login = async (username: string, password: string) => {
  await apiLogin(username, password);
  me.value = await fetchMe();
};

const logout = () => {
  clearTokens();
  me.value = null;
};

export const useSession = () => ({
  me,
  isAgent: computed(() => me.value?.role === "agent"),
  loadMe,
  login,
  logout,
});

import { AuthProvider } from "react-admin";
import { AUTH_KEY, API_URL } from "./constants";

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const error = await response.json();
      return Promise.reject(error.message || "Login failed");
    }

    const { access_token } = await response.json();
    localStorage.setItem(AUTH_KEY, access_token);
    return Promise.resolve();
  },

  logout: async () => {
    localStorage.removeItem(AUTH_KEY);
    return Promise.resolve();
  },

  checkAuth: async () => {
    return localStorage.getItem(AUTH_KEY)
      ? Promise.resolve()
      : Promise.reject();
  },

  checkError: async (error) => {
    const status = error.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem(AUTH_KEY);
      return Promise.reject();
    }
    return Promise.resolve();
  },
};

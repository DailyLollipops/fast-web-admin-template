import { AuthProvider } from "react-admin";
import { API_URL } from "../constants";

const refreshToken = async () => {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  return response.ok;
};

export const authProvider: AuthProvider = {
  login: async (params) => {
    if (params?.provider === "google") {
      return new Promise((resolve, reject) => {
        const popup = window.open(
          `${API_URL}/auth/google/login?next_url=${encodeURIComponent(window.location.origin)}`,
          "GoogleLogin",
          "width=500,height=600",
        );
        if (!popup) return reject("Popup blocked");
        const listener = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return;
          if (event.data === "login-success") {
            window.removeEventListener("message", listener);
            resolve(true);
          }
        };

        window.addEventListener("message", listener);
      });
    }

    // Native login method
    const { username, password } = params;
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const error = await response.json();
      return Promise.reject(error.message || "Login failed");
    }

    return Promise.resolve();
  },

  logout: async () => {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    return Promise.resolve();
  },

  checkAuth: async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
      credentials: "include",
    });

    if (!response.ok) {
      return Promise.reject();
    }

    return Promise.resolve();
  },

  checkError: async (error) => {
    const status = error.status;
    console.log("AuthProvider checkError status:", status);

    if (status === 401) {
      await refreshToken();
      return Promise.reject();
    }

    if (status === 403) {
      return Promise.reject();
    }

    return Promise.resolve();
  },

  getIdentity: async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
      method: "GET",
      credentials: "include",
    });

    return await response.json();
  },

  canAccess: async ({ action, resource }) => {
    const response = await fetch(
      `${API_URL}/auth/check?resource=${resource}&action=${action}`,
      {
        method: "GET",
        credentials: "include",
      },
    );

    const data = await response.json();
    return data.access;
  },
};

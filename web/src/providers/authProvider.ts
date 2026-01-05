import { AuthProvider } from "react-admin";
import { AUTH_DETAILS, API_URL } from "../constants";

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
      window.location.href = `${API_URL}/auth/google/login`;
      return Promise.resolve();
    }

    const { username, password } = params;
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const loginResponse = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!loginResponse.ok) {
      const error = await loginResponse.json();
      return Promise.reject(error.message || "Login failed");
    }

    const identityResponse = await fetch(`${API_URL}/auth/me`, {
      method: "GET",
      credentials: "include",
    });

    if (!identityResponse.ok) {
      const error = await loginResponse.json();
      return Promise.reject(error.message || "Login failed");
    }

    const authDetails = await identityResponse.text();
    localStorage.setItem(AUTH_DETAILS, authDetails);

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
      const refreshed = await refreshToken();

      if (refreshed) {
        const me = await fetch(`${API_URL}/auth/me`, {
          credentials: "include",
        });

        if (me.ok) {
          const authDetails = await me.text();
          localStorage.setItem(AUTH_DETAILS, authDetails);
          return Promise.resolve();
        }
      }

      localStorage.removeItem(AUTH_DETAILS);
      return Promise.reject();
    }

    if (status === 403) {
      return Promise.reject();
    }

    return Promise.resolve();
  },

  getIdentity: async () => {
    const authCredentials = JSON.parse(localStorage.getItem(AUTH_DETAILS)!);
    return authCredentials;
  },

  canAccess: async ({ action, resource }) => {
    const authCredentials = JSON.parse(localStorage.getItem(AUTH_DETAILS)!);
    const rolePermissions = authCredentials?.permissions ?? undefined;

    if (rolePermissions == undefined) {
      return false;
    }

    for (const permission of rolePermissions) {
      if (permission === "*") {
        return true;
      }

      const [pResource, pAction] = permission.split(".");

      if (
        (pResource === resource || pResource === "*") &&
        (pAction === action || pAction === "*")
      ) {
        return true;
      }
    }

    return false;
  },
};

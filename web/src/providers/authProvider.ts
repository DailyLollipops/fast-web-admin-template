import { AuthProvider } from "react-admin";
import { AUTH_KEY, AUTH_DETAILS, API_URL } from "../constants";

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const loginResponse = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!loginResponse.ok) {
      const error = await loginResponse.json();
      return Promise.reject(error.message || "Login failed");
    }

    const { access_token } = await loginResponse.json();
    localStorage.setItem(AUTH_KEY, access_token);

    const identityResponse = await fetch(`${API_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    });

    if (!identityResponse.ok) {
      const error = await loginResponse.json();
      return Promise.reject(error.message || "Login failed");
    }

    const authDetails = await identityResponse.text();
    localStorage.setItem(AUTH_DETAILS, authDetails);
    // window.location.reload();

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

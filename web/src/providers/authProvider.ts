import { AuthProvider } from "react-admin";

import { googleLoginFlow } from "./auth/google";
import { API_URL } from "../constants";
import { nativeLoginFlow } from "./auth/native";

const refreshToken = async () => {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  return response.ok;
};

export const authProvider: AuthProvider = {
  login: async (params) => {
    const remember = params?.remember || false;

    if (params?.provider === "google") {
      return await googleLoginFlow(remember);
    }

    return await nativeLoginFlow(params.username, params.password, remember);
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

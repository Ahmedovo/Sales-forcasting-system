import axios from "axios";
import { getToken } from "@/lib/auth";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type ApiListResponse<T> = {
  items: T[];
  total: number;
};

export default api;



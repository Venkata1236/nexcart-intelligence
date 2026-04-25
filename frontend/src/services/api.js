import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export const getRecommendations = async (userId, n = 10) => {
  const response = await api.post("/recommend", { user_id: userId, n });
  return response.data;
};

export const analyzeSentiment = async (texts) => {
  const response = await api.post("/sentiment", { texts });
  return response.data;
};

export const getProductDetail = async (productId) => {
  const response = await api.get(`/product/${productId}`);
  return response.data;
};

export const queryAgent = async (userId, query) => {
  const response = await api.post("/agent/query", { user_id: userId, query });
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export default api;
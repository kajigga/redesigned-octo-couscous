import { apiClient } from "./client";

export async function placeOrder(orderData, token) {
  const result = await apiClient("/api/orders", {
    method: "POST",
    body: orderData,
    token,
  });
  return result;
}

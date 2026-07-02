import { apiClient } from "./client";

export async function fetchMenu() {
  return apiClient("/api/menu");
}

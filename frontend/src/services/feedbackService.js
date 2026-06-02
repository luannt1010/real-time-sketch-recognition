import API_BASE_URL from "./api";

export async function submitFeedback(data) {
  const response = await fetch(`${API_BASE_URL}/feedback/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.json();
}
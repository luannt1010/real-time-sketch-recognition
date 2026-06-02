import API_BASE_URL from "./api";

export async function recognizeImage(image) {
  const response = await fetch(`${API_BASE_URL}/recognize/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image }),
  });

  return response.json();
}
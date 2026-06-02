import API_BASE_URL from "./api";

export async function startCamera() {
  return fetch(`${API_BASE_URL}/camera/start/`, {
    method: "POST",
  });
}

export async function stopCamera() {
  return fetch(`${API_BASE_URL}/camera/stop/`, {
    method: "POST",
  });
}

export async function clearCamera() {
  return fetch(`${API_BASE_URL}/camera/clear/`, {
    method: "POST",
  });
}

export async function getFrame() {
  const res = await fetch(`${API_BASE_URL}/camera/frame/`);
  return res.json();
}

export async function getCanvas() {
  const res = await fetch(`${API_BASE_URL}/camera/canvas/`);
  return res.json();
}
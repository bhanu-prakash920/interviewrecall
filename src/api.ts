let csrf = "";
const unavailable =
  "Java backend is unavailable. Start it locally to use accounts.";
async function request(path: string, init?: RequestInit) {
  try {
    return await fetch("/api" + path, { credentials: "same-origin", ...init });
  } catch {
    throw new Error(unavailable);
  }
}
export async function api<T>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  if (method !== "GET" && !csrf) {
    const response = await request("/auth/csrf");
    if (
      !response.ok ||
      !response.headers.get("content-type")?.includes("application/json")
    )
      throw new Error(unavailable);
    csrf = (await response.json()).token;
    if (!csrf) throw new Error(unavailable);
  }
  const response = await request(path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(method !== "GET" ? { "X-CSRF-TOKEN": csrf } : {}),
    },
    ...(data ? { body: JSON.stringify(data) } : {}),
  });
  if (!response.ok) {
    let message = "Could not connect. Check that the Java backend is running.";
    try {
      message = (await response.json()).message || message;
    } catch {}
    if (response.status === 403) csrf = "";
    throw new Error(message);
  }
  if (path === "/auth/login" || path === "/auth/logout") csrf = "";
  if (response.status === 204) return undefined as T;
  if (!response.headers.get("content-type")?.includes("application/json"))
    throw new Error(unavailable);
  return response.json();
}

import type { GmailScanResponse, PromptCheckResponse, PromptIncident, URLResult } from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function parseJson<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.detail || data?.error || "Request failed");
  }
  return data as T;
}

export const api = {
  async health() {
    const response = await fetch(`${BASE}/health`, { cache: "no-store" });
    return parseJson<{ status: string; service: string; litellm_reachable: boolean }>(response);
  },

  async analyzeUrls(urls: string[]) {
    const response = await fetch(`${BASE}/api/url/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls }),
    });
    return parseJson<{ results: URLResult[] }>(response);
  },

  async checkPrompt(message: string, sessionId: string) {
    const response = await fetch(`${BASE}/api/prompt/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    return parseJson<PromptCheckResponse>(response);
  },

  async getPromptLog(sessionId: string) {
    const response = await fetch(`${BASE}/api/prompt/session/${sessionId}/log`, {
      cache: "no-store",
    });
    return parseJson<{ incidents: PromptIncident[]; total_blocked: number; total_safe: number }>(response);
  },

  async startGmailOAuth() {
    const response = await fetch(`${BASE}/api/gmail/oauth/start`, { cache: "no-store" });
    return parseJson<{ authorization_url: string }>(response);
  },

  async scanGmail(accessToken: string) {
    const response = await fetch(`${BASE}/api/gmail/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: accessToken }),
    });
    return parseJson<GmailScanResponse>(response);
  },
};


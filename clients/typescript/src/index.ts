export type GuardRequest = {
  agent_id?: string;
  context: string;
  tool_name: string;
  tool_input?: Record<string, unknown>;
  irreversible?: boolean;
  metadata?: Record<string, unknown>;
};

export type GuardResponse = { decision: Record<string, unknown>; trajectory_path?: string };

export class HonestAgentHttpClient {
  constructor(private readonly baseUrl: string, private readonly fetchImpl: typeof fetch = fetch) {
    if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) throw new Error("baseUrl must use HTTP(S)");
  }

  async guard(request: GuardRequest, signal?: AbortSignal): Promise<GuardResponse> {
    return this.post("/v1/guard", request, signal);
  }

  async execute(payload: Record<string, unknown>, signal?: AbortSignal): Promise<Record<string, unknown>> {
    return this.post("/v1/execute", payload, signal);
  }

  private async post(path: string, body: unknown, signal?: AbortSignal): Promise<any> {
    const response = await this.fetchImpl(new URL(path, this.baseUrl).toString(), { method: "POST", headers: { "content-type": "application/json", "accept": "application/json" }, body: JSON.stringify(body), signal });
    const data = await response.json();
    if (!response.ok) throw new Error(`HonestAgent HTTP ${response.status}: ${typeof data?.detail === "string" ? data.detail : "request failed"}`);
    return data;
  }
}

export { runConformance } from "./conformance.js";

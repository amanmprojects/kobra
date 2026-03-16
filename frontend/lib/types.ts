export type Severity = "SAFE" | "SUSPICIOUS" | "MALICIOUS" | "CRITICAL";

export type ExplanationCard = {
  module: "url" | "prompt" | "phishing";
  what_was_flagged: string;
  why_suspicious: string[];
  evidence: { fragment: string; reason: string }[];
  confidence: number;
  severity: Severity;
  recommended_action: string;
  shap_waterfall?: { feature: string; value: number; contribution: number }[] | null;
  attention_heatmap?: Record<string, number> | null;
  lime_rationale?: { word: string; influence: number }[] | null;
  attack_type?: string | null;
  intent_score?: number | null;
  layer_triggered?: "heuristic" | "similarity" | "llm_judge" | null;
};

export type RiskScore = {
  score: number;
  tier: Severity;
};

export type URLResult = {
  url: string;
  verdict: "SAFE" | "SUSPICIOUS" | "MALICIOUS";
  risk_score: RiskScore;
  virustotal: {
    engines_flagged: number;
    total_engines: number;
    categories: string[];
    unavailable: boolean;
  };
  safe_browsing: {
    flagged: boolean;
    threat_type?: string | null;
    unavailable: boolean;
  };
  xgboost_probability: number;
  shap_waterfall: { feature: string; value: number; contribution: number }[];
  explanation_card: ExplanationCard;
};

export type PromptCheckResponse = {
  safe: boolean;
  llm_response?: string | null;
  injection_detected: boolean;
  attack_type?: string | null;
  intent_score?: number | null;
  matched_trigger?: string | null;
  explanation_card?: ExplanationCard | null;
  layer_triggered?: "heuristic" | "similarity" | "llm_judge" | null;
  risk_score: RiskScore;
};

export type PromptIncident = {
  session_id: string;
  message: string;
  safe: boolean;
  attack_type?: string | null;
  intent_score?: number | null;
  created_at: string;
};

export type EmailResult = {
  id: string;
  subject: string;
  sender: string;
  sender_domain: string;
  received_at: string;
  snippet: string;
  risk_score: RiskScore;
  explanation_card: ExplanationCard;
  urls_found: number;
  urls_malicious: number;
  top_urls: string[];
};

export type GmailScanResponse = {
  emails: EmailResult[];
  scan_summary: {
    total: number;
    safe: number;
    suspicious: number;
    malicious: number;
    critical: number;
  };
};


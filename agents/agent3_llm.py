# agents/agent3_llm.py
# ── Agent 3: Local LLM via Ollama (FREE) ─────
# Uses gemma2:2b running locally — no API key needed
# Make sure Ollama is running: https://ollama.com
# Pull model once: ollama pull gemma2:2b

import json
import urllib.request
from agents.agent2_expert import ExpertResult

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:2b"


class LLMAgent:

    def __init__(self):
        if self._is_ollama_running():
            print("[Agent 3] ✅ Ollama is running — using gemma2:2b locally (FREE)")
        else:
            print("[Agent 3] ⚠️  Ollama not detected. Start it or install from https://ollama.com")

    # ── Main ──────────────────────────────────

    def generate(self, student: dict, ml_result: dict, expert_result: ExpertResult) -> dict:
        print("[Agent 3] Generating intervention plan (local LLM)...")

        if not self._is_ollama_running():
            return self._fallback(ml_result, expert_result)

        prompt = self._build_prompt(student, ml_result, expert_result)

        try:
            payload = json.dumps({
                "model":  OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 600},
            }).encode("utf-8")

            req = urllib.request.Request(
                OLLAMA_URL,
                data    = payload,
                headers = {"Content-Type": "application/json"},
                method  = "POST",
            )

            with urllib.request.urlopen(req, timeout=120) as resp:
                raw      = json.loads(resp.read().decode("utf-8"))
                response = raw.get("response", "").strip()

            result = self._parse(response)
            print(f"[Agent 3] ✅ Done — Final risk: {result.get('final_risk')}")
            return result

        except Exception as e:
            print(f"[Agent 3] Error: {e}")
            return self._fallback(ml_result, expert_result)

    # ── Prompt ────────────────────────────────

    def _build_prompt(self, student: dict, ml: dict, exp: ExpertResult) -> str:
        rules_fired = "\n".join(
            f"  [{r.severity}] {r.name}: {r.message}" for r in exp.fired_rules
        ) or "  None"

        conflict = ""
        if exp.override_ml:
            conflict = f"\nAGENT CONFLICT: {exp.override_reason}\n"

        return f"""You are an academic advisor AI. Analyze this student and give an intervention plan.
Reply ONLY with a JSON object. No explanation outside the JSON.

Student:
  1st Sem Units Approved : {student.get('Curricular_units_1st_sem_approved')}
  1st Sem Grade          : {student.get('Curricular_units_1st_sem_grade')}
  2nd Sem Units Approved : {student.get('Curricular_units_2nd_sem_approved')}
  2nd Sem Grade          : {student.get('Curricular_units_2nd_sem_grade')}
  Tuition Up To Date     : {bool(student.get('Tuition_fees_up_to_date'))}
  Scholarship Holder     : {bool(student.get('Scholarship_holder'))}
  Age at Enrollment      : {student.get('Age_at_enrollment')}
  Debtor                 : {bool(student.get('Debtor'))}

Agent 1 ML Score : {ml['risk_score']}/100 → {ml['verdict']}
Agent 2 Expert   : {exp.risk_category}
Rules Fired:
{rules_fired}
{conflict}

Reply with ONLY this JSON, nothing else:
{{
  "final_risk": "LOW or MEDIUM or HIGH or CRITICAL",
  "summary": "one sentence about this student",
  "interventions": [
    {{"step": 1, "action": "...", "when": "..."}},
    {{"step": 2, "action": "...", "when": "..."}},
    {{"step": 3, "action": "...", "when": "..."}}
  ],
  "message_to_student": "one encouraging sentence to the student",
  "escalate": true or false
}}"""

    # ── Parse LLM response ────────────────────

    def _parse(self, text: str) -> dict:
        try:
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {
            "final_risk":         "UNKNOWN",
            "summary":            text[:200],
            "interventions":      [],
            "message_to_student": "Please speak with your academic advisor.",
            "escalate":           True,
        }

    # ── Helpers ───────────────────────────────

    def _is_ollama_running(self) -> bool:
        try:
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            return True
        except:
            return False

    def _fallback(self, ml: dict, exp: ExpertResult) -> dict:
        return {
            "final_risk":         exp.risk_category,
            "summary":            f"ML score: {ml['risk_score']}/100. Expert: {exp.risk_category}. {len(exp.fired_rules)} rules fired.",
            "interventions":      [{"step": i+1, "action": a, "when": "ASAP"}
                                   for i, a in enumerate(exp.actions[:3])],
            "message_to_student": "Please visit your academic advisor for personalized support.",
            "escalate":           exp.risk_category in ("HIGH", "CRITICAL"),
        }
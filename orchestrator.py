# orchestrator.py
import json, os
from datetime import datetime
from agents.agent1_ml     import MLAgent
from agents.agent2_expert import ExpertSystemAgent
from agents.agent3_llm    import LLMAgent


class Orchestrator:

    def __init__(self):
        self.agent1 = MLAgent()
        self.agent2 = ExpertSystemAgent()
        self.agent3 = LLMAgent()

    def analyze(self, student: dict) -> dict:
        sid = student.get("student_id", "?")
        print("\n" + "="*55)
        print(f"  Analyzing Student: {sid}")
        print("="*55)

        blackboard = {"student_id": sid, "timestamp": datetime.now().isoformat()}

        print("\n[Step 1/3] ML Risk Scoring")
        ml_result = self.agent1.predict(student)
        blackboard["agent1"] = ml_result

        print("\n[Step 2/3] Expert System")
        expert_result = self.agent2.evaluate(student, ml_result)
        blackboard["agent2"] = {
            "risk_category":   expert_result.risk_category,
            "rules_fired":     [{"id": r.id, "name": r.name,
                                  "severity": r.severity, "message": r.message}
                                 for r in expert_result.fired_rules],
            "reasoning_chain": expert_result.reasoning_chain,
            "priority_flags":  expert_result.priority_flags,
            "actions":         expert_result.actions,
            "override_ml":     expert_result.override_ml,
            "override_reason": expert_result.override_reason,
        }

        if expert_result.override_ml:
            print(f"\n  ⚠️  CONFLICT: ML={ml_result['verdict']} vs Expert={expert_result.risk_category}")
            print(f"       {expert_result.override_reason}")

        print("\n[Step 3/3] LLM Intervention Planner")
        llm_result = self.agent3.generate(student, ml_result, expert_result)
        blackboard["agent3"] = llm_result

        blackboard["final"] = {
            "student_id": sid,
            "ml_score":   ml_result["risk_score"],
            "expert":     expert_result.risk_category,
            "final_risk": llm_result.get("final_risk", expert_result.risk_category),
            "conflict":   expert_result.override_ml,
            "escalate":   llm_result.get("escalate", False),
        }

        self._print_report(blackboard)
        self._save(blackboard, sid)
        return blackboard

    def _print_report(self, bb):
        f  = bb["final"]
        a3 = bb["agent3"]
        print("\n" + "="*55)
        print("  FINAL REPORT")
        print("="*55)
        print(f"  Student     : {f['student_id']}")
        print(f"  ML Score    : {f['ml_score']}/100")
        print(f"  Expert      : {f['expert']}")
        print(f"  Final Risk  : {f['final_risk']}")
        print(f"  Conflict    : {'YES ⚠️' if f['conflict'] else 'No ✅'}")
        print(f"  Escalate    : {'YES 🚨' if f['escalate'] else 'No'}")
        if a3.get("summary"):
            print(f"\n  Summary: {a3['summary']}")
        if a3.get("interventions"):
            print("\n  Interventions:")
            for s in a3["interventions"]:
                print(f"    {s.get('step')}. [{s.get('when')}] {s.get('action')}")
        if a3.get("message_to_student"):
            print(f"\n  To Student: {a3['message_to_student']}")
        print("="*55)

    def _save(self, bb, sid):
        os.makedirs("outputs", exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"outputs/report_{sid}_{ts}.json"
        with open(path, "w") as f:
            json.dump(bb, f, indent=2)
        print(f"\n  Report saved → {path}")
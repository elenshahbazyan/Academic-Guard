# agents/agent2_expert.py
# ── Agent 2: Forward-Chaining Expert System ──

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Rule:
    id:       str
    name:     str
    severity: str
    message:  str
    action:   str


@dataclass
class ExpertResult:
    risk_category:    str
    fired_rules:      List[Rule]
    reasoning_chain:  List[str]
    priority_flags:   List[str]
    actions:          List[str]
    override_ml:      bool
    override_reason:  Optional[str]


class ExpertSystemAgent:

    def evaluate(self, student: dict, ml_result: dict) -> ExpertResult:
        print("[Agent 2] Running expert rule engine...")

        def get(key, default=0):
            return student.get(key, default)

        fired = []
        flags = []

        # ── Exact column names from UCI dataset ──
        sem1_approved  = get("Curricular_units_1st_sem_approved")
        sem1_grade     = get("Curricular_units_1st_sem_grade")
        sem1_enrolled  = get("Curricular_units_1st_sem_enrolled")
        sem1_evaluated = get("Curricular_units_1st_sem_evaluations")
        sem2_approved  = get("Curricular_units_2nd_sem_approved")
        sem2_grade     = get("Curricular_units_2nd_sem_grade")
        sem2_enrolled  = get("Curricular_units_2nd_sem_enrolled")
        tuition_ok     = get("Tuition_fees_up_to_date", 1)
        scholarship    = get("Scholarship_holder", 0)
        debtor         = get("Debtor", 0)
        age            = get("Age_at_enrollment", 20)
        admission      = get("Admission_grade", 150)
        displaced      = get("Displaced", 0)

        # Derived
        sem1_ratio = (sem1_approved / sem1_enrolled) if sem1_enrolled > 0 else 1
        sem2_ratio = (sem2_approved / sem2_enrolled) if sem2_enrolled > 0 else 1

        rule_defs = [
            # ── Academic performance rules ────────
            ("R01", "No Units Approved Sem 1",      "CRITICAL",
             sem1_enrolled > 0 and sem1_approved == 0,
             f"Enrolled in {int(sem1_enrolled)} units but approved 0 in semester 1",
             "Immediate academic intervention required"),

            ("R02", "Low Approval Rate Sem 1",      "HIGH",
             sem1_enrolled > 0 and 0 < sem1_ratio < 0.5,
             f"Only {int(sem1_approved)}/{int(sem1_enrolled)} units approved in sem 1 ({sem1_ratio*100:.0f}%)",
             "Academic support and tutoring referral"),

            ("R03", "No Units Approved Sem 2",      "CRITICAL",
             sem2_enrolled > 0 and sem2_approved == 0,
             f"Enrolled in {int(sem2_enrolled)} units but approved 0 in semester 2",
             "Emergency intervention — escalate to advisor"),

            ("R04", "Low Approval Rate Sem 2",      "HIGH",
             sem2_enrolled > 0 and 0 < sem2_ratio < 0.5,
             f"Only {int(sem2_approved)}/{int(sem2_enrolled)} units approved in sem 2 ({sem2_ratio*100:.0f}%)",
             "Schedule advisor meeting this week"),

            ("R05", "Very Low Grade Sem 1",         "HIGH",
             sem1_grade > 0 and sem1_grade < 10,
             f"Semester 1 average grade = {sem1_grade:.1f} (below 10/20)",
             "Tutoring center referral"),

            ("R06", "Very Low Grade Sem 2",         "HIGH",
             sem2_grade > 0 and sem2_grade < 10,
             f"Semester 2 average grade = {sem2_grade:.1f} (below 10/20)",
             "Immediate academic support plan"),

            ("R07", "Failed Both Semesters",        "CRITICAL",
             sem1_enrolled > 0 and sem2_enrolled > 0
             and sem1_approved == 0 and sem2_approved == 0,
             "Zero units approved across both semesters",
             "Emergency multi-department intervention"),

            ("R08", "Not Taking Evaluations Sem 1", "HIGH",
             sem1_enrolled > 0 and sem1_evaluated == 0,
             "Student enrolled but took no evaluations in semester 1 — disengaged",
             "Urgent outreach — student may have abandoned studies"),

            # ── Financial rules ───────────────────
            ("R09", "Tuition Not Paid",             "HIGH",
             tuition_ok == 0,
             "Tuition fees are overdue",
             "Financial aid office referral"),

            ("R10", "Debtor",                       "MEDIUM",
             debtor == 1,
             "Student flagged as a debtor",
             "Financial counseling referral"),

            ("R11", "Financial + Academic Crisis",  "CRITICAL",
             tuition_ok == 0 and sem1_approved == 0 and sem1_enrolled > 0,
             "Tuition overdue AND failing academically",
             "Priority case — multi-department emergency intervention"),

            # ── Combined risk rules ───────────────
            ("R12", "Scholarship at Risk",          "HIGH",
             scholarship == 1 and ml_result["risk_score"] > 55,
             f"Scholarship student with ML risk score {ml_result['risk_score']}/100",
             "Notify scholarship office + academic advisor immediately"),

            ("R13", "Mature Student Struggling",    "MEDIUM",
             age > 30 and ml_result["risk_score"] > 50,
             f"Mature student (age {int(age)}) showing academic risk",
             "Adult learner support program referral"),

            ("R14", "Low Admission + Low Performance", "HIGH",
             admission < 100 and sem1_grade > 0 and sem1_grade < 12,
             f"Low admission grade ({admission:.0f}) and low sem 1 grade ({sem1_grade:.1f})",
             "Academic foundations program referral"),
        ]

        for rid, name, severity, condition, message, action in rule_defs:
            if condition:
                fired.append(Rule(id=rid, name=name, severity=severity,
                                  message=message, action=action))

        # ── Priority flags ─────────────────────
        if scholarship == 1:
            flags.append("⚑ Scholarship Holder — Priority Support")
        if tuition_ok == 0:
            flags.append("⚑ Tuition Overdue — Financial Risk")
        if displaced == 1:
            flags.append("⚑ Displaced Student — May Need Extra Support")

        risk_category = self._category(fired)
        reasoning     = [f"[{r.severity}] {r.name}: {r.message}" for r in fired]
        actions       = list({r.action for r in fired})
        override, reason = self._check_override(risk_category, ml_result["verdict"], fired)

        result = ExpertResult(
            risk_category   = risk_category,
            fired_rules     = fired,
            reasoning_chain = reasoning,
            priority_flags  = flags,
            actions         = actions,
            override_ml     = override,
            override_reason = reason,
        )

        status = "⚠️  OVERRIDE" if override else "✅ Aligned"
        print(f"[Agent 2] Category: {risk_category} | Rules fired: {len(fired)} | {status}")
        if fired:
            for r in fired:
                print(f"           [{r.severity}] {r.name}: {r.message}")
        return result

    def _category(self, fired):
        if not fired: return "LOW"
        s = [r.severity for r in fired]
        if "CRITICAL" in s: return "CRITICAL"
        if "HIGH"     in s: return "HIGH"
        if "MEDIUM"   in s: return "MEDIUM"
        return "LOW"

    def _check_override(self, expert, ml, fired):
        level = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        diff  = level.get(expert, 1) - level.get(ml, 1)
        if abs(diff) >= 2:
            direction = "higher" if diff > 0 else "lower"
            critical  = [r.name for r in fired if r.severity in ("CRITICAL", "HIGH")]
            return True, f"Expert rates risk {direction} than ML. Key rules: {', '.join(critical[:2])}"
        return False, None
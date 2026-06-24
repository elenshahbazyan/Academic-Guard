# demo.py  ← Run this for live professor demo
# ─────────────────────────────────────────────
# Interactive CLI — type student values, see all 3 agents work live

from orchestrator import Orchestrator
from utils.data_loader import load_dataset


def print_header():
    print("""
╔══════════════════════════════════════════════════════╗
║           AcademicGuard — LIVE DEMO MODE             ║
║   Type student data → watch 3 agents analyze it     ║
╚══════════════════════════════════════════════════════╝""")


def ask(question, default, cast=float):
    """Ask a question with a default value."""
    try:
        raw = input(f"  {question} [default: {default}]: ").strip()
        return cast(raw) if raw else default
    except ValueError:
        return default


def ask_yes_no(question, default=1):
    raw = input(f"  {question} [1=Yes / 0=No, default: {default}]: ").strip()
    if raw in ("0", "1"):
        return int(raw)
    return default


def collect_student_input():
    print("\n" + "─"*55)
    print("  📋 Enter Student Information")
    print("─"*55)
    print("  (Press ENTER to use default values)\n")

    student_id = input("  Student ID [e.g. STU001]: ").strip() or "STU_DEMO"

    print("\n  ── Academic Performance ──")
    sem1_enrolled  = ask("Courses enrolled in Semester 1", 6, int)
    sem1_approved  = ask("Courses APPROVED in Semester 1", 0, int)
    sem1_grade     = ask("Average grade Semester 1 (0–20)", 8.0)
    sem1_evals     = ask("Evaluations taken Semester 1", 0, int)

    sem2_enrolled  = ask("Courses enrolled in Semester 2", 6, int)
    sem2_approved  = ask("Courses APPROVED in Semester 2", 1, int)
    sem2_grade     = ask("Average grade Semester 2 (0–20)", 9.0)

    print("\n  ── Financial Status ──")
    tuition_ok     = ask_yes_no("Tuition fees up to date?", 1)
    debtor         = ask_yes_no("Is student a debtor?", 0)
    scholarship    = ask_yes_no("Scholarship holder?", 0)

    print("\n  ── Background ──")
    age            = ask("Age at enrollment", 22, int)
    admission      = ask("Admission grade (0–200)", 120.0)
    displaced      = ask_yes_no("Displaced student (from another region)?", 0)

    student = {
        "student_id":                              student_id,
        "Curricular_units_1st_sem_enrolled":       sem1_enrolled,
        "Curricular_units_1st_sem_approved":       sem1_approved,
        "Curricular_units_1st_sem_grade":          sem1_grade,
        "Curricular_units_1st_sem_evaluations":    sem1_evals,
        "Curricular_units_1st_sem_credited":       0,
        "Curricular_units_1st_sem_without_evaluations": 0,
        "Curricular_units_2nd_sem_enrolled":       sem2_enrolled,
        "Curricular_units_2nd_sem_approved":       sem2_approved,
        "Curricular_units_2nd_sem_grade":          sem2_grade,
        "Curricular_units_2nd_sem_evaluations":    sem2_evals if (sem2_evals := sem1_evals) else 0,
        "Curricular_units_2nd_sem_credited":       0,
        "Curricular_units_2nd_sem_without_evaluations": 0,
        "Tuition_fees_up_to_date":                 tuition_ok,
        "Debtor":                                  debtor,
        "Scholarship_holder":                      scholarship,
        "Age_at_enrollment":                       age,
        "Admission_grade":                         admission,
        "Displaced":                               displaced,
        # Fill remaining features with neutral values
        "Marital_Status":        1,
        "Application_mode":      1,
        "Application_order":     1,
        "Course":                1,
        "Previous_qualification_grade": admission,
        "Nacionality":           1,
        "Mothers_qualification": 1,
        "Fathers_qualification": 1,
        "Mothers_occupation":    1,
        "Fathers_occupation":    1,
        "Gender":                1,
        "International":         0,
        "Unemployment_rate":     10.0,
        "Inflation_rate":        1.5,
        "GDP":                   0.0,
    }
    return student


def show_presets():
    """Preset student profiles for quick demo."""
    print("""
  ── Quick Presets (for demo speed) ──────────────
  1. 🔴 CRITICAL student — failing everything, tuition overdue
  2. 🟡 MEDIUM student  — some failures, financial stress
  3. 🟢 LOW student     — good grades, all paid
  4. ✏️  Custom input   — enter your own values
  ─────────────────────────────────────────────────""")

    choice = input("  Choose [1/2/3/4]: ").strip()

    if choice == "1":
        return {
            "student_id": "STU_CRITICAL",
            "Curricular_units_1st_sem_enrolled": 7,
            "Curricular_units_1st_sem_approved": 0,
            "Curricular_units_1st_sem_grade": 0.0,
            "Curricular_units_1st_sem_evaluations": 0,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 7,
            "Curricular_units_2nd_sem_enrolled": 7,
            "Curricular_units_2nd_sem_approved": 0,
            "Curricular_units_2nd_sem_grade": 0.0,
            "Curricular_units_2nd_sem_evaluations": 0,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 7,
            "Tuition_fees_up_to_date": 0,
            "Debtor": 1,
            "Scholarship_holder": 0,
            "Age_at_enrollment": 38,
            "Admission_grade": 95.0,
            "Displaced": 1,
            "Marital_Status": 1, "Application_mode": 1, "Application_order": 1,
            "Course": 1, "Previous_qualification_grade": 95.0, "Nacionality": 1,
            "Mothers_qualification": 1, "Fathers_qualification": 1,
            "Mothers_occupation": 1, "Fathers_occupation": 1,
            "Gender": 1, "International": 0,
            "Unemployment_rate": 13.9, "Inflation_rate": 3.0, "GDP": -2.0,
        }
    elif choice == "2":
        return {
            "student_id": "STU_MEDIUM",
            "Curricular_units_1st_sem_enrolled": 6,
            "Curricular_units_1st_sem_approved": 2,
            "Curricular_units_1st_sem_grade": 11.0,
            "Curricular_units_1st_sem_evaluations": 4,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 2,
            "Curricular_units_2nd_sem_enrolled": 6,
            "Curricular_units_2nd_sem_approved": 3,
            "Curricular_units_2nd_sem_grade": 10.5,
            "Curricular_units_2nd_sem_evaluations": 5,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 1,
            "Tuition_fees_up_to_date": 0,
            "Debtor": 1,
            "Scholarship_holder": 0,
            "Age_at_enrollment": 25,
            "Admission_grade": 110.0,
            "Displaced": 0,
            "Marital_Status": 1, "Application_mode": 1, "Application_order": 1,
            "Course": 1, "Previous_qualification_grade": 110.0, "Nacionality": 1,
            "Mothers_qualification": 1, "Fathers_qualification": 1,
            "Mothers_occupation": 1, "Fathers_occupation": 1,
            "Gender": 0, "International": 0,
            "Unemployment_rate": 10.8, "Inflation_rate": 1.4, "GDP": 1.0,
        }
    elif choice == "3":
        return {
            "student_id": "STU_LOW",
            "Curricular_units_1st_sem_enrolled": 6,
            "Curricular_units_1st_sem_approved": 6,
            "Curricular_units_1st_sem_grade": 14.5,
            "Curricular_units_1st_sem_evaluations": 6,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 0,
            "Curricular_units_2nd_sem_enrolled": 6,
            "Curricular_units_2nd_sem_approved": 6,
            "Curricular_units_2nd_sem_grade": 15.0,
            "Curricular_units_2nd_sem_evaluations": 6,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 0,
            "Tuition_fees_up_to_date": 1,
            "Debtor": 0,
            "Scholarship_holder": 1,
            "Age_at_enrollment": 19,
            "Admission_grade": 160.0,
            "Displaced": 0,
            "Marital_Status": 1, "Application_mode": 1, "Application_order": 1,
            "Course": 1, "Previous_qualification_grade": 160.0, "Nacionality": 1,
            "Mothers_qualification": 4, "Fathers_qualification": 4,
            "Mothers_occupation": 2, "Fathers_occupation": 2,
            "Gender": 0, "International": 0,
            "Unemployment_rate": 9.4, "Inflation_rate": 1.4, "GDP": 1.74,
        }
    else:
        return collect_student_input()


def main():
    print_header()

    # ── Load & train once ──────────────────────
    print("\n⏳ Loading dataset and training Agent 1 (one time only)...")
    orc = Orchestrator()
    df, feature_columns = load_dataset()
    orc.agent1.train(df, feature_columns)
    print("\n✅ System ready!\n")

    # ── Demo loop ──────────────────────────────
    while True:
        print("\n" + "═"*55)
        print("  Ready to analyze a student.")
        print("═"*55)

        student = show_presets()

        print(f"\n⏳ Running 3-agent pipeline for: {student['student_id']}...")
        input("\n  Press ENTER to start analysis... ")

        orc.analyze(student)

        again = input("\n\n  Analyze another student? [y/n]: ").strip().lower()
        if again != "y":
            print("\n  Thank you for using AcademicGuard! 🎓\n")
            break


if __name__ == "__main__":
    main()
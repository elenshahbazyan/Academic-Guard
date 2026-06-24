# main.py  ← Run this in PyCharm

from orchestrator import Orchestrator
from utils.data_loader import load_dataset, get_sample_student
from config.settings import TARGET_COLUMN


def find_interesting_students(df, feature_columns):
    """Find students that will actually trigger expert rules."""

    # Student 1: Worst dropout — 0 units approved in both sems
    col_sem1 = next((c for c in feature_columns if "1st_sem_approved" in c), None)
    col_sem2 = next((c for c in feature_columns if "2nd_sem_approved" in c), None)
    col_tuition = next((c for c in feature_columns if "tuition" in c.lower()), None)

    # High risk: dropout with 0 approved units
    if col_sem1 and col_sem2:
        worst = df[
            (df[TARGET_COLUMN] == 1) &
            (df[col_sem1] == 0) &
            (df[col_sem2] == 0)
        ]
        if len(worst) > 0:
            s1 = worst.iloc[0].to_dict()
            s1["student_id"] = "STU_HIGH_RISK"
        else:
            s1 = get_sample_student(df, feature_columns, at_risk=True)
    else:
        s1 = get_sample_student(df, feature_columns, at_risk=True)

    # Medium risk: dropout with tuition overdue
    if col_tuition:
        medium = df[
            (df[TARGET_COLUMN] == 1) &
            (df[col_tuition] == 0)
        ]
        if len(medium) > 0:
            s2 = medium.iloc[3].to_dict()
            s2["student_id"] = "STU_MEDIUM_RISK"
        else:
            s2 = get_sample_student(df, feature_columns, at_risk=True)
    else:
        s2 = get_sample_student(df, feature_columns, at_risk=True)

    # Low risk: graduate with good grades
    if col_sem1:
        best = df[
            (df[TARGET_COLUMN] == 0) &
            (df[col_sem1] >= 5)
        ]
        if len(best) > 0:
            s3 = best.iloc[0].to_dict()
            s3["student_id"] = "STU_LOW_RISK"
        else:
            s3 = get_sample_student(df, feature_columns, at_risk=False)
    else:
        s3 = get_sample_student(df, feature_columns, at_risk=False)

    return s1, s2, s3


def main():
    print("""
╔══════════════════════════════════════════╗
║        AcademicGuard — MAS v2.0          ║
║  Dataset: UCI Predict Student Dropout    ║
║  Agent 1: ML Ensemble (RF+XGB+LR)        ║
║  Agent 2: Expert System (Rules)          ║
║  Agent 3: Ollama gemma2:2b (FREE)        ║
╚══════════════════════════════════════════╝
    """)

    orc = Orchestrator()

    # ── Load dataset & train Agent 1 ──────────
    df, feature_columns = load_dataset()
    orc.agent1.train(df, feature_columns)

    # ── Find meaningful test students ─────────
    s_high, s_medium, s_low = find_interesting_students(df, feature_columns)

    print("\n>>> TEST 1: High-risk dropout student (0 units approved)")
    orc.analyze(s_high)

    print("\n>>> TEST 2: Medium-risk student (tuition overdue)")
    orc.analyze(s_medium)

    print("\n>>> TEST 3: Low-risk graduate student")
    orc.analyze(s_low)


if __name__ == "__main__":
    main()
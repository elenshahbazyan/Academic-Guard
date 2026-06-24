# config/settings.py

# These are the most predictive features from the UCI dataset
FEATURE_COLUMNS = [
    "Curricular_units_1st_sem_approved",
    "Curricular_units_1st_sem_grade",
    "Curricular_units_2nd_sem_approved",
    "Curricular_units_2nd_sem_grade",
    "Curricular_units_1st_sem_enrolled",
    "Curricular_units_2nd_sem_enrolled",
    "Tuition_fees_up_to_date",
    "Scholarship_holder",
    "Age_at_enrollment",
    "Admission_grade",
    "Previous_qualification_grade",
    "Debtor",
    "Gender",
    "Displaced",
]

TARGET_COLUMN = "at_risk"   # 1 = Dropout, 0 = Graduate/Enrolled
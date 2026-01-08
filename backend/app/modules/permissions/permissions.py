from enum import Enum


class PermissionCode(str, Enum):
    # Academic Curriculum
    ACADEMIC_CURRICULUM_ALL = "academic.curriculum.*"
    ACADEMIC_CURRICULUM_VIEW = "academic.curriculum.view"
    ACADEMIC_CURRICULUM_ADD = "academic.curriculum.add"
    ACADEMIC_CURRICULUM_EDIT = "academic.curriculum.edit"
    ACADEMIC_CURRICULUM_DELETE = "academic.curriculum.delete"

    # Academic Curriculum Content
    ACADEMIC_CURRICULUM_CONTENT_ALL = "academic.curriculum_content.*"
    ACADEMIC_CURRICULUM_CONTENT_VIEW = "academic.curriculum_content.view"
    ACADEMIC_CURRICULUM_CONTENT_ADD = "academic.curriculum_content.add"
    ACADEMIC_CURRICULUM_CONTENT_EDIT = "academic.curriculum_content.edit"
    ACADEMIC_CURRICULUM_CONTENT_DELETE = "academic.curriculum_content.delete"

    # Academic Exams
    ACADEMIC_EXAMS_ALL = "academic.exams.*"
    ACADEMIC_EXAMS_VIEW = "academic.exams.view"
    ACADEMIC_EXAMS_ADD = "academic.exams.add"
    ACADEMIC_EXAMS_EDIT = "academic.exams.edit"
    ACADEMIC_EXAMS_DELETE = "academic.exams.delete"

    # Academic Classes
    ACADEMIC_CLASSES_ALL = "academic.classes.*"
    ACADEMIC_CLASSES_VIEW = "academic.classes.view"
    ACADEMIC_CLASSES_ADD = "academic.classes.add"
    ACADEMIC_CLASSES_EDIT = "academic.classes.edit"
    ACADEMIC_CLASSES_DELETE = "academic.classes.delete"

    # Academic Question Bank
    ACADEMIC_QUESTION_BANK_ALL = "academic.question_bank.*"
    ACADEMIC_QUESTION_BANK_VIEW = "academic.question_bank.view"
    ACADEMIC_QUESTION_BANK_ADD = "academic.question_bank.add"
    ACADEMIC_QUESTION_BANK_EDIT = "academic.question_bank.edit"
    ACADEMIC_QUESTION_BANK_DELETE = "academic.question_bank.delete"

    # Financial Invoices
    FINANCIAL_INVOICES_ALL = "financial.invoices.*"
    FINANCIAL_INVOICES_PAY = "financial.invoices.pay"

    # Financial Payments
    FINANCIAL_PAYMENTS_ALL = "financial.payments.*"
    FINANCIAL_PAYMENTS_VIEW = "financial.payments.view"

    # Financial Subscriptions
    FINANCIAL_SUBSCRIPTIONS_ALL = "financial.subscriptions.*"
    FINANCIAL_SUBSCRIPTIONS_VIEW = "financial.subscriptions.view"
    FINANCIAL_SUBSCRIPTIONS_ADD = "financial.subscriptions.add"
    FINANCIAL_SUBSCRIPTIONS_EDIT = "financial.subscriptions.edit"
    FINANCIAL_SUBSCRIPTIONS_DELETE = "financial.subscriptions.delete"

    # Financial Accounts
    FINANCIAL_ACCOUNTS_ALL = "financial.accounts.*"
    FINANCIAL_ACCOUNTS_VIEW = "financial.accounts.view"
    FINANCIAL_ACCOUNTS_ADD = "financial.accounts.add"
    FINANCIAL_ACCOUNTS_EDIT = "financial.accounts.edit"
    FINANCIAL_ACCOUNTS_DELETE = "financial.accounts.delete"

    # Financial Expenses
    FINANCIAL_EXPENSES_ALL = "financial.expenses.*"
    FINANCIAL_EXPENSES_VIEW = "financial.expenses.view"
    FINANCIAL_EXPENSES_ADD = "financial.expenses.add"
    FINANCIAL_EXPENSES_EDIT = "financial.expenses.edit"
    FINANCIAL_EXPENSES_DELETE = "financial.expenses.delete"

    # Communication Management
    COMMUNICATION_MANAGEMENT_ALL = "communication.management.*"
    COMMUNICATION_MANAGEMENT_CONTACT = "communication.management.contact"

    # Communication Supervisor
    COMMUNICATION_SUPERVISOR_ALL = "communication.supervisor.*"
    COMMUNICATION_SUPERVISOR_CONTACT = "communication.supervisor.contact"

    # Communication Announcements
    COMMUNICATION_ANNOUNCEMENTS_ALL = "communication.announcements.*"
    COMMUNICATION_ANNOUNCEMENTS_SEND = "communication.announcements.send"

    # Communication Messages
    COMMUNICATION_MESSAGES_ALL = "communication.messages.*"
    COMMUNICATION_MESSAGES_SEND = "communication.messages.send"

    # Teacher Management
    TEACHER_MANAGEMENT_ALL = "teacher.management.*"
    TEACHER_MANAGEMENT_VIEW = "teacher.management.view"
    TEACHER_MANAGEMENT_ADD = "teacher.management.add"
    TEACHER_MANAGEMENT_EDIT = "teacher.management.edit"
    TEACHER_MANAGEMENT_DELETE = "teacher.management.delete"

    # Teacher Attendance
    ATTENDANCE_TEACHER_ALL = "attendance.teacher.*"
    ATTENDANCE_TEACHER_VIEW = "attendance.teacher.view"
    ATTENDANCE_TEACHER_ADD = "attendance.teacher.add"
    ATTENDANCE_TEACHER_EDIT = "attendance.teacher.edit"
    ATTENDANCE_TEACHER_DELETE = "attendance.teacher.delete"

    # Teacher Evaluation
    EVALUATION_TEACHER_ALL = "evaluation.teacher.*"
    EVALUATION_TEACHER_VIEW = "evaluation.teacher.view"
    EVALUATION_TEACHER_ADD = "evaluation.teacher.add"
    EVALUATION_TEACHER_EDIT = "evaluation.teacher.edit"
    EVALUATION_TEACHER_DELETE = "evaluation.teacher.delete"

    # Student Evaluation
    EVALUATION_STUDENT_ALL = "evaluation.student.*"
    EVALUATION_STUDENT_VIEW = "evaluation.student.view"
    EVALUATION_STUDENT_ADD = "evaluation.student.add"
    EVALUATION_STUDENT_EDIT = "evaluation.student.edit"

    # Teacher Training
    TRAINING_TEACHER_ALL = "training.teacher.*"
    TRAINING_TEACHER_VIEW = "training.teacher.view"
    TRAINING_TEACHER_ADD = "training.teacher.add"
    TRAINING_TEACHER_EDIT = "training.teacher.edit"
    TRAINING_TEACHER_DELETE = "training.teacher.delete"

    # Reports
    REPORTS_ATTENDANCE_VIEW = "reports.attendance.view"
    REPORTS_EVALUATIONS_VIEW = "reports.evaluations.view"
    REPORTS_FINANCE_VIEW = "reports.finance.view"
    REPORTS_TEACHERS_VIEW = "reports.teachers.view"
    REPORTS_STAFF_VIEW = "reports.staff.view"

    # System Roles
    SYSTEM_ROLES_ALL = "system.roles.*"
    SYSTEM_ROLES_VIEW = "system.roles.view"
    SYSTEM_ROLES_ADD = "system.roles.add"
    SYSTEM_ROLES_EDIT = "system.roles.edit"
    SYSTEM_ROLES_DELETE = "system.roles.delete"

    # System Role Permissions
    SYSTEM_ROLE_PERMISSIONS_ALL = "system.role_permissions.*"
    SYSTEM_ROLE_PERMISSIONS_MANAGE = "system.role_permissions.manage"

    # System Branches
    SYSTEM_BRANCHES_ALL = "system.branches.*"
    SYSTEM_BRANCHES_VIEW = "system.branches.view"
    SYSTEM_BRANCHES_ADD = "system.branches.add"
    SYSTEM_BRANCHES_EDIT = "system.branches.edit"

    # System Staff
    SYSTEM_STAFF_ALL = "system.staff.*"
    SYSTEM_STAFF_VIEW = "system.staff.view"
    SYSTEM_STAFF_ADD = "system.staff.add"
    SYSTEM_STAFF_EDIT = "system.staff.edit"

    # System Assignments
    SYSTEM_ASSIGNMENTS_ALL = "system.assignments.*"
    SYSTEM_ASSIGNMENTS_VIEW = "system.assignments.view"
    SYSTEM_ASSIGNMENTS_ADD = "system.assignments.add"
    SYSTEM_ASSIGNMENTS_EDIT = "system.assignments.edit"
    SYSTEM_ASSIGNMENTS_DELETE = "system.assignments.delete"

    # System Teachers
    SYSTEM_TEACHERS_ALL = "system.teachers.*"
    SYSTEM_TEACHERS_VIEW = "system.teachers.view"
    SYSTEM_TEACHERS_ADD = "system.teachers.add"
    SYSTEM_TEACHERS_EDIT = "system.teachers.edit"
    SYSTEM_TEACHERS_DELETE = "system.teachers.delete"

    # System Student
    SYSTEM_STUDENTS_ALL = "system.students.*"
    SYSTEM_STUDENTS_VIEW = "system.students.view"
    SYSTEM_STUDENTS_ADD = "system.students.add"
    SYSTEM_STUDENTS_EDIT = "system.students.edit"
    SYSTEM_STUDENTS_DELETE = "system.students.delete"
    SYSTEM_STUDENTS_APPROVE = "system.students.approve"
    SYSTEM_STUDENTS_REJECT = "system.students.reject"

    # System Parents
    SYSTEM_PARENTS_ALL = "system.parents.*"
    SYSTEM_PARENTS_VIEW = "system.parents.view"
    SYSTEM_PARENTS_ADD = "system.parents.add"
    SYSTEM_PARENTS_EDIT = "system.parents.edit"
    SYSTEM_PARENTS_DELETE = "system.parents.delete"
    SYSTEM_PARENTS_LINK_CHILD = "system.parents.link_child"
    SYSTEM_PARENTS_UNLINK_CHILD = "system.parents.unlink_child"

    # Penalty Staff
    PENALTY_STAFF_ALL = "penalty.staff.*"
    PENALTY_STAFF_VIEW = "penalty.staff.view"
    PENALTY_STAFF_ADD = "penalty.staff.add"
    PENALTY_STAFF_EDIT = "penalty.staff.edit"
    PENALTY_STAFF_DELETE = "penalty.staff.delete"

    # Penalty Teacher
    PENALTY_TEACHER_ALL = "penalty.teacher.*"
    PENALTY_TEACHER_VIEW = "penalty.teacher.view"
    PENALTY_TEACHER_ADD = "penalty.teacher.add"
    PENALTY_TEACHER_EDIT = "penalty.teacher.edit"
    PENALTY_TEACHER_DELETE = "penalty.teacher.delete"

    # Salary Staff
    SALARY_STAFF_ALL = "salary.staff.*"
    SALARY_STAFF_VIEW = "salary.staff.view"
    SALARY_STAFF_ADD = "salary.staff.add"
    SALARY_STAFF_EDIT = "salary.staff.edit"
    SALARY_STAFF_DELETE = "salary.staff.delete"
    SALARY_STAFF_APPROVE = "salary.staff.approve"

    # Salary Teacher
    SALARY_TEACHER_ALL = "salary.teacher.*"
    SALARY_TEACHER_VIEW = "salary.teacher.view"
    SALARY_TEACHER_ADD = "salary.teacher.add"
    SALARY_TEACHER_EDIT = "salary.teacher.edit"
    SALARY_TEACHER_DELETE = "salary.teacher.delete"
    SALARY_TEACHER_APPROVE = "salary.teacher.approve"

    # Activities Student
    ACTIVITIES_STUDENT_ALL = "activities.student.*"
    ACTIVITIES_STUDENT_APPROVE = "activities.student.approve"

    # Activities Seminars
    ACTIVITIES_SEMINARS_ALL = "activities.seminars.*"
    ACTIVITIES_SEMINARS_ORGANIZE = "activities.seminars.organize"

    # Activities Competitions
    ACTIVITIES_COMPETITIONS_ALL = "activities.competitions.*"
    ACTIVITIES_COMPETITIONS_VIEW = "activities.competitions.view"
    ACTIVITIES_COMPETITIONS_ADD = "activities.competitions.add"
    ACTIVITIES_COMPETITIONS_EDIT = "activities.competitions.edit"
    ACTIVITIES_COMPETITIONS_DELETE = "activities.competitions.delete"

    # Activities Parties
    ACTIVITIES_PARTIES_ALL = "activities.parties.*"
    ACTIVITIES_PARTIES_VIEW = "activities.parties.view"
    ACTIVITIES_PARTIES_ADD = "activities.parties.add"
    ACTIVITIES_PARTIES_EDIT = "activities.parties.edit"
    ACTIVITIES_PARTIES_DELETE = "activities.parties.delete"

    # Parent Evaluation Access
    EVALUATION_STUDENT_VIEW_FOR_PARENT = "evaluation.student.view_for_parent"
    EVALUATION_STUDENT_REPORTS_VIEW = "evaluation.student.reports.view"

    # Parent Dashboard
    PARENT_DASHBOARD_VIEW = "parent_dashboard:view"
    STUDENT_REPORTS_VIEW = "student_reports:view"
    ATTENDANCE_VIEW = "attendance:view"
    EXAM_RESULTS_VIEW = "exam_results:view"
    COMMUNICATION_SEND_MESSAGE = "communication:send_message"

    # Financial Subscriptions for Parent
    FINANCIAL_SUBSCRIPTIONS_VIEW_FOR_PARENT = "financial.subscriptions.view_for_parent"
    FINANCIAL_SUBSCRIPTIONS_PAY_FOR_PARENT = "financial.subscriptions.pay_for_parent"

    # Communication Receive Messages
    COMMUNICATION_RECEIVE_MESSAGES = "communication.receive_messages"

from app.modules.classes.models import Class
from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.models.unit import Unit
from app.modules.curriculums.models.unit_item import UnitItem
from app.modules.evaluations.constants import MAX_GRADE
from app.modules.evaluations.models import AttendanceStatus, Evaluation
from app.modules.exams.models.exam_attempt import ExamAttempt
from app.modules.student_progress.models import StudentProgress
from app.modules.student_progress.schemas import (
    StudentProgressByStudentList,
    StudentProgressBySubjectEntry,
    StudentProgressBySubjectList,
    StudentProgressEvaluationInfo,
    StudentProgressExamAttemptInfo,
    StudentProgressExamInfo,
    StudentProgressStatus,
    StudentProgressStudentInfo,
    StudentProgressUnitInfo,
    StudentProgressUnitItemInfo,
)
from app.modules.students.models import StudentClass
from app.modules.users.models import User
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class StudentProgressCRUD:
    def hash_subject_curriculum_id(self, subj: int, curr: int) -> int:
        full_hash = subj
        full_hash <<= 32
        full_hash += curr
        return full_hash

    async def get_user(self, db: AsyncSession, user_id: int) -> User:
        return (
            await db.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.student), selectinload(User.parent))
            )
        ).scalar_one_or_none()

    async def get_progress_student(
        self,
        db: AsyncSession,
        student_id: int,
    ) -> list[StudentProgressBySubjectList]:
        query = (
            select(StudentProgress, Subject.name, Subject.id, Curriculum.name, Curriculum.id)
            .select_from(StudentProgress)
            .join(StudentClass, StudentClass.student_id == student_id)
            .join(Class, Class.id == StudentClass.class_id)
            .join(Curriculum, Curriculum.id == Class.curriculum_id)
            .join(Subject, Subject.id == Class.subject_id)
            .where(StudentProgress.student_id == student_id)
            .order_by(asc(Subject.name))
        )

        result = await db.execute(query)
        entries = result.all()
        progress_response: list[StudentProgressBySubjectList] = []

        # hashes to aid in differentiating between subjects when curriculums differ
        subject_curriculum_hashes: set[int] = set()

        # map subject curriculum hash -> (subject name, curriculum name, unit items)
        subject_info_map: dict[int, tuple[str, str, list[UnitItem]]] = {}
        for entry in entries:
            subject_name: str = entry[1]
            subject_id: int = entry[2]
            curriculum_name: str = entry[3]
            curriculum_id: int = entry[4]

            full_hash = self.hash_subject_curriculum_id(subject_id, curriculum_id)

            if subject_info_map.get(full_hash) is None:
                query = (
                    select(UnitItem)
                    .join(Unit, UnitItem.unit_id == Unit.id)
                    .where(Unit.subject_id == subject_id)
                )
                result = await db.execute(query)
                subject_info_map[full_hash] = (
                    subject_name,
                    curriculum_name,
                    result.scalars().all(),
                )

            subject_curriculum_hashes.add(full_hash)

        for i, full_hash in enumerate(subject_curriculum_hashes):
            subject_name, curriculum_name, unit_items = subject_info_map[full_hash]

            progress_response.append(
                StudentProgressBySubjectList(
                    subject_id=subject_id,
                    curriculum_name=curriculum_name,
                    subject_name=subject_name,
                    unit_items_info=[
                        self.serialize_unit_item(unit_item) for unit_item in unit_items
                    ],
                    items=[],
                )
            )

            for entry in entries:
                if entry[2] == subject_id:
                    progress: StudentProgress = entry[0]
                    progress_response[i].items.append(
                        self.serialize_progress_subject_entry(progress)
                    )

        return progress_response

    async def get_progress_parent(
        self,
        db: AsyncSession,
        student_ids: list[int],
    ) -> list[StudentProgressByStudentList]:
        query = (
            select(StudentProgress, Subject.name, Subject.id, Curriculum.name, Curriculum.id)
            .select_from(StudentProgress)
            .distinct()
            .join(StudentClass, StudentClass.student_id.in_(student_ids))
            .join(Class, Class.id == StudentClass.class_id)
            .join(Curriculum, Curriculum.id == Class.curriculum_id)
            .join(Subject, Subject.id == Class.subject_id)
            .where(StudentProgress.student_id.in_(student_ids))
            .order_by(asc(Subject.name))
        )

        result = await db.execute(query)
        entries = result.all()
        progress_response: list[StudentProgressByStudentList] = []

        # map student id -> (student name, student id, subject curriculum hash set)
        students_map: dict[int, tuple[str, int, set[int]]] = {}

        # map subject curriculum hash -> (subject name, curriculum, unit items)
        subject_info_map: dict[int, tuple[str, str, list[UnitItem]]] = {}

        for entry in entries:
            progress: StudentProgress = entry[0]
            subject_name: str = entry[1]
            subject_id: int = entry[2]
            curriculum_name: str = entry[3]
            curriculum_id: int = entry[4]

            full_hash = self.hash_subject_curriculum_id(subject_id, curriculum_id)

            if subject_info_map.get(full_hash) is None:
                query = (
                    select(UnitItem)
                    .join(Unit, UnitItem.unit_id == Unit.id)
                    .where(Unit.subject_id == subject_id)
                )
                result = await db.execute(query)
                subject_info_map[full_hash] = (
                    subject_name,
                    curriculum_name,
                    result.scalars().all(),
                )

            if students_map.get(progress.student_id) is None:
                students_map[progress.student_id] = (
                    progress.student.user.full_name,
                    progress.student_id,
                    {full_hash},
                )
            else:
                students_map[progress.student_id][2].add(full_hash)

        for i, (student_name, student_id, subject_curriculum_hash_set) in enumerate(
            students_map.values()
        ):
            progress_response.append(
                StudentProgressByStudentList(
                    student_id=student_id, student_name=student_name, groups=[]
                )
            )

            for j, full_hash in enumerate(subject_curriculum_hash_set):
                subject_name, curriculum_name, unit_items = subject_info_map[full_hash]

                progress_response[i].groups.append(
                    StudentProgressBySubjectList(
                        subject_id=subject_id,
                        subject_name=subject_name,
                        curriculum_name=curriculum_name,
                        unit_items_info=[
                            self.serialize_unit_item(unit_item) for unit_item in unit_items
                        ],
                        items=[],
                    )
                )

                for entry in entries:
                    if entry[0].student_id == student_id and entry[2] == subject_id:
                        progress: StudentProgress = entry[0]
                        progress_response[i].groups[j].items.append(
                            self.serialize_progress_subject_entry(progress)
                        )

        return progress_response

    def serialize_unit_item(self, unit_item: UnitItem) -> StudentProgressUnitItemInfo:
        return StudentProgressUnitItemInfo(
            id=unit_item.id,
            title=unit_item.title,
            type=unit_item.type,
            unit_info=StudentProgressUnitInfo(
                id=unit_item.unit_id,
                title=unit_item.unit.title,
            ),
        )

    def evaluation_progress_status(self, evaluation: Evaluation) -> StudentProgressStatus:
        arrived = (
            evaluation.attendance_status != AttendanceStatus.ABSENT != AttendanceStatus.EXCUSED
        )

        grade_requirement_fullfilled = sum(ev["grade"] for ev in evaluation.evaluation_grades) >= (
            MAX_GRADE * len(evaluation.evaluation_grades) / 2
        )

        return (
            StudentProgressStatus.PASSED
            if arrived and grade_requirement_fullfilled
            else StudentProgressStatus.FAILED
        )

    def exam_attempt_progress_status(self, exam_attempt: ExamAttempt) -> StudentProgressStatus:
        score_requirement_fullfilled = exam_attempt.score >= (exam_attempt.exam.total_marks / 2)
        return (
            StudentProgressStatus.PASSED
            if score_requirement_fullfilled
            else StudentProgressStatus.FAILED
        )

    def serialize_progress_subject_entry(
        self, progress: StudentProgress
    ) -> StudentProgressBySubjectEntry:
        status = StudentProgressStatus.PASSED
        status_checks = [
            (progress.evaluation, self.evaluation_progress_status),
            (progress.exam_attempt, self.exam_attempt_progress_status),
        ]

        for item, func in status_checks:
            if item:
                status = func(item)

            if status == StudentProgressStatus.FAILED:
                break

        return StudentProgressBySubjectEntry(
            id=progress.id,
            student_info=StudentProgressStudentInfo(
                id=progress.student_id,
                name=progress.student.user.full_name,
            ),
            status=status,
            unit_item_info=self.serialize_unit_item(progress.unit_item),
            evaluation_info=StudentProgressEvaluationInfo(
                id=progress.evaluation_id,
                attendance_status=progress.evaluation.attendance_status,
                evaluation_grades=progress.evaluation.evaluation_grades,
                date=progress.evaluation.date,
            )
            if progress.evaluation_id is not None
            else None,
            exam_attempt_info=StudentProgressExamAttemptInfo(
                id=progress.exam_attempt_id,
                exam_info=StudentProgressExamInfo(
                    id=progress.exam_attempt.exam_id,
                    title=progress.exam_attempt.exam.title,
                    duration_minutes=progress.exam_attempt.exam.duration_minutes,
                    start_time=progress.exam_attempt.exam.start_time,
                    end_time=progress.exam_attempt.exam.end_time,
                    total_marks=progress.exam_attempt.exam.total_marks,
                ),
                status=progress.exam_attempt.status,
                start_time=progress.exam_attempt.start_time,
                end_time=progress.exam_attempt.end_time,
                score=progress.exam_attempt.score,
            )
            if progress.exam_attempt_id is not None
            else None,
            created_at=progress.created_at,
        )


student_progress_crud = StudentProgressCRUD()

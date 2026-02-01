from collections.abc import Sequence

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
    StudentProgressClassGroup,
    StudentProgressEntry,
    StudentProgressEvaluationInfo,
    StudentProgressExamAttemptInfo,
    StudentProgressExamInfo,
    StudentProgressStatus,
    StudentProgressStudentGroupInternal,
    StudentProgressStudentGroupResponse,
    StudentProgressStudentInfo,
    StudentProgressUnitInfo,
    StudentProgressUnitItemInfo,
)
from app.modules.students.models import Student
from app.modules.users.models import User, UserBranch
from sqlalchemy import and_, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class StudentProgressCRUD:
    def create_class_group(
        self,
        class_id: int,
        class_name: str,
        subject_name: str,
        curriculum_name: str,
        unit_items: Sequence[UnitItem],
        progress: StudentProgress,
    ) -> StudentProgressClassGroup:
        return StudentProgressClassGroup(
            class_id=class_id,
            class_name=class_name,
            subject_name=subject_name,
            curriculum_name=curriculum_name,
            unit_items_info=[self.serialize_unit_item(unit_item) for unit_item in unit_items],
            items=[self.serialize_progress_entry(progress)],
        )

    async def get_user(self, db: AsyncSession, user_id: int) -> User | None:
        return (
            await db.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.student), selectinload(User.parent))
            )
        ).scalar_one_or_none()

    async def get_class_unit_items(self, db: AsyncSession, class_id: int) -> Sequence[UnitItem]:
        query = (
            select(UnitItem)
            .join(Unit, UnitItem.unit_id == Unit.id)
            .join(
                Class,
                and_(
                    Class.subject_id == Unit.subject_id,
                    Class.curriculum_id == Unit.curriculum_id,
                ),
            )
            .where(and_(Class.id == class_id))
            .order_by(asc(UnitItem.id))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_progress_student(
        self,
        db: AsyncSession,
        student_id: int,
    ) -> list[StudentProgressClassGroup]:
        query = (
            select(StudentProgress, Class.id, Class.name, Subject.name, Curriculum.name)
            .select_from(StudentProgress)
            .join(Student, Student.id == StudentProgress.student_id)
            .join(UserBranch, UserBranch.user_id == Student.user_id)
            .join(UnitItem, UnitItem.id == StudentProgress.unit_item_id)
            .join(Unit, Unit.id == UnitItem.unit_id)
            .join(
                Class,
                and_(
                    Class.subject_id == Unit.subject_id,
                    Class.curriculum_id == Unit.curriculum_id,
                    UserBranch.branch_id == Class.branch_id,
                ),
            )
            .join(Subject, Subject.id == Unit.subject_id)
            .join(Curriculum, Curriculum.id == Unit.curriculum_id)
            .where(StudentProgress.student_id == student_id)
            .order_by(asc(UnitItem.id))
        )

        result = await db.execute(query)
        entries = result.all()
        progress_response: dict[int, StudentProgressClassGroup] = {}

        for entry in entries:
            progress: StudentProgress = entry[0]
            class_id: int = entry[1]
            class_name: str = entry[2]
            subject_name: str = entry[3]
            curriculum_name: str = entry[4]

            if class_id in progress_response:
                # - add new progress to class group -

                progress_response[class_id].items.append(self.serialize_progress_entry(progress))
            else:
                # - create new class group -

                unit_items = await self.get_class_unit_items(db, class_id)

                progress_response[class_id] = self.create_class_group(
                    class_id=class_id,
                    class_name=class_name,
                    subject_name=subject_name,
                    curriculum_name=curriculum_name,
                    unit_items=unit_items,
                    progress=progress,
                )

        return list(progress_response.values())

    async def get_progress_parent(
        self,
        db: AsyncSession,
        student_ids: list[int],
    ) -> list[StudentProgressStudentGroupResponse]:
        query = (
            select(StudentProgress, Class.id, Class.name, Subject.name, Curriculum.name)
            .select_from(StudentProgress)
            .join(Student, Student.id == StudentProgress.student_id)
            .join(UserBranch, UserBranch.user_id == Student.user_id)
            .join(UnitItem, UnitItem.id == StudentProgress.unit_item_id)
            .join(Unit, Unit.id == UnitItem.unit_id)
            .join(
                Class,
                and_(
                    Class.subject_id == Unit.subject_id,
                    Class.curriculum_id == Unit.curriculum_id,
                    UserBranch.branch_id == Class.branch_id,
                ),
            )
            .join(Subject, Subject.id == Unit.subject_id)
            .join(Curriculum, Curriculum.id == Unit.curriculum_id)
            .where(StudentProgress.student_id.in_(student_ids))
            .order_by(asc(UnitItem.id))
        )

        result = await db.execute(query)
        entries = result.all()
        progress_response: dict[int, StudentProgressStudentGroupInternal] = {}

        for entry in entries:
            progress: StudentProgress = entry[0]
            class_id: int = entry[1]
            class_name: str = entry[2]
            subject_name: str = entry[3]
            curriculum_name: str = entry[4]

            if progress.student_id in progress_response:
                if class_id in progress_response[progress.student_id].groups:
                    progress_response[progress.student_id].groups[class_id].items.append(
                        self.serialize_progress_entry(progress)
                    )
                else:
                    unit_items = await self.get_class_unit_items(db, class_id)
                    progress_response[progress.student_id].groups[class_id] = (
                        self.create_class_group(
                            class_id=class_id,
                            class_name=class_name,
                            subject_name=subject_name,
                            curriculum_name=curriculum_name,
                            unit_items=unit_items,
                            progress=progress,
                        )
                    )
            else:
                unit_items = await self.get_class_unit_items(db, class_id)
                progress_response[progress.student_id] = StudentProgressStudentGroupInternal(
                    student_id=progress.student_id,
                    student_name=progress.student.user.full_name,
                    groups={
                        class_id: self.create_class_group(
                            class_id=class_id,
                            class_name=class_name,
                            subject_name=subject_name,
                            curriculum_name=curriculum_name,
                            unit_items=unit_items,
                            progress=progress,
                        )
                    },
                )

        return [
            StudentProgressStudentGroupResponse(
                student_id=group.student_id,
                student_name=group.student_name,
                groups=list(group.groups.values()),
            )
            for group in progress_response.values()
        ]

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
        arrived = evaluation.attendance_status not in (
            AttendanceStatus.ABSENT,
            AttendanceStatus.EXCUSED,
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

    def serialize_progress_entry(self, progress: StudentProgress) -> StudentProgressEntry:
        status = StudentProgressStatus.PASSED
        status_checks = [
            (progress.evaluation, self.evaluation_progress_status),
            (progress.exam_attempt, self.exam_attempt_progress_status),
        ]

        for item, func in status_checks:
            if item:
                status = func(item)  # type: ignore reportArgumentType

            if status == StudentProgressStatus.FAILED:
                break

        return StudentProgressEntry(
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
                notes=progress.evaluation.notes,
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

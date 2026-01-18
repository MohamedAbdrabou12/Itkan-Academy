from app.modules.classes.models import Class
from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.models.unit import Unit
from app.modules.curriculums.models.unit_item import UnitItem
from app.modules.student_progress.models import StudentProgress
from app.modules.student_progress.schemas import (
    StudentProgressByStudentList,
    StudentProgressBySubjectEntry,
    StudentProgressBySubjectList,
    StudentProgressEvaluationInfo,
    StudentProgressExamAttemptInfo,
    StudentProgressExamInfo,
    StudentProgressStudentInfo,
    StudentProgressUnitInfo,
    StudentProgressUnitItemInfo,
)
from app.modules.students.models import StudentClass
from app.modules.users.models import User
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


def hash_student_subject_curriculum_id(stud: int, subj: int, curr: int) -> int:
    full_hash = stud
    full_hash <<= 32
    full_hash += subj
    full_hash <<= 32
    full_hash += curr
    return full_hash


def hash_subject_curriculum_id(subj: int, curr: int) -> int:
    full_hash = subj
    full_hash <<= 32
    full_hash += curr
    return full_hash


class StudentProgressCRUD:
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
            select(StudentProgress, Subject.name, Subject.id, Curriculum.id)
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

        # map subject curriculum hash -> (subject name, unit items)
        subject_info_map: dict[int, tuple[str, list[UnitItem]]] = {}
        for entry in entries:
            subject_name: str = entry[1]
            subject_id: int = entry[2]
            curriculum_id: int = entry[3]

            full_hash = hash_subject_curriculum_id(subject_id, curriculum_id)

            if subject_info_map.get(full_hash) is None:
                query = (
                    select(UnitItem)
                    .join(Unit, UnitItem.unit_id == Unit.id)
                    .where(Unit.subject_id == subject_id)
                )
                result = await db.execute(query)
                subject_info_map[full_hash] = (subject_name, result.scalars().all())

            subject_curriculum_hashes.add(full_hash)

        for i, full_hash in enumerate(subject_curriculum_hashes):
            subject_name, unit_items = subject_info_map[full_hash]

            progress_response.append(
                StudentProgressBySubjectList(
                    subject_id=subject_id,
                    subject_name=subject_name,
                    unit_items_info=[
                        StudentProgressUnitItemInfo(
                            id=unit_item.id,
                            title=unit_item.title,
                            type=unit_item.type,
                            unit_info=StudentProgressUnitInfo(
                                id=unit_item.unit_id,
                                title=unit_item.unit.title,
                            ),
                        )
                        for unit_item in unit_items
                    ],
                    items=[],
                )
            )

            for entry in entries:
                if entry[2] == subject_id:
                    progress: StudentProgress = entry[0]
                    progress_response[i].items.append(
                        StudentProgressBySubjectEntry(
                            id=progress.id,
                            student_info=StudentProgressStudentInfo(
                                id=progress.student_id,
                                name=progress.student.user.full_name,
                            ),
                            status=progress.status,
                            unit_item_info=StudentProgressUnitItemInfo(
                                id=progress.unit_item_id,
                                title=progress.unit_item.title,
                                type=progress.unit_item.type,
                                unit_info=StudentProgressUnitInfo(
                                    id=progress.unit_item.unit_id,
                                    title=progress.unit_item.unit.title,
                                ),
                            ),
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
                    )

        return progress_response

    async def get_progress_parent(
        self,
        db: AsyncSession,
        student_ids: list[int],
    ) -> list[StudentProgressByStudentList]:
        query = (
            select(StudentProgress, Subject.name, Subject.id, Curriculum.id)
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

        # map subject curriculum hash -> (subject name, unit items)
        subject_info_map: dict[int, tuple[str, list[UnitItem]]] = {}

        for entry in entries:
            progress: StudentProgress = entry[0]
            subject_name: str = entry[1]
            subject_id: int = entry[2]
            curriculum_id: int = entry[3]

            full_hash = hash_student_subject_curriculum_id(
                progress.student_id, subject_id, curriculum_id
            )

            if subject_info_map.get(full_hash) is None:
                query = (
                    select(UnitItem)
                    .join(Unit, UnitItem.unit_id == Unit.id)
                    .where(Unit.subject_id == subject_id)
                )
                result = await db.execute(query)
                subject_info_map[full_hash] = (
                    subject_name,
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
                subject_name, unit_items = subject_info_map[full_hash]

                progress_response[i].groups.append(
                    StudentProgressBySubjectList(
                        subject_id=subject_id,
                        subject_name=subject_name,
                        unit_items_info=[
                            StudentProgressUnitItemInfo(
                                id=unit_item.id,
                                title=unit_item.title,
                                type=unit_item.type,
                                unit_info=StudentProgressUnitInfo(
                                    id=unit_item.unit_id,
                                    title=unit_item.unit.title,
                                ),
                            )
                            for unit_item in unit_items
                        ],
                        items=[],
                    )
                )

                for entry in entries:
                    if entry[0].student_id == student_id and entry[2] == subject_id:
                        progress: StudentProgress = entry[0]
                        progress_response[i].groups[j].items.append(
                            StudentProgressBySubjectEntry(
                                id=progress.id,
                                student_info=StudentProgressStudentInfo(
                                    id=progress.student_id,
                                    name=progress.student.user.full_name,
                                ),
                                status=progress.status,
                                unit_item_info=StudentProgressUnitItemInfo(
                                    id=progress.unit_item_id,
                                    title=progress.unit_item.title,
                                    type=progress.unit_item.type,
                                    unit_info=StudentProgressUnitInfo(
                                        id=progress.unit_item.unit_id,
                                        title=progress.unit_item.unit.title,
                                    ),
                                ),
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
                        )

        return progress_response


student_progress_crud = StudentProgressCRUD()

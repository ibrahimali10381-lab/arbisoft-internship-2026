from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Course, Question, Topic, User
from app.security import get_current_user


def owned_course(
    course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Course:
    course = db.get(Course, course_id)
    if course is None or course.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    return course


def load_owned_course(db: Session, user: User, course_id: int) -> Course:
    return owned_course(course_id, db, user)


def owned_topic(
    topic_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Topic:
    topic = db.get(Topic, topic_id)
    if topic is None or topic.course.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")
    return topic


def owned_question(
    question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Question:
    question = db.get(Question, question_id)
    if question is None or question.topic.course.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")
    return question

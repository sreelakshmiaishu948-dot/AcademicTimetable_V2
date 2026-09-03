import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client,Client

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# SUPABASE CONNECTION
# ============================================================


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# GENERIC CRUD FUNCTIONS
# ============================================================

def get_all(table_name):
    response = (
        supabase
        .table(table_name)
        .select("*")
        .execute()
    )

    return response.data


def get_by_id(table_name, record_id):
    response = (
        supabase
        .table(table_name)
        .select("*")
        .eq("id", record_id)
        .execute()
    )

    return response.data


def create_record(table_name, data):
    response = (
        supabase
        .table(table_name)
        .insert(data)
        .execute()
    )

    return response.data


def update_record(table_name, record_id, data):
    response = (
        supabase
        .table(table_name)
        .update(data)
        .eq("id", record_id)
        .execute()
    )

    return response.data


def delete_record(table_name, record_id):
    response = (
        supabase
        .table(table_name)
        .delete()
        .eq("id", record_id)
        .execute()
    )

    return response.data


# ============================================================
# ROOMS
# ============================================================

def get_rooms():
    return get_all("rooms")


def get_room(room_id):
    return get_by_id("rooms", room_id)


def add_room(room_number, building, room_type, capacity):
    return create_record(
        "rooms",
        {
            "room_number": room_number,
            "building": building,
            "room_type": room_type,
            "capacity": capacity
        }
    )


def update_room(
    room_id,
    room_number,
    building,
    room_type,
    capacity
):
    return update_record(
        "rooms",
        room_id,
        {
            "room_number": room_number,
            "building": building,
            "room_type": room_type,
            "capacity": capacity
        }
    )


def delete_room(room_id):
    return delete_record("rooms", room_id)


# ============================================================
# TEACHERS
# ============================================================

def get_teachers():
    return get_all("teachers")


def get_teacher(teacher_id):
    return get_by_id("teachers", teacher_id)


def add_teacher(
    name,
    email,
    department,
    max_hours_per_week
):
    return create_record(
        "teachers",
        {
            "name": name,
            "email": email,
            "department": department,
            "max_hours_per_week": max_hours_per_week
        }
    )


def update_teacher(
    teacher_id,
    name,
    email,
    department,
    max_hours_per_week
):
    return update_record(
        "teachers",
        teacher_id,
        {
            "name": name,
            "email": email,
            "department": department,
            "max_hours_per_week": max_hours_per_week
        }
    )


def delete_teacher(teacher_id):
    return delete_record("teachers", teacher_id)


# ============================================================
# SUBJECTS
# ============================================================

def get_subjects():
    return get_all("subjects")


def get_subject(subject_id):
    return get_by_id("subjects", subject_id)


def add_subject(
    code,
    name,
    department,
    credits,
    weekly_sessions,
    duration_slots=1
):
    return create_record(
        "subjects",
        {
            "code": code,
            "name": name,
            "department": department,
            "credits": credits,
            "weekly_sessions": weekly_sessions,
            "duration_slots": duration_slots
        }
    )


def update_subject(
    subject_id,
    code,
    name,
    department,
    credits,
    weekly_sessions,
    duration_slots=1
):
    return update_record(
        "subjects",
        subject_id,
        {
            "code": code,
            "name": name,
            "department": department,
            "credits": credits,
            "weekly_sessions": weekly_sessions,
            "duration_slots": duration_slots
        }
    )


def delete_subject(subject_id):
    return delete_record("subjects", subject_id)


# ============================================================
# STUDENT GROUPS
# ============================================================

def get_student_groups():
    return get_all("student_groups")


def get_student_group(student_group_id):
    return get_by_id(
        "student_groups",
        student_group_id
    )


def add_student_group(
    name,
    department,
    semester,
    section,
    student_count
):
    return create_record(
        "student_groups",
        {
            "name": name,
            "department": department,
            "semester": semester,
            "section": section,
            "student_count": student_count
        }
    )


def update_student_group(
    student_group_id,
    name,
    department,
    semester,
    section,
    student_count
):
    return update_record(
        "student_groups",
        student_group_id,
        {
            "name": name,
            "department": department,
            "semester": semester,
            "section": section,
            "student_count": student_count
        }
    )


def delete_student_group(student_group_id):
    return delete_record(
        "student_groups",
        student_group_id
    )


# ============================================================
# TIME SLOTS
# ============================================================

def get_time_slots():
    return get_all("time_slots")


def get_time_slot(time_slot_id):
    return get_by_id(
        "time_slots",
        time_slot_id
    )


def add_time_slot(
    day_of_week,
    start_time,
    end_time,
    slot_name
):
    return create_record(
        "time_slots",
        {
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
            "slot_name": slot_name
        }
    )


def update_time_slot(
    time_slot_id,
    day_of_week,
    start_time,
    end_time,
    slot_name
):
    return update_record(
        "time_slots",
        time_slot_id,
        {
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
            "slot_name": slot_name
        }
    )


def delete_time_slot(time_slot_id):
    return delete_record(
        "time_slots",
        time_slot_id
    )


# ============================================================
# TEACHER AVAILABILITY
# ============================================================

def get_teacher_availability():
    return get_all("teacher_availability")


def get_teacher_availability_by_id(availability_id):
    return get_by_id(
        "teacher_availability",
        availability_id
    )


def add_teacher_availability(
    teacher_id,
    time_slot_id,
    available
):
    return create_record(
        "teacher_availability",
        {
            "teacher_id": teacher_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def update_teacher_availability(
    availability_id,
    teacher_id,
    time_slot_id,
    available
):
    return update_record(
        "teacher_availability",
        availability_id,
        {
            "teacher_id": teacher_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def delete_teacher_availability(availability_id):
    return delete_record(
        "teacher_availability",
        availability_id
    )


# ============================================================
# ROOM AVAILABILITY
# ============================================================

def get_room_availability():
    return get_all("room_availability")


def get_room_availability_by_id(availability_id):
    return get_by_id(
        "room_availability",
        availability_id
    )


def add_room_availability(
    room_id,
    time_slot_id,
    available
):
    return create_record(
        "room_availability",
        {
            "room_id": room_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def update_room_availability(
    availability_id,
    room_id,
    time_slot_id,
    available
):
    return update_record(
        "room_availability",
        availability_id,
        {
            "room_id": room_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def delete_room_availability(availability_id):
    return delete_record(
        "room_availability",
        availability_id
    )


# ============================================================
# STUDENT GROUP AVAILABILITY
# ============================================================

def get_student_group_availability():
    return get_all("student_group_availability")


def get_student_group_availability_by_id(availability_id):
    return get_by_id(
        "student_group_availability",
        availability_id
    )


def add_student_group_availability(
    student_group_id,
    time_slot_id,
    available
):
    return create_record(
        "student_group_availability",
        {
            "student_group_id": student_group_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def update_student_group_availability(
    availability_id,
    student_group_id,
    time_slot_id,
    available
):
    return update_record(
        "student_group_availability",
        availability_id,
        {
            "student_group_id": student_group_id,
            "time_slot_id": time_slot_id,
            "available": available
        }
    )


def delete_student_group_availability(availability_id):
    return delete_record(
        "student_group_availability",
        availability_id
    )


# ============================================================
# TIMETABLE VERSIONS
# ============================================================

def get_timetable_versions():
    return get_all("timetable_versions")


def get_timetable_version(version_id):
    return get_by_id(
        "timetable_versions",
        version_id
    )


def add_timetable_version(
    name,
    description,
    status
):
    return create_record(
        "timetable_versions",
        {
            "name": name,
            "description": description,
            "status": status
        }
    )


def update_timetable_version(
    version_id,
    name,
    description,
    status
):
    return update_record(
        "timetable_versions",
        version_id,
        {
            "name": name,
            "description": description,
            "status": status
        }
    )


def delete_timetable_version(version_id):
    return delete_record(
        "timetable_versions",
        version_id
    )


# ============================================================
# TIMETABLE ALLOCATIONS
# ============================================================

def get_timetable_allocations():
    return get_all("timetable_allocations")


def get_timetable_allocation(allocation_id):
    return get_by_id(
        "timetable_allocations",
        allocation_id
    )


def add_timetable_allocation(
    version_id,
    subject_id,
    teacher_id,
    room_id,
    student_group_id,
    time_slot_id,
    status
):
    return create_record(
        "timetable_allocations",
        {
            "version_id": version_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "room_id": room_id,
            "student_group_id": student_group_id,
            "time_slot_id": time_slot_id,
            "status": status
        }
    )


def update_timetable_allocation(
    allocation_id,
    version_id,
    subject_id,
    teacher_id,
    room_id,
    student_group_id,
    time_slot_id,
    status
):
    return update_record(
        "timetable_allocations",
        allocation_id,
        {
            "version_id": version_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "room_id": room_id,
            "student_group_id": student_group_id,
            "time_slot_id": time_slot_id,
            "status": status
        }
    )


def delete_timetable_allocation(allocation_id):
    return delete_record(
        "timetable_allocations",
        allocation_id
    )


# ============================================================
# SIMPLE CONNECTION TEST
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("   ACADEMIC TIMETABLE DATABASE")
    print("========================================")

    print("\nTeachers:", len(get_teachers()))
    print("Student Groups:", len(get_student_groups()))
    print("Subjects:", len(get_subjects()))
    print("Rooms:", len(get_rooms()))
    print("Time Slots:", len(get_time_slots()))
    print("Teacher Availability:", len(get_teacher_availability()))
    print("Room Availability:", len(get_room_availability()))
    print(
        "Student Group Availability:",
        len(get_student_group_availability())
    )
    print(
        "Timetable Versions:",
        len(get_timetable_versions())
    )
    print(
        "Timetable Allocations:",
        len(get_timetable_allocations())
    )

    print("\n========================================")
    print("       DATABASE CONNECTION OK")
    print("========================================")
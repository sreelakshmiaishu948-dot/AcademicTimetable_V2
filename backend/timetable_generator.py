from database import supabase
from collections import defaultdict


# ============================================================
# CONFIGURATION
# ============================================================

TABLE_TEACHERS = "teachers"
TABLE_GROUPS = "student_groups"
TABLE_SUBJECTS = "subjects"
TABLE_ROOMS = "rooms"
TABLE_SLOTS = "time_slots"

TABLE_TEACHER_AVAILABILITY = "teacher_availability"
TABLE_ROOM_AVAILABILITY = "room_availability"
TABLE_GROUP_AVAILABILITY = "student_group_availability"

TABLE_VERSIONS = "timetable_versions"
TABLE_ALLOCATIONS = "timetable_allocations"


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_all(table_name):
    response = (
        supabase
        .table(table_name)
        .select("*")
        .execute()
    )

    return response.data


# ============================================================
# LOAD DATABASE DATA
# ============================================================

def load_data():

    teachers = get_all(TABLE_TEACHERS)
    groups = get_all(TABLE_GROUPS)
    subjects = get_all(TABLE_SUBJECTS)
    rooms = get_all(TABLE_ROOMS)
    slots = get_all(TABLE_SLOTS)

    teacher_availability = get_all(TABLE_TEACHER_AVAILABILITY)
    room_availability = get_all(TABLE_ROOM_AVAILABILITY)
    group_availability = get_all(TABLE_GROUP_AVAILABILITY)

    return (
        teachers,
        groups,
        subjects,
        rooms,
        slots,
        teacher_availability,
        room_availability,
        group_availability
    )


# ============================================================
# AUTOMATIC TIMETABLE GENERATOR
# ============================================================

def generate_timetable():

    print("=" * 60)
    print("        AUTOMATIC TIMETABLE GENERATION")
    print("=" * 60)

    (
        teachers,
        groups,
        subjects,
        rooms,
        slots,
        teacher_availability,
        room_availability,
        group_availability
    ) = load_data()

    print()
    print(f"Teachers       : {len(teachers)}")
    print(f"Student Groups : {len(groups)}")
    print(f"Subjects       : {len(subjects)}")
    print(f"Rooms          : {len(rooms)}")
    print(f"Time Slots     : {len(slots)}")
    print()

    # --------------------------------------------------------
    # EXPECTED SESSIONS
    # --------------------------------------------------------

    expected_sessions = sum(
        subject.get("weekly_sessions", 0)
        for subject in subjects
    ) * len(groups)

    print(f"Expected sessions: {expected_sessions}")
    print()

    # --------------------------------------------------------
    # CREATE LOOKUP DICTIONARIES
    # --------------------------------------------------------

    teacher_by_id = {
        teacher["id"]: teacher
        for teacher in teachers
    }

    group_by_id = {
        group["id"]: group
        for group in groups
    }

    subject_by_id = {
        subject["id"]: subject
        for subject in subjects
    }

    room_by_id = {
        room["id"]: room
        for room in rooms
    }

    slot_by_id = {
        slot["id"]: slot
        for slot in slots
    }

    # --------------------------------------------------------
    # SORT TIME SLOTS
    # --------------------------------------------------------

    slots = sorted(
        slots,
        key=lambda x: (
            x["day_of_week"],
            x["start_time"]
        )
    )

    # --------------------------------------------------------
    # AVAILABILITY SETS
    # --------------------------------------------------------

    teacher_available = set()

    for row in teacher_availability:
        if row["available"]:
            teacher_available.add(
                (
                    row["teacher_id"],
                    row["time_slot_id"]
                )
            )

    room_available = set()

    for row in room_availability:
        if row["available"]:
            room_available.add(
                (
                    row["room_id"],
                    row["time_slot_id"]
                )
            )

    group_available = set()

    for row in group_availability:
        if row["available"]:
            group_available.add(
                (
                    row["student_group_id"],
                    row["time_slot_id"]
                )
            )

    # --------------------------------------------------------
    # REMOVE OLD ALLOCATIONS
    # --------------------------------------------------------

    print("Removing old allocations...")
    print("Old allocations cleared.")
    print()

    supabase \
        .table(TABLE_ALLOCATIONS) \
        .delete() \
        .gte("id", 0) \
        .execute()

    # --------------------------------------------------------
    # GET TIMETABLE VERSION
    # --------------------------------------------------------

    version_response = (
        supabase
        .table(TABLE_VERSIONS)
        .select("*")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not version_response.data:
        raise Exception(
            "No timetable version found in timetable_versions table."
        )

    version_id = version_response.data[0]["id"]

    print(f"Using timetable version: {version_id}")
    print()

    # --------------------------------------------------------
    # TRACKING
    # --------------------------------------------------------

    allocations = []

    teacher_workload = defaultdict(int)

    teacher_slot_used = set()

    room_slot_used = set()

    group_slot_used = set()

    # --------------------------------------------------------
    # ROOM CAPACITY
    # --------------------------------------------------------

    suitable_rooms = [
        room
        for room in rooms
        if room["capacity"] >= 60
    ]

    if len(suitable_rooms) < 4:
        raise Exception(
            "At least 4 rooms with capacity >= 60 are required."
        )

    # --------------------------------------------------------
    # SUBJECT DAY PATTERN
    #
    # Each subject is scheduled on 3 different days.
    # This prevents all 3 weekly sessions from being
    # placed on the same day.
    # --------------------------------------------------------

    day_patterns = [
        (0, 1, 2),
        (0, 1, 3),
        (0, 1, 4),
        (0, 2, 3),
        (0, 2, 4),
        (1, 2, 3),
        (1, 3, 4),
        (2, 3, 4)
    ]

    # --------------------------------------------------------
    # GLOBAL SLOT LOAD
    # --------------------------------------------------------

    slot_load = defaultdict(int)

    # --------------------------------------------------------
    # PROCESS GROUPS
    # --------------------------------------------------------

    for group_index, group in enumerate(groups):

        group_id = group["id"]
        group_name = group["name"]

        print(f"Processing: {group_name}")

        group_session_count = 0

        for subject_index, subject in enumerate(subjects):

            subject_id = subject["id"]
            subject_code = subject["code"]

            weekly_sessions = subject["weekly_sessions"]

            # 3 sessions per subject
            for session_number in range(weekly_sessions):

                # ------------------------------------------------
                # CHOOSE DAY
                # ------------------------------------------------

                base_days = day_patterns[
                    subject_index % len(day_patterns)
                ]

                day_number = (
                    base_days[session_number]
                    + group_index
                ) % 5

                # ------------------------------------------------
                # FIND BEST SLOT
                # ------------------------------------------------

                candidates = []

                for slot in slots:

                    slot_id = slot["id"]

                    # Convert day_of_week 1-5 to index 0-4
                    slot_day = slot["day_of_week"] - 1

                    if slot_day != day_number:
                        continue

                    # Student group cannot have two classes
                    # in the same slot.
                    if (group_id,slot_id) in group_slot_used:
                        continue

                    if (
                        group_id,
                        slot_id
                    ) not in group_available:
                        continue

                    # ------------------------------------------------
                    # FIND AVAILABLE TEACHERS
                    # ------------------------------------------------

                    available_teachers = []

                    for teacher in teachers:

                        teacher_id = teacher["id"]

                        max_hours = teacher[
                            "max_hours_per_week"
                        ]

                        if teacher_workload[teacher_id] >= max_hours:
                            continue

                        if (
                            teacher_id,
                            slot_id
                        ) in teacher_slot_used:
                            continue

                        if (
                            teacher_id,
                            slot_id
                        ) not in teacher_available:
                            continue

                        available_teachers.append(teacher)

                    if not available_teachers:
                        continue

                    # ------------------------------------------------
                    # FIND AVAILABLE ROOM
                    # ------------------------------------------------

                    available_rooms = []

                    student_count = group["student_count"]

                    for room in suitable_rooms:

                        room_id = room["id"]

                        if room["capacity"] < student_count:
                            continue

                        if (
                            room_id,
                            slot_id
                        ) in room_slot_used:
                            continue

                        if (
                            room_id,
                            slot_id
                        ) not in room_available:
                            continue

                        available_rooms.append(room)

                    if not available_rooms:
                        continue

                    # ------------------------------------------------
                    # SELECT LEAST LOADED TEACHER
                    # ------------------------------------------------

                    selected_teacher = min(
                        available_teachers,
                        key=lambda teacher:
                        teacher_workload[teacher["id"]]
                    )

                    # ------------------------------------------------
                    # SELECT LEAST USED ROOM
                    # ------------------------------------------------

                    selected_room = min(
                        available_rooms,
                        key=lambda room:
                        sum(
                            1
                            for allocation in allocations
                            if allocation["room_id"] == room["id"]
                        )
                    )

                    candidates.append(
                        (
                            slot_load[slot_id],
                            teacher_workload[
                                selected_teacher["id"]
                            ],
                            slot,
                            selected_teacher,
                            selected_room
                        )
                    )

                # ------------------------------------------------
                # NO SLOT FOUND
                # ------------------------------------------------

                if not candidates:

                    raise Exception(
                        f"Could not schedule "
                        f"{subject_code} for "
                        f"{group_name}. "
                        f"Please check teacher/room availability."
                    )

                # ------------------------------------------------
                # BEST CANDIDATE
                # ------------------------------------------------

                candidates.sort(
                    key=lambda x: (
                        x[0],
                        x[1],
                        x[2]["day_of_week"],
                        x[2]["start_time"]
                    )
                )

                (
                    _,
                    _,
                    selected_slot,
                    selected_teacher,
                    selected_room
                ) = candidates[0]

                slot_id = selected_slot["id"]

                teacher_id = selected_teacher["id"]

                room_id = selected_room["id"]

                # ------------------------------------------------
                # CREATE ALLOCATION
                # ------------------------------------------------

                allocation = {
                    "version_id": version_id,
                    "subject_id": subject_id,
                    "teacher_id": teacher_id,
                    "room_id": room_id,
                    "student_group_id": group_id,
                    "time_slot_id": slot_id,
                    "status": "scheduled"
                }

                allocations.append(allocation)

                # ------------------------------------------------
                # UPDATE TRACKING
                # ------------------------------------------------

                teacher_workload[teacher_id] += 1

                teacher_slot_used.add(
                    (
                        teacher_id,
                        slot_id
                    )
                )

                room_slot_used.add(
                    (
                        room_id,
                        slot_id
                    )
                )

                group_slot_used.add((group_id,slot_id))

                slot_load[slot_id] += 1

                group_session_count += 1

                print(
                    f"  {subject_code:<5} | "
                    f"{selected_teacher['name']:<20} | "
                    f"Room {selected_room['room_number']:<14} | "
                    f"{selected_slot['slot_name']}"
                )

        print(
            f"  Total sessions for "
            f"{group_name}: "
            f"{group_session_count}"
        )

        print()

    # ========================================================
    # VALIDATION
    # ========================================================

    print("=" * 60)
    print("VALIDATING TIMETABLE")
    print("=" * 60)

    actual_sessions = len(allocations)

    print()
    print(f"Expected sessions : {expected_sessions}")
    print(f"Generated sessions: {actual_sessions}")
    print()

    if actual_sessions != expected_sessions:

        raise Exception(
            f"Timetable incomplete. "
            f"Expected {expected_sessions}, "
            f"but generated {actual_sessions}."
        )

    # --------------------------------------------------------
    # TEACHER WORKLOAD VALIDATION
    # --------------------------------------------------------

    print("Teacher workload:")

    for teacher in teachers:

        teacher_id = teacher["id"]

        workload = teacher_workload[teacher_id]

        maximum = teacher["max_hours_per_week"]

        print(
            f"  {teacher['name']:<20}: "
            f"{workload}/{maximum} hours"
        )

        if workload > maximum:

            raise Exception(
                f"Teacher workload exceeded: "
                f"{teacher['name']}"
            )

    print()

    # --------------------------------------------------------
    # INSERT INTO SUPABASE
    # --------------------------------------------------------

    print("=" * 60)
    print("Saving timetable to Supabase...")
    print("=" * 60)

    # Insert in batches
    batch_size = 50

    for start in range(
        0,
        len(allocations),
        batch_size
    ):

        batch = allocations[
            start:start + batch_size
        ]

        supabase \
            .table(TABLE_ALLOCATIONS) \
            .insert(batch) \
            .execute()

    print()
    print("=" * 60)
    print("       TIMETABLE GENERATION COMPLETED")
    print("=" * 60)

    print()
    print(
        f"Total allocations created: "
        f"{len(allocations)}"
    )

    print()

    print("Teacher workload:")

    for teacher in teachers:

        teacher_id = teacher["id"]

        print(
            f"  {teacher['name']:<20}: "
            f"{teacher_workload[teacher_id]} hours"
        )

    print()

    print(
        "Timetable saved successfully "
        "to Supabase."
    )

    print("=" * 60)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        generate_timetable()

    except Exception as error:

        print()
        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print()
        print(error)
        print()
from database import supabase


def get_data(table):
    return supabase.table(table).select("*").execute().data


print("=" * 60)
print("        TIMETABLE VALIDATION")
print("=" * 60)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

teachers = get_data("teachers")
groups = get_data("student_groups")
subjects = get_data("subjects")
rooms = get_data("rooms")
slots = get_data("time_slots")
allocations = get_data("timetable_allocations")

print()
print(f"Teachers       : {len(teachers)}")
print(f"Student Groups : {len(groups)}")
print(f"Subjects       : {len(subjects)}")
print(f"Rooms          : {len(rooms)}")
print(f"Time Slots     : {len(slots)}")
print(f"Allocations    : {len(allocations)}")
print()


# ------------------------------------------------------------
# LOOKUPS
# ------------------------------------------------------------

teacher_map = {
    t["id"]: t
    for t in teachers
}

group_map = {
    g["id"]: g
    for g in groups
}

subject_map = {
    s["id"]: s
    for s in subjects
}

room_map = {
    r["id"]: r
    for r in rooms
}

slot_map = {
    s["id"]: s
    for s in slots
}


errors = []


# ------------------------------------------------------------
# 1. CHECK TOTAL ALLOCATIONS
# ------------------------------------------------------------

print("1. CHECKING TOTAL ALLOCATIONS")

expected = (
    len(groups)
    * sum(
        s["weekly_sessions"]
        for s in subjects
    )
)

actual = len(allocations)

print(f"   Expected : {expected}")
print(f"   Actual   : {actual}")

if actual != expected:
    errors.append(
        f"Expected {expected} allocations but found {actual}"
    )
else:
    print("   PASS")


# ------------------------------------------------------------
# 2. CHECK STUDENT GROUP CONFLICTS
# ------------------------------------------------------------

print()
print("2. CHECKING STUDENT GROUP CONFLICTS")

group_slots = {}

for allocation in allocations:

    key = (
        allocation["student_group_id"],
        allocation["time_slot_id"]
    )

    if key in group_slots:

        group = group_map[
            allocation["student_group_id"]
        ]

        slot = slot_map[
            allocation["time_slot_id"]
        ]

        errors.append(
            f"Student group conflict: "
            f"{group['name']} at "
            f"{slot['slot_name']}"
        )

    group_slots[key] = True

if not any(
    "Student group conflict" in e
    for e in errors
):
    print("   PASS")


# ------------------------------------------------------------
# 3. CHECK TEACHER CONFLICTS
# ------------------------------------------------------------

print()
print("3. CHECKING TEACHER CONFLICTS")

teacher_slots = {}

for allocation in allocations:

    key = (
        allocation["teacher_id"],
        allocation["time_slot_id"]
    )

    if key in teacher_slots:

        teacher = teacher_map[
            allocation["teacher_id"]
        ]

        slot = slot_map[
            allocation["time_slot_id"]
        ]

        errors.append(
            f"Teacher conflict: "
            f"{teacher['name']} at "
            f"{slot['slot_name']}"
        )

    teacher_slots[key] = True

if not any(
    "Teacher conflict" in e
    for e in errors
):
    print("   PASS")


# ------------------------------------------------------------
# 4. CHECK ROOM CONFLICTS
# ------------------------------------------------------------

print()
print("4. CHECKING ROOM CONFLICTS")

room_slots = {}

for allocation in allocations:

    key = (
        allocation["room_id"],
        allocation["time_slot_id"]
    )

    if key in room_slots:

        room = room_map[
            allocation["room_id"]
        ]

        slot = slot_map[
            allocation["time_slot_id"]
        ]

        errors.append(
            f"Room conflict: "
            f"{room['room_number']} at "
            f"{slot['slot_name']}"
        )

    room_slots[key] = True

if not any(
    "Room conflict" in e
    for e in errors
):
    print("   PASS")


# ------------------------------------------------------------
# 5. CHECK TEACHER WORKLOAD
# ------------------------------------------------------------

print()
print("5. CHECKING TEACHER WORKLOAD")

teacher_hours = {}

for allocation in allocations:

    teacher_id = allocation["teacher_id"]

    teacher_hours[teacher_id] = (
        teacher_hours.get(teacher_id, 0) + 1
    )

workload_ok = True

for teacher in teachers:

    teacher_id = teacher["id"]

    hours = teacher_hours.get(
        teacher_id,
        0
    )

    maximum = teacher["max_hours_per_week"]

    print(
        f"   {teacher['name']}: "
        f"{hours}/{maximum}"
    )

    if hours > maximum:

        workload_ok = False

        errors.append(
            f"Teacher workload exceeded: "
            f"{teacher['name']}"
        )

if workload_ok:
    print("   PASS")


# ------------------------------------------------------------
# 6. CHECK ROOM CAPACITY
# ------------------------------------------------------------

print()
print("6. CHECKING ROOM CAPACITY")

capacity_ok = True

for allocation in allocations:

    room = room_map[
        allocation["room_id"]
    ]

    group = group_map[
        allocation["student_group_id"]
    ]

    if room["capacity"] < group["student_count"]:

        capacity_ok = False

        errors.append(
            f"Room capacity insufficient: "
            f"{room['room_number']} for "
            f"{group['name']}"
        )

if capacity_ok:
    print("   PASS")


# ------------------------------------------------------------
# 7. CHECK SUBJECT SESSIONS
# ------------------------------------------------------------

print()
print("7. CHECKING SUBJECT SESSIONS")

subject_group_count = {}

for allocation in allocations:

    key = (
        allocation["student_group_id"],
        allocation["subject_id"]
    )

    subject_group_count[key] = (
        subject_group_count.get(key, 0) + 1
    )

sessions_ok = True

for group in groups:

    for subject in subjects:

        key = (
            group["id"],
            subject["id"]
        )

        actual_count = subject_group_count.get(
            key,
            0
        )

        expected_count = subject[
            "weekly_sessions"
        ]

        if actual_count != expected_count:

            sessions_ok = False

            errors.append(
                f"{group['name']} - "
                f"{subject['code']}: "
                f"expected {expected_count}, "
                f"found {actual_count}"
            )

if sessions_ok:
    print("   PASS")


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

print()
print("=" * 60)

if errors:

    print("        VALIDATION FAILED")
    print("=" * 60)

    print()

    for error in errors:
        print("ERROR:", error)

else:

    print("        VALIDATION SUCCESSFUL")
    print("=" * 60)

    print()
    print(f"All {actual} timetable allocations are valid.")
    print()
    print("No student group conflicts.")
    print("No teacher conflicts.")
    print("No room conflicts.")
    print("Teacher workloads are valid.")
    print("Room capacities are valid.")
    print("Every subject has the required sessions.")

print()
print("=" * 60)
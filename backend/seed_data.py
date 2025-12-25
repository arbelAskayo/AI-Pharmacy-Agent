"""
Database seeding script.
Populates the database with synthetic data for testing.
Idempotent: safe to run multiple times.
"""
from datetime import datetime, timedelta
from database import get_db, init_db, is_db_seeded
from logging_config import get_logger

logger = get_logger(__name__)


# Seed data definitions
USERS = [
    {"name": "David Cohen", "hebrew_name": "דוד כהן", "phone": "050-1234567", "email": "david.cohen@email.com"},
    {"name": "Sarah Levi", "hebrew_name": "שרה לוי", "phone": "052-2345678", "email": "sarah.levi@email.com"},
    {"name": "Michael Ben-Ari", "hebrew_name": "מיכאל בן-ארי", "phone": "054-3456789", "email": "michael.benari@email.com"},
    {"name": "Rachel Goldstein", "hebrew_name": "רחל גולדשטיין", "phone": "053-4567890", "email": "rachel.gold@email.com"},
    {"name": "Yossi Mizrachi", "hebrew_name": "יוסי מזרחי", "phone": "050-5678901", "email": "yossi.m@email.com"},
    {"name": "Miriam Shapiro", "hebrew_name": "מרים שפירא", "phone": "052-6789012", "email": "miriam.shapiro@email.com"},
    {"name": "Avi Peretz", "hebrew_name": "אבי פרץ", "phone": "054-7890123", "email": "avi.peretz@email.com"},
    {"name": "Tamar Rosenberg", "hebrew_name": "תמר רוזנברג", "phone": "053-8901234", "email": "tamar.r@email.com"},
    {"name": "Dan Katz", "hebrew_name": "דן כץ", "phone": "050-9012345", "email": "dan.katz@email.com"},
    {"name": "Noa Friedman", "hebrew_name": "נועה פרידמן", "phone": "052-0123456", "email": "noa.friedman@email.com"},
]

MEDICATIONS = [
    {
        "name": "Aspirin",
        "hebrew_name": "אספירין",
        "active_ingredient": "Acetylsalicylic acid",
        "active_ingredient_hebrew": "חומצה אצטילסליצילית",
        "dosage_form": "Tablet",
        "strength": "500mg",
        "usage_instructions": "Take 1-2 tablets every 4-6 hours as needed for pain or fever. Do not exceed 8 tablets in 24 hours. Take with food or water.",
        "usage_instructions_hebrew": "ליטול 1-2 טבליות כל 4-6 שעות לפי הצורך לכאב או חום. לא לעבור 8 טבליות ב-24 שעות. ליטול עם אוכל או מים.",
        "requires_prescription": 0,
    },
    {
        "name": "Ibuprofen",
        "hebrew_name": "איבופרופן",
        "active_ingredient": "Ibuprofen",
        "active_ingredient_hebrew": "איבופרופן",
        "dosage_form": "Tablet",
        "strength": "400mg",
        "usage_instructions": "Take 1 tablet every 6-8 hours as needed for pain or inflammation. Maximum 3 tablets per day. Take with food.",
        "usage_instructions_hebrew": "ליטול טבליה אחת כל 6-8 שעות לפי הצורך לכאב או דלקת. מקסימום 3 טבליות ביום. ליטול עם אוכל.",
        "requires_prescription": 0,
    },
    {
        "name": "Amoxicillin",
        "hebrew_name": "אמוקסיצילין",
        "active_ingredient": "Amoxicillin trihydrate",
        "active_ingredient_hebrew": "אמוקסיצילין טריהידרט",
        "dosage_form": "Capsule",
        "strength": "500mg",
        "usage_instructions": "Take 1 capsule every 8 hours for 7-10 days as prescribed. Complete the full course even if feeling better. May be taken with or without food.",
        "usage_instructions_hebrew": "ליטול כמוסה אחת כל 8 שעות למשך 7-10 ימים לפי הוראת רופא. לסיים את הטיפול המלא גם אם מרגישים טוב יותר. ניתן ליטול עם או בלי אוכל.",
        "requires_prescription": 1,
    },
    {
        "name": "Omeprazole",
        "hebrew_name": "אומפרזול",
        "active_ingredient": "Omeprazole",
        "active_ingredient_hebrew": "אומפרזול",
        "dosage_form": "Capsule",
        "strength": "20mg",
        "usage_instructions": "Take 1 capsule once daily, preferably in the morning before breakfast. Swallow whole, do not crush or chew.",
        "usage_instructions_hebrew": "ליטול כמוסה אחת פעם ביום, עדיף בבוקר לפני ארוחת הבוקר. לבלוע בשלמות, לא לרסק או ללעוס.",
        "requires_prescription": 1,
    },
    {
        "name": "Vitamin D3",
        "hebrew_name": "ויטמין D3",
        "active_ingredient": "Cholecalciferol",
        "active_ingredient_hebrew": "כולקלציפרול",
        "dosage_form": "Softgel",
        "strength": "1000 IU",
        "usage_instructions": "Take 1 softgel daily with a meal containing fat for better absorption. Store in a cool, dry place.",
        "usage_instructions_hebrew": "ליטול כמוסת ג'ל אחת ביום עם ארוחה המכילה שומן לספיגה טובה יותר. לאחסן במקום קריר ויבש.",
        "requires_prescription": 0,
    },
]

BRANCHES = ["Main Street", "Downtown", "Airport"]


def clear_existing_data() -> None:
    """Clear all existing data from tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refill_requests")
        cursor.execute("DELETE FROM stock")
        cursor.execute("DELETE FROM prescriptions")
        cursor.execute("DELETE FROM medications")
        cursor.execute("DELETE FROM users")
        conn.commit()
    logger.info("database_cleared")


def seed_users() -> list[int]:
    """Seed users table and return list of user IDs."""
    user_ids = []
    with get_db() as conn:
        cursor = conn.cursor()
        for user in USERS:
            cursor.execute(
                """INSERT INTO users (name, hebrew_name, phone, email) 
                   VALUES (?, ?, ?, ?)""",
                (user["name"], user["hebrew_name"], user["phone"], user["email"])
            )
            user_ids.append(cursor.lastrowid)
        conn.commit()
    logger.info("users_seeded", count=len(user_ids))
    return user_ids


def seed_medications() -> list[int]:
    """Seed medications table and return list of medication IDs."""
    medication_ids = []
    with get_db() as conn:
        cursor = conn.cursor()
        for med in MEDICATIONS:
            cursor.execute(
                """INSERT INTO medications 
                   (name, hebrew_name, active_ingredient, active_ingredient_hebrew,
                    dosage_form, strength, usage_instructions, usage_instructions_hebrew,
                    requires_prescription) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (med["name"], med["hebrew_name"], med["active_ingredient"],
                 med["active_ingredient_hebrew"], med["dosage_form"], med["strength"],
                 med["usage_instructions"], med["usage_instructions_hebrew"],
                 med["requires_prescription"])
            )
            medication_ids.append(cursor.lastrowid)
        conn.commit()
    logger.info("medications_seeded", count=len(medication_ids))
    return medication_ids


def seed_stock(medication_ids: list[int]) -> None:
    """Seed stock table with varied quantities across branches."""
    stock_data = [
        # Aspirin - good stock at Main Street, low elsewhere
        (medication_ids[0], "Main Street", 150),
        (medication_ids[0], "Downtown", 25),
        (medication_ids[0], "Airport", 10),
        # Ibuprofen - moderate everywhere
        (medication_ids[1], "Main Street", 80),
        (medication_ids[1], "Downtown", 60),
        (medication_ids[1], "Airport", 40),
        # Amoxicillin - out of stock at Airport
        (medication_ids[2], "Main Street", 30),
        (medication_ids[2], "Downtown", 15),
        (medication_ids[2], "Airport", 0),
        # Omeprazole - low stock
        (medication_ids[3], "Main Street", 20),
        (medication_ids[3], "Downtown", 5),
        (medication_ids[3], "Airport", 8),
        # Vitamin D3 - high stock everywhere
        (medication_ids[4], "Main Street", 200),
        (medication_ids[4], "Downtown", 180),
        (medication_ids[4], "Airport", 150),
    ]
    
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        for med_id, branch, qty in stock_data:
            cursor.execute(
                """INSERT INTO stock (medication_id, branch, quantity, last_updated)
                   VALUES (?, ?, ?, ?)""",
                (med_id, branch, qty, now)
            )
        conn.commit()
    logger.info("stock_seeded", count=len(stock_data))


def seed_prescriptions(user_ids: list[int], medication_ids: list[int]) -> None:
    """Seed prescriptions with varied states (active, expired, refills used)."""
    today = datetime.now().date()
    
    # Get prescription medication IDs (Amoxicillin = index 2, Omeprazole = index 3)
    amoxicillin_id = medication_ids[2]
    omeprazole_id = medication_ids[3]
    
    prescriptions = [
        # User 1 (David Cohen) - Active Omeprazole, 3 refills remaining
        (user_ids[0], omeprazole_id, today - timedelta(days=60), today + timedelta(days=305), 5, 2, "Dr. Ruth Avraham"),
        
        # User 2 (Sarah Levi) - Active Amoxicillin, just prescribed
        (user_ids[1], amoxicillin_id, today - timedelta(days=3), today + timedelta(days=7), 0, 0, "Dr. Moshe Klein"),
        
        # User 3 (Michael Ben-Ari) - Expired prescription
        (user_ids[2], omeprazole_id, today - timedelta(days=400), today - timedelta(days=35), 3, 3, "Dr. Yael Stern"),
        
        # User 4 (Rachel Goldstein) - Active Omeprazole with all refills used
        (user_ids[3], omeprazole_id, today - timedelta(days=180), today + timedelta(days=185), 4, 4, "Dr. Oren Levy"),
        
        # User 5 (Yossi Mizrachi) - Active Amoxicillin
        (user_ids[4], amoxicillin_id, today - timedelta(days=1), today + timedelta(days=13), 1, 0, "Dr. Dana Cohen"),
        
        # User 6 (Miriam Shapiro) - Two active prescriptions
        (user_ids[5], omeprazole_id, today - timedelta(days=30), today + timedelta(days=335), 6, 1, "Dr. Eitan Rosen"),
        (user_ids[5], amoxicillin_id, today - timedelta(days=5), today + timedelta(days=5), 0, 0, "Dr. Eitan Rosen"),
        
        # User 7 (Avi Peretz) - Expired Amoxicillin
        (user_ids[6], amoxicillin_id, today - timedelta(days=60), today - timedelta(days=50), 0, 0, "Dr. Nir Barak"),
        
        # User 8 (Tamar Rosenberg) - Active Omeprazole, many refills remaining
        (user_ids[7], omeprazole_id, today - timedelta(days=10), today + timedelta(days=355), 12, 0, "Dr. Hila Marcus"),
        
        # User 9 (Dan Katz) - Multiple prescriptions, varied states
        (user_ids[8], omeprazole_id, today - timedelta(days=200), today + timedelta(days=165), 5, 3, "Dr. Gadi Weiss"),
        (user_ids[8], amoxicillin_id, today - timedelta(days=100), today - timedelta(days=90), 0, 0, "Dr. Gadi Weiss"),
        
        # User 10 (Noa Friedman) - Active Omeprazole
        (user_ids[9], omeprazole_id, today - timedelta(days=45), today + timedelta(days=320), 6, 2, "Dr. Shira Tal"),
        
        # Additional prescriptions for variety
        (user_ids[0], amoxicillin_id, today - timedelta(days=90), today - timedelta(days=80), 0, 0, "Dr. Ruth Avraham"),
        (user_ids[1], omeprazole_id, today - timedelta(days=15), today + timedelta(days=350), 10, 0, "Dr. Avi Carmel"),
        (user_ids[4], omeprazole_id, today - timedelta(days=120), today + timedelta(days=245), 8, 4, "Dr. Dana Cohen"),
    ]
    
    with get_db() as conn:
        cursor = conn.cursor()
        for user_id, med_id, prescribed, expiry, refills_allowed, refills_used, doctor in prescriptions:
            cursor.execute(
                """INSERT INTO prescriptions 
                   (user_id, medication_id, prescribed_date, expiry_date, 
                    refills_allowed, refills_used, prescribing_doctor)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, med_id, prescribed.isoformat(), expiry.isoformat(),
                 refills_allowed, refills_used, doctor)
            )
        conn.commit()
    logger.info("prescriptions_seeded", count=len(prescriptions))


def seed_database(force: bool = False) -> bool:
    """
    Seed the database with initial data.
    
    Args:
        force: If True, clear existing data and re-seed
        
    Returns:
        True if seeding was performed, False if already seeded
    """
    # First ensure tables exist
    init_db()
    
    # Check if already seeded
    if is_db_seeded() and not force:
        logger.info("database_already_seeded")
        return False
    
    logger.info("database_seeding_start")
    
    # Clear existing data if forcing re-seed
    if force:
        clear_existing_data()
    
    # Seed in order of dependencies
    user_ids = seed_users()
    medication_ids = seed_medications()
    seed_stock(medication_ids)
    seed_prescriptions(user_ids, medication_ids)
    
    logger.info("database_seeding_complete")
    return True


if __name__ == "__main__":
    # Allow running directly for testing
    from logging_config import configure_logging
    configure_logging()
    seed_database(force=True)
    print("Database seeded successfully!")


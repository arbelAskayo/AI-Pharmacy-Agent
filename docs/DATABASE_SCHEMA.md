# Pharmacy Database Schema Documentation

## Overview

The pharmacy database (`pharmacy.db`) is a SQLite database that stores information about users, medications, prescriptions, stock levels, and refill requests for a pharmacy chain with multiple branches.

**Database Location**: `backend/pharmacy.db`  
**Database Type**: SQLite 3  
**Encoding**: UTF-8 (supports Hebrew text)

## Database Statistics

| Table | Record Count | Description |
|-------|--------------|-------------|
| `users` | 10 | Customer profiles |
| `medications` | 5 | Medication catalog |
| `prescriptions` | 15 | User prescriptions (active & expired) |
| `stock` | 15 | Inventory across 3 branches |
| `refill_requests` | 0 | Prescription refill requests |

## Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│    users     │         │  prescriptions   │         │ medications  │
├──────────────┤         ├──────────────────┤         ├──────────────┤
│ id (PK)      │◄───────┤ user_id (FK)     │        │ id (PK)      │
│ name         │         │ medication_id(FK)├───────►│ name         │
│ hebrew_name  │         │ prescribed_date  │         │ hebrew_name  │
│ phone        │         │ expiry_date      │         │ ...          │
│ email        │         │ refills_allowed  │         └──────────────┘
└──────────────┘         │ refills_used     │                │
      │                  │ doctor           │                │
      │                  └──────────────────┘                │
      │                         │                            │
      │                         │                            │
      │                  ┌──────▼───────────┐               │
      │                  │ refill_requests  │               │
      │                  ├──────────────────┤               │
      └─────────────────►│ user_id (FK)     │               │
                         │ prescription_id  │               │
                         │ request_date     │               │
                         │ status           │               │
                         └──────────────────┘               │
                                                            │
                         ┌──────────────────┐               │
                         │     stock        │               │
                         ├──────────────────┤               │
                         │ medication_id(FK)├───────────────┘
                         │ branch           │
                         │ quantity         │
                         │ last_updated     │
                         └──────────────────┘
```

## Table Schemas

### 1. `users` Table

Stores customer/patient information.

**Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hebrew_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL
);
```

**Fields:**
- `id`: Unique user identifier (auto-increment)
- `name`: User's full name (English)
- `hebrew_name`: User's full name (Hebrew/עברית)
- `phone`: Phone number (format: `XXX-XXXXXXX`)
- `email`: Email address

**Sample Data:**
| id | name | hebrew_name | phone | email |
|----|------|-------------|-------|-------|
| 1 | David Cohen | דוד כהן | 050-1234567 | david.cohen@email.com |
| 2 | Sarah Levi | שרה לוי | 052-2345678 | sarah.levi@email.com |
| 3 | Michael Ben-Ari | מיכאל בן-ארי | 054-3456789 | michael.benari@email.com |

**Notes:**
- Phone numbers can be looked up in any format (with/without hyphens, spaces)
- Email lookups are case-insensitive
- All 10 users have at least one prescription (current or past)

---

### 2. `medications` Table

Catalog of available medications with bilingual information.

**Schema:**
```sql
CREATE TABLE medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hebrew_name TEXT NOT NULL,
    active_ingredient TEXT NOT NULL,
    active_ingredient_hebrew TEXT NOT NULL,
    dosage_form TEXT NOT NULL,
    strength TEXT NOT NULL,
    usage_instructions TEXT NOT NULL,
    usage_instructions_hebrew TEXT NOT NULL,
    requires_prescription INTEGER NOT NULL DEFAULT 0
);
```

**Fields:**
- `id`: Unique medication identifier
- `name`: Medication name (English)
- `hebrew_name`: Medication name (Hebrew)
- `active_ingredient`: Active pharmaceutical ingredient (English)
- `active_ingredient_hebrew`: Active ingredient (Hebrew)
- `dosage_form`: Form of medication (Tablet, Capsule, Softgel, etc.)
- `strength`: Dosage strength (e.g., "500mg", "20mg", "1000 IU")
- `usage_instructions`: How to take the medication (English)
- `usage_instructions_hebrew`: Usage instructions (Hebrew)
- `requires_prescription`: `1` if prescription required, `0` if OTC

**Complete Medication List:**

| ID | Name | Hebrew Name | Active Ingredient | Form | Strength | Rx Required |
|----|------|-------------|-------------------|------|----------|-------------|
| 1 | Aspirin | אספירין | Acetylsalicylic acid | Tablet | 500mg | No (OTC) |
| 2 | Ibuprofen | איבופרופן | Ibuprofen | Tablet | 400mg | No (OTC) |
| 3 | Amoxicillin | אמוקסיצילין | Amoxicillin trihydrate | Capsule | 500mg | **Yes** |
| 4 | Omeprazole | אומפרזול | Omeprazole | Capsule | 20mg | **Yes** |
| 5 | Vitamin D3 | ויטמין D3 | Cholecalciferol | Softgel | 1000 IU | No (OTC) |

**Medication Categories:**
- **OTC (Over-The-Counter)**: Aspirin, Ibuprofen, Vitamin D3
- **Prescription Required**: Amoxicillin, Omeprazole

---

### 3. `prescriptions` Table

Tracks user prescriptions with refill information.

**Schema:**
```sql
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    prescribed_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    refills_allowed INTEGER NOT NULL,
    refills_used INTEGER NOT NULL DEFAULT 0,
    prescribing_doctor TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);
```

**Fields:**
- `id`: Unique prescription identifier
- `user_id`: Reference to `users.id`
- `medication_id`: Reference to `medications.id`
- `prescribed_date`: Date prescription was written (ISO 8601: `YYYY-MM-DD`)
- `expiry_date`: Date prescription expires (ISO 8601: `YYYY-MM-DD`)
- `refills_allowed`: Total number of refills permitted
- `refills_used`: Number of refills already used
- `prescribing_doctor`: Name of prescribing doctor

**Prescription Status Logic:**
- **Expired**: `expiry_date < CURRENT_DATE`
- **No Refills**: `refills_used >= refills_allowed`
- **Active**: `expiry_date >= CURRENT_DATE AND refills_used < refills_allowed`

**Statistics:**
- Total prescriptions: **15**
- Active prescriptions: **7**
- Expired prescriptions: **4**
- No refills remaining: **4**

**Sample Prescriptions:**
```sql
-- Active prescription with refills
Rx #1: David Cohen - Omeprazole
  Prescribed: 2025-10-26 | Expires: 2026-10-26
  Refills: 3 remaining (used 2 of 5)
  Doctor: Dr. Ruth Avraham

-- Expired prescription
Rx #3: Michael Ben-Ari - Omeprazole
  Prescribed: 2024-11-20 | Expired: 2025-11-20
  Refills: All used (3 of 3)
  Doctor: Dr. Yael Stern
```

---

### 4. `stock` Table

Inventory levels for each medication at each branch.

**Schema:**
```sql
CREATE TABLE stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    branch TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);
```

**Fields:**
- `id`: Unique stock record identifier
- `medication_id`: Reference to `medications.id`
- `branch`: Branch name (`"Main Street"`, `"Downtown"`, `"Airport"`)
- `quantity`: Current inventory count
- `last_updated`: Last inventory update timestamp (ISO 8601)

**Branches:**
1. **Main Street** - Flagship location
2. **Downtown** - City center branch
3. **Airport** - Travel-focused branch

**Stock Levels Summary:**

| Medication | Main Street | Downtown | Airport | Total |
|------------|-------------|----------|---------|-------|
| Aspirin | 150 | 25 | 10 | **185** |
| Ibuprofen | 80 | 60 | 40 | **180** |
| Amoxicillin | 30 | 15 | **0** ⚠️ | **45** |
| Omeprazole | 20 | 5 | 8 | **33** |
| Vitamin D3 | 200 | 180 | 150 | **530** |

**Stock Status:**
- ✅ **High Stock**: Aspirin, Ibuprofen, Vitamin D3
- ⚠️ **Low Stock**: Omeprazole (Downtown: 5 units)
- ❌ **Out of Stock**: Amoxicillin at Airport branch

---

### 5. `refill_requests` Table

Tracks prescription refill requests from users.

**Schema:**
```sql
CREATE TABLE refill_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prescription_id INTEGER NOT NULL,
    request_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);
```

**Fields:**
- `id`: Unique request identifier
- `user_id`: Reference to `users.id`
- `prescription_id`: Reference to `prescriptions.id`
- `request_date`: When refill was requested (ISO 8601 timestamp)
- `status`: Request status (`"pending"`, `"approved"`, `"rejected"`, `"completed"`)

**Current State:**
- **0 refill requests** in database (fresh system)

---

## Data Relationships

### Foreign Key Constraints

1. **`prescriptions.user_id` → `users.id`**
   - Each prescription belongs to one user
   - Users can have multiple prescriptions

2. **`prescriptions.medication_id` → `medications.id`**
   - Each prescription is for one medication
   - Medications can appear in multiple prescriptions

3. **`stock.medication_id` → `medications.id`**
   - Each stock record tracks one medication
   - One medication can have stock at multiple branches

4. **`refill_requests.user_id` → `users.id`**
   - Each refill request is made by one user

5. **`refill_requests.prescription_id` → `prescriptions.id`**
   - Each refill request is for one specific prescription

---

## Common Queries

### Find User by Phone (with normalization)
```sql
-- Finds user regardless of phone format
SELECT * FROM users 
WHERE REPLACE(REPLACE(phone, '-', ''), ' ', '') LIKE '%0501234567%';
```

### Check Medication Stock
```sql
-- Get stock levels for a medication across all branches
SELECT m.name, s.branch, s.quantity, s.last_updated
FROM stock s
JOIN medications m ON s.medication_id = m.id
WHERE m.name = 'Aspirin'
ORDER BY s.branch;
```

### List Active Prescriptions for User
```sql
-- Get active prescriptions with refills available
SELECT 
    u.name,
    m.name as medication,
    p.expiry_date,
    (p.refills_allowed - p.refills_used) as refills_remaining,
    p.prescribing_doctor
FROM prescriptions p
JOIN users u ON p.user_id = u.id
JOIN medications m ON p.medication_id = m.id
WHERE p.user_id = 1 
  AND p.expiry_date >= date('now')
  AND p.refills_used < p.refills_allowed;
```

### Find Low Stock Items
```sql
-- Medications with quantity below threshold
SELECT m.name, s.branch, s.quantity
FROM stock s
JOIN medications m ON s.medication_id = m.id
WHERE s.quantity < 30
ORDER BY s.quantity ASC;
```

### Expired Prescriptions
```sql
-- Find all expired prescriptions
SELECT 
    u.name,
    m.name as medication,
    p.expiry_date,
    p.prescribing_doctor
FROM prescriptions p
JOIN users u ON p.user_id = u.id
JOIN medications m ON p.medication_id = m.id
WHERE p.expiry_date < date('now')
ORDER BY p.expiry_date DESC;
```

---

## Database Management

### Initialize Database
```bash
cd backend
python -c "from database import init_db; init_db()"
```

### Seed Database (Reset & Populate)
```bash
cd backend
python seed_data.py
```

### Backup Database
```bash
cd backend
sqlite3 pharmacy.db ".backup pharmacy_backup_$(date +%Y%m%d).db"
```

### View Database in Terminal
```bash
cd backend
sqlite3 pharmacy.db

# SQLite commands:
.tables              # List all tables
.schema users        # Show table schema
.mode column         # Format output
.headers on          # Show column names
SELECT * FROM users; # Query data
.quit                # Exit
```

### Access via GUI
- **DB Browser for SQLite**: https://sqlitebrowser.org/
- Open `backend/pharmacy.db` file directly

---

## Notes & Best Practices

### Date Format
All dates use **ISO 8601** format: `YYYY-MM-DD` (e.g., `2025-12-25`)
- Easily comparable as strings
- SQLite date functions work correctly

### Boolean Fields
SQLite doesn't have native boolean type:
- `1` = True
- `0` = False
- Example: `requires_prescription` (0 = OTC, 1 = Rx required)

### Text Encoding
- UTF-8 encoding supports Hebrew characters
- All Hebrew fields properly stored and retrieved
- Use `dir="auto"` in HTML for proper RTL display

### Normalization in Queries
Phone numbers and branch names support flexible matching:
- Phone: `"050-1234567"` = `"0501234567"` = `"050 123 4567"`
- Branch: `"Main Street"` = `"MainStreet"` = `"main-street"`

See: `backend/utils/normalization.py`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-25 | Initial schema with 5 tables |
| 1.1 | 2025-12-25 | Added input normalization support |

---

## Related Documentation

- [Backend API Documentation](../backend/README.md)
- [Database Seeding Guide](../backend/seed_data.py)
- [Input Normalization](../backend/utils/normalization.py)
- [Repository Layer](../backend/repositories/)


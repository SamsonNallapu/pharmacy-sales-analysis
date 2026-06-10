"""
generate_data.py
----------------
Generates a synthetic (but realistically messy) community pharmacy
dispensing dataset for the cleaning & analysis project.

The messiness is deliberate and mirrors real-world data problems:
- duplicate rows
- missing values
- inconsistent date formats
- inconsistent text casing / whitespace
- prices stored as text with currency symbols
- impossible values (negative quantities)
"""

import random
import csv
from datetime import datetime, timedelta

random.seed(42)

CATEGORIES = {
    "Paracetamol 500mg": ("Pain Relief", 1.10),
    "Ibuprofen 200mg": ("Pain Relief", 1.45),
    "Amoxicillin 250mg": ("Antibiotics", 3.20),
    "Omeprazole 20mg": ("Gastro", 2.10),
    "Cetirizine 10mg": ("Allergy", 1.25),
    "Loratadine 10mg": ("Allergy", 1.30),
    "Salbutamol Inhaler": ("Respiratory", 6.50),
    "Atorvastatin 20mg": ("Cardiovascular", 2.80),
    "Metformin 500mg": ("Diabetes", 1.90),
    "Vitamin D 1000IU": ("Supplements", 3.50),
}

PAYMENT_TYPES = ["NHS Prescription", "Private Prescription", "OTC Sale"]
DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"]  # mixed on purpose


def messy_case(text: str) -> str:
    """Randomly mangle casing/whitespace like sloppy manual entry."""
    roll = random.random()
    if roll < 0.15:
        return text.upper()
    if roll < 0.25:
        return text.lower()
    if roll < 0.32:
        return "  " + text + " "
    return text


def make_rows(n: int = 1200):
    rows = []
    start = datetime(2025, 1, 1)
    for i in range(n):
        product = random.choice(list(CATEGORIES))
        category, base_price = CATEGORIES[product]
        date = start + timedelta(days=random.randint(0, 364),
                                 hours=random.randint(8, 18))

        qty = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        if random.random() < 0.01:          # ~1% impossible values
            qty = -qty

        price = round(base_price * random.uniform(0.95, 1.10), 2)
        price_str = f"£{price}" if random.random() < 0.4 else str(price)

        rows.append({
            "transaction_id": f"TXN{10000 + i}",
            "date": date.strftime(random.choice(DATE_FORMATS)),
            "product_name": messy_case(product),
            "category": messy_case(category) if random.random() > 0.05 else "",
            "quantity": qty if random.random() > 0.02 else "",
            "unit_price": price_str if random.random() > 0.03 else "",
            "payment_type": messy_case(random.choice(PAYMENT_TYPES)),
        })

    # inject ~2% duplicate rows
    dupes = random.sample(rows, k=int(n * 0.02))
    rows.extend(dupes)
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = make_rows()
    with open("data/raw/pharmacy_sales_raw.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to data/raw/pharmacy_sales_raw.csv")

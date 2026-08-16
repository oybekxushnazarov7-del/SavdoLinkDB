import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List


def load_reference(path: Path) -> dict:
    """Mavjud do'kon/mahsulot ro'yxati va ma'lumotlarini fayldan o'qiydi."""
    with open(path, "r", encoding="utf-8") as f:
        if path.suffix.lower() == ".json":
            return json.load(f)
        else:
            reader = csv.DictReader(f, delimiter=";")
            return {"data": list(reader)}


def generate_day(
    day: date,
    stores: List[str],
    products: List[Dict[str, Any]],
    receipts_per_store: int,
    seed: int,
) -> List[dict]:
    """Bir kunlik cheklar va ulardagi sotuv qatorlarini generatsiya qiladi."""
    # Bir xil seed orqali har safar qayta chaqirilganda bir xil natija olish (reproducibility)
    day_seed = seed + int(day.strftime("%Y%m%d"))
    random.seed(day_seed)

    rows = []

    # Dam olish kunlarida (Shanba=5, Yakshanba=6) savdo hajmini oshirish
    is_weekend = day.weekday() in (5, 6)
    multiplier = 1.4 if is_weekend else 1.0
    actual_receipts = int(receipts_per_store * multiplier)

    # Mahsulotlarga talab notekis bo'lishi uchun vaznlar (weights) belgilash
    weights = [1 / (i + 1) for i in range(len(products))]

    for store_code in stores:
        for receipt_idx in range(1, actual_receipts + 1):
            receipt_no = f"REC-{day.strftime('%Y%m%d')}-{store_code}-{receipt_idx:04d}"
            
            # Har bir chekda 1 tadan 5 tagacha turli mahsulot bo'lishi mumkin
            items_count = random.randint(1, 5)
            selected_products = random.choices(products, weights=weights, k=items_count)

            # Kun davomidagi vaqtni tasodifiy tanlash (08:00 dan 22:00 gacha)
            random_seconds = random.randint(8 * 3600, 22 * 3600)
            sale_time = (
                timedelta(seconds=random_seconds)
            )
            sale_datetime_str = f"{day.strftime('%Y-%m-%d')} {str(sale_time)}"

            for prod in selected_products:
                qty = random.randint(1, 4)
                price = prod.get("price", 10000)
                discount = random.choice([0, 0, 0, 500, 1000])

                rows.append({
                    "receipt_no": receipt_no,
                    "store_code": store_code,
                    "cashier_id": f"CASH-{random.randint(1, 10):02d}",
                    "sale_datetime_raw": sale_datetime_str,
                    "sku": prod.get("sku", "SKU-UNKNOWN"),
                    "qty_raw": str(qty),
                    "unit_price_raw": str(price),
                    "discount_raw": str(discount),
                    "payment_type": random.choice(["CARD", "CASH", "CARD"]),
                })

    return rows


def write_day(rows: List[dict], out_dir: Path, day: date) -> Path:
    """Generatsiya qilingan ma'lumotlarni kunlik CSV faylga yozadi."""
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"sales_{day.strftime('%Y_%m_%d')}.csv"

    fieldnames = [
        "receipt_no",
        "store_code",
        "cashier_id",
        "sale_datetime_raw",
        "sku",
        "qty_raw",
        "unit_price_raw",
        "discount_raw",
        "payment_type",
    ]

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    return file_path


def main():
    """CLI argumentlarini qabul qiladi va generatsiyani boshqaradi."""
    parser = argparse.ArgumentParser(
        description="Katta hajmda test ma'lumotlarini (scale data) generatsiya qilish skripti."
    )
    parser.add_argument("--days", type=int, default=30, help="Generatsiya qilinadigan kunlar soni")
    parser.add_argument(
        "--receipts-per-store",
        type=int,
        default=500,
        help="Bitta do'kondagi kunlik o'rtacha cheklar soni",
    )
    parser.add_argument("--seed", type=int, default=42, help="Takrorlanuvchanlik uchun random seed")
    parser.add_argument(
        "--out", type=str, default="data/raw_scaled", help="Chiquvchi papka yo'li"
    )
    parser.add_argument(
        "--ref-products", type=str, default="data/products.json", help="Mahsulotlar moslamasi fayli"
    )

    args = parser.parse_args()

    out_dir = Path(args.out)
    ref_path = Path(args.ref_products)

    # Malumot va do'konlar bazasi shabloni
    stores = ["STORE_01", "STORE_02", "STORE_03", "STORE_04", "STORE_05"]
    
    if ref_path.exists():
        ref_data = load_reference(ref_path)
        products = ref_data if isinstance(ref_data, list) else ref_data.get("data", [])
    else:
        # Baza fayli bo'lmagan holat uchun standart shablon mahsulotlar
        products = [
            {"sku": f"SKU-{i:03d}", "price": random.choice([5000, 12000, 25000, 45000])}
            for i in range(1, 51)
        ]

    start_date = date.today() - timedelta(days=args.days)
    total_rows = 0

    print(f"Generatsiya boshlandi... Seed: {args.seed}")

    for day_offset in range(args.days):
        current_day = start_date + timedelta(days=day_offset)
        rows = generate_day(
            day=current_day,
            stores=stores,
            products=products,
            receipts_per_store=args.receipts_per_store,
            seed=args.seed,
        )
        saved_file = write_day(rows, out_dir, current_day)
        total_rows += len(rows)
        print(f"Yozildi: {saved_file} ({len(rows)} qator)")

    print(f"\nTugallandi! Jami {total_rows} ta savdo qatori yaratildi.")


if __name__ == "__main__":
    main()
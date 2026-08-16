from pathlib import Path
from src.extract.csv_extractor import CsvExtractor

def main():
    # Fayl yo'lini belgilaymiz
    file_path = Path("data/incoming/sales_2026-01-14.csv")
    
    # Fayl mavjudligini tekshiramiz
    if not file_path.exists():
        print(f"Xatolik: {file_path} fayli topilmadi!")
        print("Iltimos, avval test ma'lumotlarini generatsiya qiling yoki fayl yo'lini tekshiring.")
        return

    print("--- Extract (S2) Tekshiruvi Boshlandi ---\n")

    # 1. Dastlabki 3 ta qatorni chiqarib ko'rish
    extractor = CsvExtractor(file_path)
    print("Dastlabki 3 ta qator:")
    for i, row in enumerate(extractor):
        print(row)
        if i >= 2:
            break

    print("\n-----------------------------------------")

    # 2. Fayldagi barcha qatorlar sonini hisoblash
    full_extractor = CsvExtractor(file_path)
    total_rows = len(list(full_extractor))
    print(f"Jami qatorlar soni: {total_rows} qator")

if __name__ == "__main__":
    main()
# SavdoLink ETL & Analytics: Texnik Tahlil va Hujjatlashtirish

### Q1. Kursor va to'plamli (set-based) yechim unumdorligi o'rtasidagi farq nimada?
12 ta do'kon uchun kunlik agregat hisobot tayyorlashda SQL Kursor 4.8 soniya, to'plamli `GROUP BY` so'rovi esa 0.31 soniya vaqt oldi (15 barobar tezroq)[cite: 3]. Kursor har bir qator yoki do'kon uchun alohida so'rov bajarib, jadvalga 12 marta murojaat qilsa, to'plamli usul bitta o'tishda (single pass) xotirada hisoblaydi[cite: 3].

### Q2. Idempotentlik printsipi ETL quvurida qanday ta'minlangan?
Idempotency `mart.usp_RefreshDailyFacts` saqlanadigan protsedurasida `DELETE-INSERT` namunasi orqali amalga oshirilgan[cite: 3]. Berilgan sana oralig'idagi ma'lumotlar qayta yuklanganda, avval shu davrga tegishli eski ma'lumotlar o'chiriladi va yangilari yoziladi[cite: 3]. Bu jarayon necha marta takrorlanishidan qat'i nazar, bazada dublikat ma'lumotlar hosil bo'lmaydi[cite: 3].

### Q3. Data Quality (DQ) rad etilgan ma'lumotlar bilan qanday ishlaydi?
Xato yoki yetishmayotgan ustunlarga ega ma'lumotlar quvurni to'xtatib qo'ymaydi[cite: 3]. Validatsiyadan o'tmagan qatorlar `audit.DQErrorLog` jadvaliga xatolik sababi bilan yoziladi va o'tkazib yuboriladi[cite: 3]. Faqat yaroqli (valid) qatorlar tranzaksiya ichida `core` jadvallariga yuklanadi[cite: 3].

### Q4. Nega pul qiymatlari uchun Float emas Decimal va maxsus Money klassi ishlatildi?
Suvchivergulli sonlar (`float`) kompyuter xotirasida ikkilik sanoq tizimida yaxlitlash xatolariga olib keladi (masalan, `0.1 + 0.2 = 0.30000000000000004`). Moliya va hisob-kitob tizimlarida har bir tiyin aniq bo'lishi shartligi uchun `Decimal` turi va doimiy valyutani nazorat qiluvchi `Money` value-object ishlatilgan[cite: 3].

*(...Qolgan savollar ushbu formatda loyiha raqamlari asosida to'ldiriladi...)*
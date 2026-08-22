"""
Vazifasi: Bazaga yuklash idempotentsiyasini sinash.
"""
def test_idempotent_behavior_concept():
    # Transaction delete-insert mantiqining ishlash simulyatsiyasi
    initial_records = [1, 2, 3]
    new_records = [1, 2, 3]
    
    # Eskilarini o'chirish va qayta yozish
    cleared = [r for r in initial_records if r not in new_records]
    final_records = cleared + new_records
    
    assert len(final_records) == 3
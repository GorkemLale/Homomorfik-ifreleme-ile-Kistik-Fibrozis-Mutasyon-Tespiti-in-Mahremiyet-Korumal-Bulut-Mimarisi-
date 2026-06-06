from data import HEALTHY_CFTR, MUTATED_CFTR
from dna_utils import dna_to_numbers, pad_sequences, generate_random_mask, numbers_to_dna
from encryption_utils import SEALEngine, SEALEvaluator

def main():
    print("=== Microsoft SEAL (Dogrudan) PQC DNA Karsilastirma Projesi ===\n")
    
    # 1. String to Number Conversion
    print("--- 1. Asama: DNA Dizilimlerini Sayilara Cevirme ---")
    healthy_nums = dna_to_numbers(HEALTHY_CFTR)
    mutated_nums = dna_to_numbers(MUTATED_CFTR)
    
    print(f"Saglikli CFTR Uzunlugu: {len(healthy_nums)}")
    print(f"Mutasyonlu CFTR Uzunlugu: {len(mutated_nums)}")
    
    # Pad sequences to match lengths
    healthy_nums, mutated_nums = pad_sequences(healthy_nums, mutated_nums)
    vector_length = len(healthy_nums)
    
    print("\n[A=1, T=2, C=3, G=4]")
    print(f"Saglikli (Ilk 20):  {healthy_nums[:20]}")
    print(f"Mutasyonlu (Ilk 20):{mutated_nums[:20]}")
    
    # 2. Random Masking (R) - Kriptografik güvenli
    print("\n--- 2. Asama: Kriptografik Guvenli R Vektoru ile Maskeleme ---")
    R = generate_random_mask(vector_length)
    
    # Multiply element-wise
    masked_healthy = [h * r for h, r in zip(healthy_nums, R)]
    masked_mutated = [m * r for m, r in zip(mutated_nums, R)]
    
    print(f"Rastgele Vektor (R) (Ilk 10): {R[:10]}")
    print(f"Maskelenmis Saglikli (Ilk 10): {masked_healthy[:10]}")
    print(f"Maskelenmis Mutasyonlu (Ilk 10): {masked_mutated[:10]}")
    print("Maskeleme tamamlandi (secrets modulu - kriptografik guvenli).")
    
    # 3. PQC / FHE Encryption (Microsoft SEAL - Doğrudan)
    print("\n--- 3. Asama: PQC FHE Sifreleme (Microsoft SEAL - Dogrudan) ---")
    print("Microsoft SEAL BFV Baglami olusturuluyor...")
    engine = SEALEngine()
    print(f"Microsoft SEAL BFV Sifreleme Motoru hazir.")
    print(f"  - Polinom Derece: {engine.slot_count}")
    print(f"  - Sema: BFV (Brakerski/Fan-Vercauteren)")
    print(f"  - Guvenlik Seviyesi: ~128-bit (Post-Quantum Lattice-Based)")
    print("Public Key ve Secret Key uretildi.")
    print("  * Secret Key: Yalnizca istemcide (bu makinede) saklanir.")
    print("  * Public Key: Sunucuya gonderilebilir.")
    
    # Encrypt the masked data
    print("Maskelenmis veriler Microsoft SEAL ile sifreleniyor...")
    enc_healthy_bytes = engine.encrypt_vector(masked_healthy)
    enc_mutated_bytes = engine.encrypt_vector(masked_mutated)
    print(f"Sifreleme basarili.")
    print(f"  - Sifreli Saglikli Boyut: {len(enc_healthy_bytes):,} byte")
    print(f"  - Sifreli Mutasyonlu Boyut: {len(enc_mutated_bytes):,} byte")
    
    # 4. Hospital Database / Cloud Computation (Simüle)
    print("\n--- 4. Asama: Hastane Sunucusu (Sifreli Hesaplama) ---")
    print("Sunucu genetik verileri veya maskeleri bilmeden, sadece sifreli vektorleri alir.")
    print("Sunucuda Secret Key YOKTUR - verilerin icerigini goremez!")
    
    # Sunucu tarafını simüle et
    parms_bytes = engine.get_public_context_bytes()['parms']
    server_evaluator = SEALEvaluator(parms_bytes)
    
    print("Sunucu isliyor: E(Mutasyonlu) - E(Saglikli)...")
    enc_diff_bytes = server_evaluator.compute_difference(enc_mutated_bytes, enc_healthy_bytes)
    print(f"Sunucu hesaplama tamamlandi. Sonuc boyutu: {len(enc_diff_bytes):,} byte")
    
    # 5. Decryption and Risk Analysis
    print("\n--- 5. Asama: Sifre Cozme ve Risk Analizi ---")
    print("Kullanici tarafinda (Gizli anahtara sahip olan) sifre cozuluyor...")
    diff_result = engine.decrypt_vector(enc_diff_bytes)
    
    # Count differences (only within the actual data range)
    differences = 0
    for i in range(vector_length):
        if diff_result[i] != 0:
            differences += 1
            
    risk_percentage = (differences / vector_length) * 100
    
    print(f"\nToplam incelenen gen boyutu: {vector_length}")
    print(f"Tespit edilen farklilik/mutasyon skoru: {differences}")
    print(f"Hastalik Risk Yuzdesi: %{risk_percentage:.2f}")
    
    if differences > 0:
        print("Sonuc: MUTASYON TESPIT EDILDI! (Kistik Fibroz - ΔF508 suphesi)")
    else:
        print("Sonuc: Mutasyon bulunmadi, genom saglikli.")

if __name__ == "__main__":
    main()

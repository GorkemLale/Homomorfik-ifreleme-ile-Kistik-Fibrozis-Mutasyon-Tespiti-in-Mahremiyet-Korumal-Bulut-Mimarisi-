# Proje Kod Mantığı ve Matematiksel Modeli

Bu doküman, projemizde geliştirilen sistemin (İstemci-Sunucu tabanlı DNA Mutasyon Analizi) arka planında yatan matematiksel ve mantıksal işleyişi adım adım açıklamaktadır. Sistem, **Tam Homomorfik Şifreleme (Fully Homomorphic Encryption - FHE)** kullanarak verilerin (DNA dizilimlerinin) bulut sunucusunda gizliliği korunarak işlenmesini sağlar.

**Kullanılan Kütüphane:** Microsoft SEAL (seal-python bağlamaları ile doğrudan kullanım)  
**Şifreleme Şeması:** BFV (Brakerski/Fan-Vercauteren)  
**Güvenlik Temeli:** RLWE (Ring Learning With Errors) — Lattice-based, Post-Quantum dayanıklı kriptografi

## 1. DNA Verisinin Sayısallaştırılması (Mapping)
İlk adımda, metinsel DNA dizileri (A, T, C, G) bilgisayarın ve şifreleme algoritmalarının işleyebileceği matematiksel vektörlere dönüştürülür.
* **Fonksiyon:** `dna_to_numbers(dna_string)` (İlgili dosya: `dna_utils.py`)
* **Matematiksel Dönüşüm:**
  - A (Adenin) $\rightarrow 1$
  - T (Timin)  $\rightarrow 2$
  - C (Sitozin) $\rightarrow 3$
  - G (Guanin)  $\rightarrow 4$

Örneğin, "ATCG" dizisi $V = [1, 2, 3, 4]$ vektörüne dönüşür.

Eğer karşılaştırılacak iki dizi (Sağlıklı DNA ve Mutasyonlu DNA) farklı uzunluklardaysa, `pad_sequences` fonksiyonu ile kısa olan dizinin sonuna `0` (boşluk/etkisiz eleman) eklenerek iki dizinin matematiksel vektör boyutları ($L$) eşitlenir.

* $H = [h_1, h_2, ..., h_L]$ (Sağlıklı DNA Vektörü)
* $M = [m_1, m_2, ..., m_L]$ (Mutasyonlu/Test Edilen DNA Vektörü)

## 2. Rastgele Maskeleme (Random Masking)
Veri güvenliğini şifreleme algoritmasının yanı sıra temel matematiksel bir perdelemeyle de artırmak ve sunucunun hesaplanan farktan orijinal dizileri tersine mühendislikle bulmasını zorlaştırmak için bir maskeleme işlemi uygulanır.
* **Vektör Oluşturma:** Uzunluğu $L$ olan ve $1$ ile $1000$ arasında **kriptografik olarak güvenli** rastgele tam sayılardan oluşan bir $R$ vektörü üretilir. Python `secrets` modülü kullanılır (CSPRNG - Cryptographically Secure Pseudo-Random Number Generator).
  $$R = [r_1, r_2, ..., r_L]$$
* **Maskeleme İşlemi:** Orijinal DNA vektörleri, bu rastgele $R$ vektörü ile eleman bazında (element-wise) çarpılır:
  $$H' = H \circ R \Rightarrow H'_i = h_i \times r_i$$
  $$M' = M \circ R \Rightarrow M'_i = m_i \times r_i$$
Bu sayede şifrelenecek temel veriler rastgele değerlerle büyütülerek asıl dizi yapıları gizlenmiş olur.

## 3. Homomorfik Şifreleme (FHE Encryption)
Maskelenmiş $H'$ ve $M'$ vektörleri, **doğrudan Microsoft SEAL kütüphanesi** (`seal-python` bağlamaları) kullanılarak şifrelenir.

### Microsoft SEAL Parametreleri
- **Şema:** BFV (Brakerski/Fan-Vercauteren) — tam sayı aritmetiği için optimize
- **Polinom Derece:** $n = 8192$ → ~128-bit güvenlik seviyesi
- **Katsayı Modülü:** `CoeffModulus.BFVDefault(8192)` → SEAL'ın önerdiği güvenli parametreler
- **Düz Metin Modülü:** `PlainModulus.Batching(8192, 20)` → 20-bit, SIMD batching destekli

### Anahtar Üretimi ve Güvenlik
Microsoft SEAL `KeyGenerator` sınıfı kullanılarak:
- **Public Key (Açık Anahtar):** Şifreleme için kullanılır. Sunucuya gönderilebilir.
- **Secret Key (Gizli Anahtar):** Şifre çözme için kullanılır. **Yalnızca istemcide saklanır, ağ üzerinden asla gönderilmez.**

* Şifreleme fonksiyonunu $E(\cdot)$ ile gösterelim.
* İstemci, gizli anahtarını (Secret Key) sadece kendisinde saklar; ağ üzerinden sunucuya sadece **şifreli veriler** ve **şifreleme parametreleri** gönderilir.
  $$Enc_{H'} = E(H')$$
  $$Enc_{M'} = E(M')$$

### Vektör İşleme
Microsoft SEAL'ın `BatchEncoder` sınıfı, bir tam sayı vektörünü tek bir `Plaintext` polinomuna paketler (SIMD — Single Instruction, Multiple Data). `Encryptor` sınıfı bu düz metni `Ciphertext` nesnesine şifreler.

## 4. Sunucu Tarafı Hesaplama (Homomorphic Evaluation)
Sunucu tarafı (`server_app.py`), verilerin şifresini çözemez ve gerçek gen dizilimlerini asla göremez. Sunucu yalnızca şifreleme parametrelerini alır — Secret Key'e sahip **DEĞİLDİR**.

Microsoft SEAL'ın `Evaluator` sınıfı kullanılarak, iki şifreli vektör arasındaki fark hesaplanır:
$$Enc_{Diff} = Enc_{M'} \ominus Enc_{H'}$$

Homomorfik şifreleme teorisindeki çıkarma özelliği sayesinde bu işlem, aslında şifresiz hallerinin farkının şifrelenmiş haline eşittir:
$$E(M') \ominus E(H') = E(M' - H')$$
Sunucu bu elde ettiği yeni şifreli fark vektörünü ($Enc_{Diff}$) istemciye analiz için geri gönderir.

## 5. İstemci Tarafı Şifre Çözme (Decryption)
İstemci (Kullanıcı makinesi veya güvenli Hastane terminali) kendi gizli anahtarı ile sunucudan gelen sonucun şifresini çözer. Microsoft SEAL'ın `Decryptor` sınıfı kullanılır:
$$Diff = Decrypt(Enc_{Diff}) = M' - H'$$

Buradaki $i$. elemanı matematiksel olarak incelediğimizde:
$$Diff_i = M'_i - H'_i = (m_i \times r_i) - (h_i \times r_i)$$
$$Diff_i = r_i \times (m_i - h_i)$$

## 6. Risk Analizi ve Mutasyon Tespiti
İstemci algoritması ( `client_backend.py` ), şifresi çözülen `Diff` vektörü üzerinden risk oranını ve mutasyon durumunu hesaplar:
* **Eğer $m_i = h_i$ ise (o noktadaki baz aynı / sağlıklı ise):**
  $$Diff_i = r_i \times (0) = 0$$ olarak elde edilir.
* **Eğer $m_i \neq h_i$ ise (o noktada bir mutasyon/değişim varsa):**
  $$Diff_i = r_i \times (m_i - h_i) \neq 0$$ olarak elde edilir. (Maske vektörü $R$'nin elemanları $\geq 1$ olarak seçildiği için sıfır olma ihtimali yoktur.)

**Sonuç ve Çıktı:**
Algoritma, $Diff$ vektöründeki **0'dan farklı (non-zero)** elemanları sayarak toplam **mutasyon miktarını** bulur. Hastalık veya anomali risk yüzdesi şu basit denklemle hesaplanarak arayüze yansıtılır:
$$Risk Yuzdesi = \left( \frac{\text{Tespit Edilen Mutasyon Sayısı}}{\text{Toplam Dizi Uzunluğu (L)}} \right) \times 100$$

### Özet
Bu matematiksel model sayesinde hastaya ait olan hassas genetik (DNA) verileri hiçbir zaman sunucuda açık halde bulunmaz; sunucu veriyi okuyamaz ama matematiksel eşlenik işlemleri yerine getirerek istemciye doğru sonucu sunar. **Microsoft SEAL'ın doğrudan kullanıldığı** Tam Homomorfik Şifreleme (FHE), kriptografik güvenli maskeleme (CSPRNG) ile birleşerek gizliliği kırılması neredeyse imkansız hale getirir. Şifrelemenin temeli olan RLWE (Ring Learning With Errors) problemi, lattice-based kriptografiye dayanır ve post-quantum güvenlik özelliklerine sahiptir.

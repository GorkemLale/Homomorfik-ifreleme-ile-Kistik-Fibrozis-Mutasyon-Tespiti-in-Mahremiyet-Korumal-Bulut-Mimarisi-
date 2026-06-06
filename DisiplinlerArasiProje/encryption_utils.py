"""
Microsoft SEAL Doğrudan C++ Bağlamaları Modülü
===============================================
Bu modül, şifreleme işlemlerini tamamen saf C++ ile yazılmış olan 
kendi özel 'seal_cpp' kütüphanemize devreder. 
Python tarafı yalnızca C++ motorunu çağıran çok ince bir sarmalayıcıdır.
"""

import seal_cpp

class SEALEngine:
    """
    İstemci Tarafı Microsoft SEAL BFV Şifreleme Motoru (Saf C++ Wrapper).
    
    Gizli anahtar (Secret Key) C++ hafızasında kalır ve ağ üzerinden 
    asla gönderilmez.
    """

    def __init__(self):
        # Arka planda saf C++ motorunu başlat (Context, KeyGen vs. C++ içinde yapılır)
        self._engine = seal_cpp.SEALEngineCpp()
        self.slot_count = self._engine.get_slot_count()

    def encrypt_vector(self, int_vector):
        """Bir tamsayı vektörünü C++ motoru ile şifreler."""
        return self._engine.encrypt_vector(int_vector)

    def decrypt_vector(self, cipher_bytes):
        """Şifreli vektörün şifresini C++ motoru ile çözer."""
        return self._engine.decrypt_vector(cipher_bytes)

    def get_public_context_bytes(self):
        """
        Sunucuya gönderilecek genel bağlam verilerini döndürür.
        Gizli anahtar YER ALMAZ.
        """
        return self._engine.get_public_context_bytes()


class SEALEvaluator:
    """
    Sunucu Tarafı Microsoft SEAL Hesaplama Motoru (Saf C++ Wrapper).
    
    YALNIZCA açık anahtar ve parametrelerle çalışır. Gizli anahtara erişimi YOKTUR.
    """

    def __init__(self, parms_bytes):
        # Arka planda saf C++ hesaplama motorunu başlat
        self._evaluator = seal_cpp.SEALEvaluatorCpp(parms_bytes)

    def compute_difference(self, cipher1_bytes, cipher2_bytes):
        """
        İki şifreli vektör arasındaki farkı C++ motoru ile şifreli alanda hesaplar.
        """
        return self._evaluator.compute_difference(cipher1_bytes, cipher2_bytes)

"""
İstemci Arka Ucu (Client Backend)
=================================
Bu modül, kullanıcı arayüzünden gelen DNA verilerini alır,
Microsoft SEAL ile şifreler, sunucuya gönderir ve sonucu çözer.

Gizli anahtar bu sunucuda kalır, asla ağ üzerinden gönderilmez.
"""

import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

from data import HEALTHY_CFTR, MUTATED_CFTR
from dna_utils import dna_to_numbers, pad_sequences, generate_random_mask
from encryption_utils import SEALEngine

app = Flask(__name__)
CORS(app)

SERVER_URL = "http://localhost:5000/process"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        req_data = request.json or {}
        # Kullanıcı arayüzden özel bir dizi gönderdiyse onu al, yoksa varsayılanı kullan
        healthy_dna = req_data.get('healthy_dna', HEALTHY_CFTR)
        mutated_dna = req_data.get('mutated_dna', MUTATED_CFTR)

        # 1. DNA Dizilerini sayılara çevir ve boyutları eşitle
        healthy_nums = dna_to_numbers(healthy_dna)
        mutated_nums = dna_to_numbers(mutated_dna)
        healthy_nums, mutated_nums = pad_sequences(healthy_nums, mutated_nums)
        vector_length = len(healthy_nums)

        # 2. Kriptografik güvenli R Vektörü ile maskeleme
        R = generate_random_mask(vector_length)
        masked_healthy = [h * r for h, r in zip(healthy_nums, R)]
        masked_mutated = [m * r for m, r in zip(mutated_nums, R)]

        # 3. Microsoft SEAL BFV Şifreleme Motoru Oluşturma
        engine = SEALEngine()

        # 4. Verileri Şifreleme (serialize edilmiş bytes döner)
        enc_healthy_bytes = engine.encrypt_vector(masked_healthy)
        enc_mutated_bytes = engine.encrypt_vector(masked_mutated)

        # 5. Sunucuya Göndermek İçin Hazırlık
        # Sadece şifreleme parametrelerini gönderiyoruz (Secret Key GÖNDERİLMEZ!)
        public_ctx = engine.get_public_context_bytes()

        payload = {
            "parms": base64.b64encode(public_ctx['parms']).decode('utf-8'),
            "enc_healthy": base64.b64encode(enc_healthy_bytes).decode('utf-8'),
            "enc_mutated": base64.b64encode(enc_mutated_bytes).decode('utf-8')
        }

        # 6. Sunucuya (Hastane) İsteği Gönder
        response = requests.post(SERVER_URL, json=payload)
        
        if response.status_code != 200:
            return jsonify({"error": f"Sunucu hatası: {response.text}"}), 500
            
        result_b64 = response.json().get('result')
        if not result_b64:
            return jsonify({"error": "Sunucudan sonuç alınamadı"}), 500

        # 7. Sonucu Al, Şifreyi Çöz (Secret Key ile - sadece istemcide!)
        diff_bytes = base64.b64decode(result_b64)
        diff_result = engine.decrypt_vector(diff_bytes)

        # 8. Risk Analizi
        differences = 0
        for i in range(vector_length):
            if diff_result[i] != 0:
                differences += 1
                
        risk_percentage = (differences / vector_length) * 100

        return jsonify({
            "vector_length": vector_length,
            "differences": differences,
            "risk_percentage": round(risk_percentage, 2),
            "status": "MUTASYON TESPIT EDILDI" if differences > 0 else "SAGLIKLI",
            "message": "Microsoft SEAL FHE İşlemi Başarıyla Tamamlandı"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--- İstemci Arka Ucu (Client Backend) Başlatılıyor ---")
    print("    Şifreleme: Microsoft SEAL (Doğrudan) - BFV Şeması")
    app.run(port=5001, debug=True)

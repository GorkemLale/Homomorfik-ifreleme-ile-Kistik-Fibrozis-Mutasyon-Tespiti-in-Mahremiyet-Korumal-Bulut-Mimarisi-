"""
Hastane Sunucusu (FHE Server)
=============================
Bu modül, hastane/bulut sunucusunu simüle eder.
İstemciden gelen şifreli DNA verilerini alır ve şifreli alanda
homomorfik hesaplama yapar.

ÖNEMLİ: Bu sunucu Secret Key'e sahip DEĞİLDİR.
Verilerin şifresini çözemez, genetik dizilimleri asla göremez.
Sadece şifreli veriler üzerinde matematiksel işlem yapabilir.
"""

import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from encryption_utils import SEALEvaluator

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        
        # 1. Base64'ten verileri al
        parms_b64 = data.get('parms')
        healthy_b64 = data.get('enc_healthy')
        mutated_b64 = data.get('enc_mutated')
        
        if not parms_b64 or not healthy_b64 or not mutated_b64:
            return jsonify({"error": "Missing data"}), 400

        # 2. Byte'a çevir
        parms_bytes = base64.b64decode(parms_b64)
        healthy_bytes = base64.b64decode(healthy_b64)
        mutated_bytes = base64.b64decode(mutated_b64)
        
        # 3. Microsoft SEAL Evaluator oluştur (Secret Key OLMADAN!)
        evaluator = SEALEvaluator(parms_bytes)
        
        # 4. Sunucu tarafında Şifreli Hesaplama (Mutated - Healthy)
        #    Homomorfik özellik: E(M) - E(H) = E(M - H)
        #    Sunucu M ve H değerlerini BİLMEZ!
        diff_bytes = evaluator.compute_difference(mutated_bytes, healthy_bytes)
        
        # 5. Sonucu base64 edip geri dön
        diff_b64 = base64.b64encode(diff_bytes).decode('utf-8')
        
        return jsonify({"result": diff_b64})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--- Hastane Sunucusu (FHE Server) Başlatılıyor ---")
    print("    Hesaplama: Microsoft SEAL (Doğrudan) - Homomorfik Evaluator")
    print("    NOT: Bu sunucu Secret Key'e sahip DEĞİLDİR!")
    app.run(port=5000, debug=True)

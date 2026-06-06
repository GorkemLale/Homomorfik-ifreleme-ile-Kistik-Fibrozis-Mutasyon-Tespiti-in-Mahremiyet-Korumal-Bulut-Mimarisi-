import { useState } from 'react';
import './App.css';

function App() {
  const [healthyDna, setHealthyDna] = useState('TGTTCTCAGTTTTCCTGGATTATGCCTGGCACCATTAAAGAAAATATCATCTTTGGTGTTTCCTATGATG');
  const [mutatedDna, setMutatedDna] = useState('TGTTCTCAGTTTTCCTGGATTATGCCTGGCACCATTAAAGAAAATATCATTGGTGTTTCCTATGATG');
  
  const [status, setStatus] = useState('idle'); // idle, encrypting, sending, calculating, decrypting, done, error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleAnalyze = async () => {
    setStatus('encrypting');
    setResult(null);
    setErrorMsg('');

    try {
      // Small simulated delay for UI steps
      await new Promise(r => setTimeout(r, 600));
      setStatus('sending');
      
      await new Promise(r => setTimeout(r, 600));
      setStatus('calculating');

      // The actual request to the Local Client Backend
      const response = await fetch('http://localhost:5001/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          healthy_dna: healthyDna,
          mutated_dna: mutatedDna
        })
      });

      setStatus('decrypting');
      await new Promise(r => setTimeout(r, 600));

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Bilinmeyen bir hata oluştu');
      }

      setResult(data);
      setStatus('done');
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      
      {/* Header */}
      <div className="w-full max-w-4xl text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">
          FHE DNA Mutasyon Analizi
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Tam Homomorfik Şifreleme (Microsoft SEAL) kullanılarak genetik verileriniz hastane sunucusuna
          <span className="text-emerald-400 font-semibold"> şifreli </span> olarak gönderilir.
          Sunucu verinizi göremez!
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: Input Form */}
        <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700 shadow-xl">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <span className="bg-blue-500/20 text-blue-400 p-2 rounded-lg mr-3">🧬</span>
            Genetik Veri Girişi
          </h2>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Sağlıklı Referans DNA (Örn: CFTR Geni)</label>
              <textarea 
                value={healthyDna}
                onChange={(e) => setHealthyDna(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition h-28 font-mono text-sm resize-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">İncelenecek Hasta DNA'sı</label>
              <textarea 
                value={mutatedDna}
                onChange={(e) => setMutatedDna(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition h-28 font-mono text-sm resize-none"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={status !== 'idle' && status !== 'done' && status !== 'error'}
              className="w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold py-4 px-6 rounded-xl transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/25"
            >
              Şifrele ve Güvenli Analizi Başlat
            </button>
          </div>
        </div>

        {/* Right Column: Status & Results */}
        <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700 shadow-xl flex flex-col">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <span className="bg-emerald-500/20 text-emerald-400 p-2 rounded-lg mr-3">🔒</span>
            Güvenlik İşlemleri & Sonuç
          </h2>
          
          {/* Status Steps */}
          <div className="space-y-4 mb-8 flex-grow">
            <StepItem currentStatus={status} stepKey="encrypting" icon="🔑" text="1. İstemcide Şifreleme (Microsoft SEAL BFV)" />
            <StepItem currentStatus={status} stepKey="sending" icon="🚀" text="2. Hastane Sunucusuna Gönderim" />
            <StepItem currentStatus={status} stepKey="calculating" icon="⚙️" text="3. Şifreli Alan Üzerinde Hesaplama (Sunucu)" />
            <StepItem currentStatus={status} stepKey="decrypting" icon="🔓" text="4. Şifreli Sonucun Çözülmesi (İstemci)" />
          </div>

          {/* Result Box */}
          {status === 'done' && result && (
            <div className={`mt-auto p-6 rounded-xl border ${result.differences > 0 ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'} animate-fade-in-up`}>
              <h3 className={`text-xl font-bold mb-2 ${result.differences > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                {result.status}
              </h3>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="bg-slate-900 rounded-lg p-3 border border-slate-700 text-center">
                  <p className="text-slate-400 text-xs mb-1">Risk Yüzdesi</p>
                  <p className="text-2xl font-bold text-white">%{result.risk_percentage}</p>
                </div>
                <div className="bg-slate-900 rounded-lg p-3 border border-slate-700 text-center">
                  <p className="text-slate-400 text-xs mb-1">Tespit Edilen Fark</p>
                  <p className="text-2xl font-bold text-white">{result.differences} baz</p>
                </div>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="mt-auto p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200">
              <p className="font-bold">Hata Oluştu:</p>
              <p className="text-sm">{errorMsg}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Helper component for steps
function StepItem({ currentStatus, stepKey, icon, text }) {
  const stepsOrder = ['idle', 'encrypting', 'sending', 'calculating', 'decrypting', 'done', 'error'];
  
  const currentIndex = stepsOrder.indexOf(currentStatus);
  const stepIndex = stepsOrder.indexOf(stepKey);
  
  let state = 'pending'; // pending, active, completed
  if (currentStatus === 'error' && stepIndex >= currentIndex) {
    state = 'pending';
  } else if (currentStatus === 'done' || stepIndex < currentIndex) {
    state = 'completed';
  } else if (stepIndex === currentIndex) {
    state = 'active';
  }

  return (
    <div className={`flex items-center p-3 rounded-lg border transition-all duration-300 ${
      state === 'completed' ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300' :
      state === 'active' ? 'bg-blue-500/20 border-blue-500/30 text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.5)]' :
      'bg-slate-800 border-slate-700 text-slate-500'
    }`}>
      <span className="text-xl mr-3">{icon}</span>
      <span className="font-medium">{text}</span>
      {state === 'active' && (
        <span className="ml-auto flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
        </span>
      )}
      {state === 'completed' && (
        <span className="ml-auto text-emerald-400 font-bold">✓</span>
      )}
    </div>
  );
}

export default App;

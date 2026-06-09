import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const [pasienList, setPasienList] = useState([]);
  const [namaPasien, setNamaPasien] = useState('');
  const [fileDicom, setFileDicom] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Ambil data antrean dari Flask API
  const fetchPasien = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/pasien');
      if (response.data.status === 'success') {
        setPasienList(response.data.data);
      }
    } catch (err) {
      console.error('Gagal mengambil data pasien:', err);
    }
  };

  useEffect(() => {
    fetchPasien();
  }, []);

  // Handle proses upload dan analisis AI
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!fileDicom || !namaPasien) return;

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('nama_pasien', namaPasien);
    formData.append('file_dicom', fileDicom);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.status === 'success') {
        // Jika sukses, langsung arahkan ke halaman detail menggunakan ID dari backend
        navigate(`/detail/${response.data.id_pasien}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Gagal memproses rekam medis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-extrabold mb-2 text-blue-900">Sistem Pendukung Keputusan Keputusan Klinis (SPKK)</h1>
      <p class="text-gray-600 mb-8">Deteksi Trauma Abdomen Multi-Organ Berbasis Random Forest</p>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      {/* Form Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
        <h2 className="text-lg font-bold mb-4">Unggah Citra CT Scan Baru</h2>
        <form onSubmit={handleUpload} className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <label className="block text-sm font-semibold text-gray-700 mb-1">Nama Pasien / ID</label>
            <input 
              type="text" 
              value={namaPasien}
              onChange={(e) => setNamaPasien(e.target.value)}
              placeholder="Masukkan nama..." 
              required 
              className="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div className="flex-1 w-full">
            <label className="block text-sm font-semibold text-gray-700 mb-1">File CT Scan (.dcm)</label>
            <input 
              type="file" 
              accept=".dcm"
              onChange={(e) => setFileDicom(e.target.files[0])}
              required 
              className="w-full border border-gray-300 p-2 rounded-lg bg-gray-50 text-sm"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 transition-colors text-white font-bold py-2.5 px-8 rounded-lg w-full md:w-auto"
          >
            {loading ? 'Menganalisis...' : 'Analisis AI'}
          </button>
        </form>
      </div>

      {/* Table Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-800 text-white">
            <tr>
              <th className="p-4 font-semibold">ID</th>
              <th className="p-4 font-semibold">Nama Pasien</th>
              <th className="p-4 font-semibold">Status Klinis (Triase)</th>
              <th className="p-4 font-semibold">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {pasienList.map((p) => (
              <tr key={p.id} className={`transition-colors hover:bg-gray-50 ${p.status_kritis === 1 ? 'bg-red-50/50' : ''}`}>
                <td className="p-4 text-gray-500">#{p.id}</td>
                <td className="p-4 font-bold text-gray-800">{p.nama_pasien}</td>
                <td className="p-4">
                  {p.status_kritis === 1 ? (
                    <span className="inline-flex items-center gap-1.5 bg-red-100 text-red-800 py-1 px-3 rounded-full text-sm font-bold border border-red-200">
                      <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
                      Indikasi Cedera ({p.probabilitas_max}%)
                    </span>
                  ) : (
                    <span className="bg-green-100 text-green-800 py-1 px-3 rounded-full text-sm font-bold border border-green-200">Normal</span>
                  )}
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => navigate(`/detail/${p.id}`)}
                    className="text-blue-600 font-semibold hover:text-blue-800 hover:underline"
                  >
                    Lihat Detail &rarr;
                  </button>
                </td>
              </tr>
            ))}
            {pasienList.length === 0 && (
              <tr>
                <td colSpan="4" className="p-8 text-center text-gray-500">Belum ada data riwayat pasien.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
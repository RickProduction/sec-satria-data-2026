import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const [pasienList, setPasienList] = useState([]);
  const [namaPasien, setNamaPasien] = useState('');
  const [fileDicom, setFileDicom] = useState(null);
  const [fileName, setFileName] = useState('');
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
    if (!fileDicom || !namaPasien) {
      setError('Silakan isi nama pasien dan pilih file');
      return;
    }

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('nama_pasien', namaPasien);
    formData.append('file_dicom', fileDicom);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 // 60 detik timeout
      });
      
      if (response.data.status === 'success') {
        navigate(`/detail/${response.data.id_pasien}`);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.message || 'Gagal memproses rekam medis.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileDicom(file);
      setFileName(file.name);
      
      // Validasi ekstensi
      const validExtensions = ['.dcm', '.jpg', '.jpeg', '.png'];
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      if (!validExtensions.includes(ext)) {
        setError('Format file tidak didukung. Gunakan .dcm, .jpg, .jpeg, atau .png');
        setFileDicom(null);
        setFileName('');
      } else {
        setError('');
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-extrabold mb-2 text-blue-900">Sistem Pendukung Keputusan Keputusan Klinis (SPKK)</h1>
      <p className="text-gray-600 mb-8">Deteksi Trauma Abdomen Multi-Organ Berbasis Random Forest</p>

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
            <label className="block text-sm font-semibold text-gray-700 mb-1">File CT Scan (.dcm / .jpg / .png)</label>
            <div className="relative">
              <input 
                type="file" 
                accept=".dcm,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                required 
                className="w-full border border-gray-300 p-2 rounded-lg bg-gray-50 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {fileName && (
                <p className="text-xs text-gray-500 mt-1">
                  📎 {fileName}
                </p>
              )}
            </div>
          </div>
          <button 
            type="submit" 
            disabled={loading || !fileDicom}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 transition-colors text-white font-bold py-2.5 px-8 rounded-lg w-full md:w-auto"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Menganalisis...
              </span>
            ) : 'Analisis AI'}
          </button>
        </form>
        <p className="text-xs text-gray-400 mt-2">* Mendukung format DICOM (.dcm) dan gambar (.jpg, .jpeg, .png)</p>
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
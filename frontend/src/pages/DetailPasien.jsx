import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function Detail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [shapcamLoading, setShapcamLoading] = useState(false);
  const [shapcamData, setShapcamData] = useState(null);
  const [shapcamError, setShapcamError] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const fetchDetail = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/pasien/${id}`);
      if (response.data.status === 'success') {
        setData(response.data.data);
        fetchShapcam();
      } else {
        setError('Data tidak ditemukan');
      }
    } catch (err) {
      setError('Gagal mengambil data detail');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchShapcam = async () => {
    setShapcamLoading(true);
    setShapcamError(null);
    try {
      const response = await axios.get(`http://localhost:5000/api/shapcam/pasien/${id}`, {
        timeout: 120000
      });
      console.log('SHAP-CAM Response:', response.data);
      
      if (response.data.status === 'success') {
        setShapcamData(response.data.data);
      } else {
        setShapcamError(response.data.message || 'Gagal memuat SHAP-CAM');
      }
    } catch (err) {
      console.error('SHAP-CAM error:', err);
      setShapcamError(err.response?.data?.message || err.message || 'Gagal memuat SHAP-CAM');
    } finally {
      setShapcamLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat data pasien...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Data tidak ditemukan'}
        </div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg"
        >
          Kembali ke Dashboard
        </button>
      </div>
    );
  }

  const { nama_pasien, file_dicom, status_kritis, probabilitas_max, organ } = data;
  
  const organList = [
    { key: 'hati', label: 'Hati (Liver)' },
    { key: 'ginjal', label: 'Ginjal (Kidney)' },
    { key: 'limpa', label: 'Limpa (Spleen)' },
    { key: 'usus', label: 'Usus (Bowel)' }
  ];

  const hasCedera = organList.some(o => organ[o.key]?.status === 'Cedera');

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-extrabold text-blue-900">📋 Laporan Klinis Medis</h1>
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:text-blue-800 font-semibold"
        >
          ← Kembali ke Dashboard
        </button>
      </div>

      {/* Info Pasien */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-6">
        <p className="text-gray-700">
          <span className="font-bold">Pasien:</span> {nama_pasien} 
          <span className="ml-4 font-bold">Sumber File:</span> {file_dicom}
        </p>
      </div>

      {/* Status Kritis */}
      {status_kritis === 1 ? (
        <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded-lg mb-6">
          <h2 className="text-red-800 font-bold text-lg">🚨 PERHATIAN MEDIS DIPERLUKAN (KRITIS)</h2>
          <p className="text-red-700 mt-1">
            Sistem mendeteksi probabilitas tinggi adanya trauma internal parah pada organ. 
            Prioritaskan tindakan keseluruhan.
          </p>
        </div>
      ) : (
        <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded-lg mb-6">
          <h2 className="text-green-800 font-bold text-lg">✅ STATUS STABIL</h2>
          <p className="text-green-700 mt-1">
            Sistem tidak mendeteksi indikasi trauma internal yang signifikan.
          </p>
        </div>
      )}

      {/* Status Organ */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h2 className="font-bold text-lg">📊 Status Segmentasi Organ</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {organList.map(({ key, label }) => {
            const org = organ[key];
            if (!org) return null;
            const isCedera = org.status === 'Cedera';
            const conf = org.conf || 0;
            
            return (
              <div key={key} className="px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-gray-700 min-w-30">{label}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    isCedera 
                      ? 'bg-red-100 text-red-800 border border-red-200' 
                      : 'bg-green-100 text-green-800 border border-green-200'
                  }`}>
                    {org.status}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-2 md:mt-0">
                  <span className="text-sm text-gray-500">Tingkat Kerusakan:</span>
                  <div className="w-32 bg-gray-200 rounded-full h-2.5">
                    <div 
                      className={`h-2.5 rounded-full transition-all duration-500 ${
                        isCedera ? 'bg-red-600' : 'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(conf, 100)}%` }}
                    ></div>
                  </div>
                  <span className={`text-sm font-bold ${isCedera ? 'text-red-600' : 'text-green-600'}`}>
                    {typeof conf === 'number' ? conf.toFixed(2) : conf}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ===== SHAP-CAM SECTION - 2 GAMBAR ===== */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h2 className="font-bold text-lg">🧠 Visualisasi SHAP-CAM</h2>
        </div>
        
        <div className="p-6">
          {/* Loading */}
          {shapcamLoading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-600">Generating SHAP-CAM visualization...</p>
              <p className="text-sm text-gray-400 mt-1">Proses ini membutuhkan waktu 10-30 detik</p>
            </div>
          )}

          {/* Error */}
          {shapcamError && !shapcamLoading && (
            <div className="bg-yellow-50 border border-yellow-400 text-yellow-800 px-4 py-3 rounded-lg">
              <p className="font-semibold">⚠️ SHAP-CAM tidak tersedia</p>
              <p className="text-sm">{shapcamError}</p>
              <button
                onClick={fetchShapcam}
                className="mt-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-1 px-4 rounded-lg text-sm transition-colors"
              >
                Coba Lagi
              </button>
            </div>
          )}

          {/* SHAP-CAM Data - 2 GAMBAR: Original + Heatmap */}
          {shapcamData && !shapcamLoading && (
            <div>
              {/* 2 Gambar: Original + SHAP-CAM Heatmap (tanpa overlay) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Original */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-3 py-2 text-center border-b border-gray-200">
                    <span className="font-semibold text-sm">Original CT-Scan</span>
                  </div>
                  {shapcamData.original ? (
                    <img 
                      src={`data:image/png;base64,${shapcamData.original}`}
                      alt="Original CT-Scan"
                      className="w-full h-64 object-contain bg-gray-900"
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect width="200" height="200" fill="%23333"/%3E%3Ctext x="50" y="100" fill="%23fff" font-size="16"%3ENo Image%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  ) : (
                    <div className="w-full h-64 flex items-center justify-center bg-gray-900 text-white">
                      No Image
                    </div>
                  )}
                </div>

                {/* SHAP-CAM Heatmap - dengan kontras lebih tinggi */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-3 py-2 text-center border-b border-gray-200">
                    <span className="font-semibold text-sm">SHAP-CAM Heatmap</span>
                  </div>
                  {shapcamData.heatmap ? (
                    <img 
                      src={`data:image/png;base64,${shapcamData.heatmap}`}
                      alt="SHAP-CAM Heatmap"
                      className="w-full h-64 object-contain bg-gray-900"
                      style={{ filter: 'contrast(1.5) brightness(1.2)' }}
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect width="200" height="200" fill="%23333"/%3E%3Ctext x="50" y="100" fill="%23fff" font-size="16"%3ENo Image%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  ) : (
                    <div className="w-full h-64 flex items-center justify-center bg-gray-900 text-white">
                      No Image
                    </div>
                  )}
                </div>
              </div>

              {/* Keterangan Area Fokus */}
              <div className="mt-4 text-center text-sm text-gray-500">
                <p>🔴 <span className="font-semibold">Area merah</span> menunjukkan region yang paling berpengaruh dalam keputusan model</p>
              </div>
            </div>
          )}

          {/* Initial State */}
          {!shapcamLoading && !shapcamData && !shapcamError && (
            <div className="text-center py-8 text-gray-500">
              <p className="text-4xl mb-4">🔄</p>
              <p>Memuat SHAP-CAM...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Detail;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function DetailPasien() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pasien, setPasien] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/pasien/${id}`);
        if (response.data.status === 'success') {
          setPasien(response.data.data);
        }
      } catch (err) {
        console.error('Gagal memuat detail pasien:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-xl font-bold text-gray-600 animate-pulse">Memuat Hasil Analisis Organ...</div>
      </div>
    );
  }

  if (!pasien) {
    return (
      <div className="max-w-6xl mx-auto p-8 text-center">
        <p className="text-red-500 font-bold">Data pasien tidak ditemukan.</p>
        <button onClick={() => navigate('/')} className="mt-4 bg-blue-600 text-white p-2 rounded">Kembali</button>
      </div>
    );
  }

  // Komponen Kartu Organ Internal (Reusable Component)
  const OrganCard = ({ namaOrgan, status, conf }) => {
    const isCedera = status === 'Cedera';
    return (
      <div className="p-6 rounded-xl shadow-sm bg-white border border-gray-200 relative overflow-hidden">
        <div className={`absolute top-0 left-0 w-full h-1 ${isCedera ? 'bg-red-500' : 'bg-green-500'}`}></div>
        <h3 className="text-xl font-extrabold text-gray-800 mb-4">{namaOrgan}</h3>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">Prediksi Sistem:</span>
          <span className={`font-black px-2 py-1 rounded text-sm ${isCedera ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
            {status}
          </span>
        </div>
        <div className="mt-4">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Tingkat Keyakinan</span>
            <span className="font-mono font-bold text-gray-700">{conf}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2.5 shadow-inner">
            <div 
              className={`h-2.5 rounded-full transition-all duration-1000 ${isCedera ? 'bg-red-500' : 'bg-green-500'}`} 
              style={{ width: `${conf}%` }}
            ></div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-800">Laporan Klinis Medis</h1>
          <p className="text-gray-500 mt-1">
            Pasien: <span className="font-bold text-gray-800">{pasien.nama_pasien}</span> | Sumber File: <span className="font-mono text-xs">{pasien.file_dicom}</span>
          </p>
        </div>
        <button 
          onClick={() => navigate('/')} 
          className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-semibold py-2 px-5 rounded-lg shadow-sm transition-colors"
        >
          &larr; Kembali ke Antrean
        </button>
      </div>

      {/* Banner Triase */}
      {pasien.status_kritis === 1 ? (
        <div className="bg-linear-to-r from-red-600 to-red-500 text-white p-5 rounded-xl mb-8 shadow-lg flex items-center gap-4">
          <div className="text-4xl">⚠️</div>
          <div>
            <h2 class="font-bold text-xl">PERHATIAN MEDIS DIPERLUKAN (KRITIS)</h2>
            <p className="text-red-50 text-sm mt-0.5">Sistem mendeteksi probabilitas tinggi adanya trauma internal parah pada organ. Prioritaskan tindakan kedaruratan.</p>
          </div>
        </div>
      ) : (
        <div className="bg-green-600 text-white p-5 rounded-xl mb-8 shadow-md flex items-center gap-4">
          <div className="text-4xl">✅</div>
          <div>
            <h2 className="font-bold text-xl">STATUS AMAN (NORMAL)</h2>
            <p className="text-green-50 text-sm mt-0.5 font-medium">Berdasarkan ekstraksi fitur statistik citra, organ dalam kondisi batas normal.</p>
          </div>
        </div>
      )}

      {/* Grid Status Organ */}
      <h3 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Status Segmentasi Organ</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <OrganCard namaOrgan="Hati (Liver)" status={pasien.organ.hati.status} conf={pasien.organ.hati.conf} />
        <OrganCard namaOrgan="Ginjal (Kidney)" status={pasien.organ.ginjal.status} conf={pasien.organ.ginjal.conf} />
        <OrganCard namaOrgan="Limpa (Spleen)" status={pasien.organ.limpa.status} conf={pasien.organ.limpa.conf} />
        <OrganCard namaOrgan="Usus (Bowel)" status={pasien.organ.usus.status} conf={pasien.organ.usus.conf} />
      </div>
    </div>
  );
}

export default DetailPasien;
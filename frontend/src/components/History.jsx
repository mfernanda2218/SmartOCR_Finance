import { useEffect, useState } from 'react';
import { History as HistoryIcon, Trash2, Eye, Calendar, FileText, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

export default function History({ refreshTrigger }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    loadHistory();
  }, [refreshTrigger]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await apiService.getHistory(0, 50);
      setRecords(data.records || []);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar histórico');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Tem certeza que deseja remover este registro?')) return;

    try {
      await apiService.deleteRecord(id);
      setRecords(records.filter(record => record.id !== id));
      if (selectedRecord?.id === id) {
        setSelectedRecord(null);
      }
    } catch (err) {
      setError('Erro ao remover registro');
      console.error(err);
    }
  };

  const handleView = async (id) => {
    try {
      const record = await apiService.getRecordById(id);
      setSelectedRecord(record);
    } catch (err) {
      setError('Erro ao carregar detalhes do registro');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <HistoryIcon className="w-6 h-6" />
          Histórico
        </h2>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <HistoryIcon className="w-6 h-6" />
          Histórico
        </h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <HistoryIcon className="w-6 h-6" />
        Histórico de Extrações
      </h2>

      {records.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <HistoryIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p>Nenhum registro encontrado</p>
        </div>
      ) : (
        <div className="space-y-3">
          {records.map((record) => (
            <div
              key={record.id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="font-medium">{record.filename || 'Sem nome'}</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      {new Date(record.created_at).toLocaleString('pt-BR')}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleView(record.id)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Ver detalhes"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(record.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Remover"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {record.document_type && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded capitalize">
                    {record.document_type}
                  </span>
                  {record.processing_status && (
                    <span className={`text-xs px-2 py-1 rounded capitalize ${
                      record.processing_status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : record.processing_status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {record.processing_status}
                    </span>
                  )}
                  {record.confidence_score && (
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      {(record.confidence_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal de Detalhes */}
      {selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">Detalhes do Registro</h3>
                <button
                  onClick={() => setSelectedRecord(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">ID:</span>
                    <p className="font-medium">{selectedRecord.id}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Arquivo:</span>
                    <p className="font-medium">{selectedRecord.filename || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Criado em:</span>
                    <p className="font-medium">
                      {new Date(selectedRecord.created_at).toLocaleString('pt-BR')}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Tipo:</span>
                    <p className="font-medium capitalize">{selectedRecord.document_type}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <p className="font-medium capitalize">{selectedRecord.processing_status}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Confiança:</span>
                    <p className="font-medium">
                      {selectedRecord.confidence_score 
                        ? `${(selectedRecord.confidence_score * 100).toFixed(1)}%` 
                        : 'N/A'}
                    </p>
                  </div>
                </div>

                {selectedRecord.cpfs && selectedRecord.cpfs.length > 0 && (
                  <div>
                    <span className="text-gray-600 text-sm">CPFs:</span>
                    <div className="mt-1 space-y-1">
                      {selectedRecord.cpfs.map((cpf, index) => (
                        <div key={index} className="bg-gray-50 p-2 rounded font-mono text-sm">
                          {cpf}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedRecord.values && selectedRecord.values.length > 0 && (
                  <div>
                    <span className="text-gray-600 text-sm">Valores:</span>
                    <div className="mt-1 space-y-1">
                      {selectedRecord.values.map((value, index) => (
                        <div key={index} className="bg-gray-50 p-2 rounded font-mono text-sm">
                          R$ {value}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedRecord.raw_text && (
                  <div>
                    <span className="text-gray-600 text-sm">Texto Bruto:</span>
                    <div className="mt-1 bg-gray-50 p-3 rounded max-h-48 overflow-y-auto">
                      <pre className="text-xs whitespace-pre-wrap font-mono">
                        {selectedRecord.raw_text}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
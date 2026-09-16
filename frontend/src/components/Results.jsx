import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { FileText, Calendar, DollarSign, CreditCard, Hash, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

export default function Results() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const record = await apiService.getRecordById(id);
        setData(record);
        setError(null);
      } catch (err) {
        setError('Erro ao carregar resultados');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadData();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <FileText className="w-6 h-6" />
          Resultados da Extração
        </h2>
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <FileText className="w-6 h-6" />
          Resultados da Extração
        </h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const {
    cpfs = [],
    cnpjs = [],
    dates = [],
    values = [],
    boleto_lines = [],
    raw_text = '',
    document_type = '',
    processing_status = '',
    confidence_score = 0,
    processing_time_ms = 0,
    warnings = []
  } = data;

  const metadata = {
    document_type,
    processing_status,
    confidence_score,
    processing_time_ms,
    warnings
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <FileText className="w-6 h-6" />
        Resultados da Extração
      </h2>

      {metadata && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-3">Metadados</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Tipo:</span>
              <p className="font-medium capitalize">{metadata.document_type}</p>
            </div>
            <div>
              <span className="text-gray-600">Status:</span>
              <p className="font-medium capitalize">{metadata.processing_status}</p>
            </div>
            <div>
              <span className="text-gray-600">Confiança:</span>
              <p className="font-medium">{(metadata.confidence_score * 100).toFixed(1)}%</p>
            </div>
            <div>
              <span className="text-gray-600">Tempo:</span>
              <p className="font-medium">{metadata.processing_time_ms}ms</p>
            </div>
          </div>
          
          {metadata.warnings && metadata.warnings.length > 0 && (
            <div className="mt-3">
              <span className="text-gray-600 text-sm">Warnings:</span>
              <ul className="list-disc list-inside text-sm text-yellow-700 mt-1">
                {metadata.warnings.map((warning, index) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CPFs */}
        {cpfs.length > 0 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <CreditCard className="w-4 h-4" />
              CPFs ({cpfs.length})
            </h3>
            <div className="space-y-2">
              {cpfs.map((cpf, index) => (
                <div key={index} className="bg-white p-2 rounded font-mono text-sm">
                  {cpf}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CNPJs */}
        {cnpjs.length > 0 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <Hash className="w-4 h-4" />
              CNPJs ({cnpjs.length})
            </h3>
            <div className="space-y-2">
              {cnpjs.map((cnpj, index) => (
                <div key={index} className="bg-white p-2 rounded font-mono text-sm">
                  {cnpj}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Datas */}
        {dates.length > 0 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <Calendar className="w-4 h-4" />
              Datas ({dates.length})
            </h3>
            <div className="space-y-2">
              {dates.map((date, index) => (
                <div key={index} className="bg-white p-2 rounded text-sm">
                  {date}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Valores */}
        {values.length > 0 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <DollarSign className="w-4 h-4" />
              Valores ({values.length})
            </h3>
            <div className="space-y-2">
              {values.map((value, index) => (
                <div key={index} className="bg-white p-2 rounded text-sm font-mono">
                  R$ {value}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Linhas Digitáveis */}
        {boleto_lines.length > 0 && (
          <div className="p-4 bg-gray-50 rounded-lg md:col-span-2">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <Hash className="w-4 h-4" />
              Linhas Digitáveis ({boleto_lines.length})
            </h3>
            <div className="space-y-2">
              {boleto_lines.map((line, index) => (
                <div key={index} className="bg-white p-3 rounded font-mono text-sm break-all">
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Texto Bruto */}
      {raw_text && (
        <div className="mt-6">
          <h3 className="font-semibold mb-3">Texto Bruto</h3>
          <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
            <pre className="text-sm whitespace-pre-wrap font-mono">
              {raw_text}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
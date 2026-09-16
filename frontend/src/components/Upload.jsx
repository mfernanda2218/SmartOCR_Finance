import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import { apiService } from '../services/api';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = useCallback((e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
      
      // Criar preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  }, []);

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const data = await apiService.uploadImage(file);
      setResult(data);
      // Navegar para a página de resultados após o upload bem-sucedido
      if (data.id) {
        navigate(`/results/${data.id}`);
      }
    } catch (err) {
      setError(err.message || 'Erro ao processar imagem');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setError(null);
    setResult(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <UploadIcon className="w-6 h-6" />
        Upload de Documento
      </h2>

      {!file ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors">
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center gap-4"
          >
            <UploadIcon className="w-16 h-16 text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700">
                Clique ou arraste uma imagem aqui
              </p>
              <p className="text-sm text-gray-500 mt-1">
                PNG, JPG até 10MB
              </p>
            </div>
          </label>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-blue-500" />
              <span className="font-medium">{file.name}</span>
              <span className="text-sm text-gray-500">
                ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
            <button
              onClick={handleReset}
              className="text-gray-500 hover:text-red-500 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {preview && (
            <div className="relative rounded-lg overflow-hidden border">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-64 object-contain bg-gray-100"
              />
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processando...
              </>
            ) : (
              <>
                <UploadIcon className="w-5 h-5" />
                Processar Documento
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-800">Erro no processamento</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <p className="font-medium text-green-800">Processamento concluído!</p>
              </div>
              
              {result.metadata && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tipo:</span>
                    <span className="font-medium capitalize">{result.metadata.document_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confiança:</span>
                    <span className="font-medium">{(result.metadata.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tempo:</span>
                    <span className="font-medium">{result.metadata.processing_time_ms}ms</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
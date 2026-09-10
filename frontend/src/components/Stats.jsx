import { useEffect, useState } from 'react';
import { BarChart3, FileText, CreditCard, DollarSign, TrendingUp } from 'lucide-react';
import { apiService } from '../services/api';

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await apiService.getStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar estatísticas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Estatísticas
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
          <BarChart3 className="w-6 h-6" />
          Estatísticas
        </h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    {
      label: 'Total de Extrações',
      value: stats.total_extractions,
      icon: FileText,
      color: 'blue',
    },
    {
      label: 'Documentos com CPF',
      value: stats.documents_with_cpf,
      icon: CreditCard,
      color: 'green',
    },
    {
      label: 'Documentos com Valores',
      value: stats.documents_with_values,
      icon: DollarSign,
      color: 'purple',
    },
    {
      label: 'Campos por Documento',
      value: stats.average_fields_per_document.toFixed(2),
      icon: TrendingUp,
      color: 'orange',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  };

  const bgClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50',
    orange: 'bg-orange-50',
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BarChart3 className="w-6 h-6" />
        Estatísticas
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className={`${bgClasses[stat.color]} p-4 rounded-lg`}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-5 h-5 ${colorClasses[stat.color]}`} />
                <span className="text-sm text-gray-600">{stat.label}</span>
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold mb-3">Resumo</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Taxa de Sucesso:</span>
            <span className="font-medium">
              {stats.total_extractions > 0
                ? ((stats.successful_extractions / stats.total_extractions) * 100).toFixed(1)
                : 0}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Documentos com CNPJ:</span>
            <span className="font-medium">{stats.documents_with_cnpj}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
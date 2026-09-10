const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Serviço de comunicação com a API SmartOCR
 */
class APIService {
  /**
   * Faz upload de uma imagem para extração OCR
   */
  async uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Erro no upload: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
      throw error;
    }
  }

  /**
   * Busca histórico de extrações
   */
  async getHistory(skip = 0, limit = 20) {
    try {
      const response = await fetch(`${API_BASE_URL}/history?skip=${skip}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar histórico: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
      throw error;
    }
  }

  /**
   * Busca um registro específico por ID
   */
  async getRecordById(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/history/${id}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar registro: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar registro:', error);
      throw error;
    }
  }

  /**
   * Remove um registro do histórico
   */
  async deleteRecord(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/history/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao deletar registro: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao deletar registro:', error);
      throw error;
    }
  }

  /**
   * Busca estatísticas do sistema
   */
  async getStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar estatísticas: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
      throw error;
    }
  }

  /**
   * Health check da API
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`API não está saudável: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro no health check:', error);
      throw error;
    }
  }
}

export const apiService = new APIService();
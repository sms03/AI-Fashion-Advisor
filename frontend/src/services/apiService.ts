import axios from 'axios';

// Define the base URL for the API
const API_BASE_URL = 'http://localhost:8000';

// Create an axios instance with the base URL
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define the interface for the fashion advice response
export interface FashionAdviceResponse {
  text_advice: string;
  image_url: string | null;
}

// Add a request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', 
      error.response ? `${error.response.status} - ${error.response.statusText}` : 'Network Error');
    return Promise.reject(error);
  }
);

// Fashion API service
export const fashionService = {
  // Health check to see if the backend is running
  async healthCheck() {
    try {
      return await apiClient.get('/api/health');
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Upload image and get fashion advice
  async analyzeFashion(imageFile: File, scenario: string): Promise<FashionAdviceResponse> {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('scenario', scenario);

      const response = await apiClient.post<FashionAdviceResponse>('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Fashion analysis failed:', error);
      throw error;
    }
  }
};

export default apiClient;
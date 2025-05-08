import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { fashionService } from '../services/apiService';

// Define the interface locally to avoid import issues
interface FashionAdviceResponse {
  text_advice: string;
  image_url: string | null;
}

const FashionAdvisor: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scenario, setScenario] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<FashionAdviceResponse | null>(null);
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [toastMessage, setToastMessage] = useState<{title: string, message: string, type: 'success' | 'error' | 'info'} | null>(null);

  // Check backend status on component mount
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        await fashionService.healthCheck();
        setBackendStatus('online');
      } catch (error) {
        setBackendStatus('offline');
        setToastMessage({
          title: 'Backend server unavailable',
          message: 'The fashion advisor service is currently unavailable. Please ensure the backend server is running.',
          type: 'error'
        });
      }
    };

    checkBackendStatus();
  }, []);

  // Toast message display and auto-dismiss
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Set the selected file for upload
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    multiple: false
  });

  const analyzeFashion = async () => {
    if (!selectedFile) {
      setToastMessage({
        title: 'No image selected',
        message: 'Please upload an image first',
        type: 'error'
      });
      return;
    }

    if (!scenario.trim()) {
      setToastMessage({
        title: 'No scenario provided',
        message: 'Please describe the scenario or occasion',
        type: 'error'
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fashionService.analyzeFashion(selectedFile, scenario);
      setResult(response);
    } catch (error) {
      console.error('Error analyzing fashion:', error);
      setToastMessage({
        title: 'Error',
        message: 'Failed to analyze the image. Please try again.',
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedImage(null);
    setSelectedFile(null);
    setScenario('');
    setResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-8 animate-fade-in">
      {/* Toast notification */}
      {toastMessage && (
        <div className={`fixed top-4 right-4 p-4 rounded-lg shadow z-50 ${
          toastMessage.type === 'error' ? 'bg-red-500 text-white' :
          toastMessage.type === 'success' ? 'bg-green-500 text-white' :
          'bg-blue-500 text-white'
        }`}>
          <div className="flex justify-between">
            <h3 className="font-semibold">{toastMessage.title}</h3>
            <button onClick={() => setToastMessage(null)} className="text-white">×</button>
          </div>
          <p className="mt-1">{toastMessage.message}</p>
        </div>
      )}

      <div className="text-center relative mb-8">
        <h1 className="text-4xl font-serif font-bold mb-2">AI Fashion Advisor</h1>
        <p className="text-lg text-gray-600">
          Upload your outfit and get professional fashion advice
        </p>
        {/* Backend status indicator */}
        <div className="absolute top-0 right-0">
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
            backendStatus === 'online' ? 'bg-green-100 text-green-800' : 
            backendStatus === 'checking' ? 'bg-yellow-100 text-yellow-800' : 
            'bg-red-100 text-red-800'
          }`}>
            {backendStatus === 'online' ? 'Server Online' : 
             backendStatus === 'checking' ? 'Checking Server...' : 
             'Server Offline'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="space-y-4">
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer h-[300px] transition-all duration-200 ${
                isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50'
              } hover:border-blue-400 hover:bg-blue-50`}
            >
              <input {...getInputProps()} />
              {selectedImage ? (
                <img 
                  src={selectedImage} 
                  alt="Selected outfit" 
                  className="max-h-full max-w-full object-contain" 
                />
              ) : (
                <div className="text-center">
                  <p className="text-gray-500">
                    Drag and drop your outfit image here, or click to select a file
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Supports JPG, JPEG, PNG
                  </p>
                </div>
              )}
            </div>

            <textarea
              placeholder="Describe the scenario or occasion (e.g., 'Job interview at a tech company', 'First date at a casual restaurant', 'Wedding guest')"
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              className="w-full min-h-[120px] p-3 border border-gray-300 rounded-md resize-y"
            />

            <div className="flex gap-4">
              <button 
                className={`bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200 flex-1 flex items-center justify-center ${isLoading || !selectedFile || !scenario.trim() || backendStatus !== 'online' ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={analyzeFashion} 
                disabled={isLoading || !selectedFile || !scenario.trim() || backendStatus !== 'online'}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </>
                ) : "Get Fashion Advice"}
              </button>
              <button 
                className="border border-gray-300 hover:bg-gray-100 text-gray-700 px-4 py-2 rounded-md font-medium flex-1"
                onClick={resetForm}
                disabled={isLoading}
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        <div>
          {result && (
            <div className="bg-black rounded-lg shadow p-6 animate-fade-in">
              <h2 className="text-2xl font-bold mb-4 text-blue-400">Fashion Advice</h2>
              <p className="mb-4 whitespace-pre-line text-white font-medium">{result.text_advice}</p>
              {result.image_url && (
                <img src={result.image_url} alt="Fashion suggestion" className="w-full max-h-[400px] object-contain rounded-md border border-gray-600" />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FashionAdvisor;
import React, { useState } from 'react';
import { Upload, AlertCircle, CheckCircle, Clock, Shield, Eye, EyeOff } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8005';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setResult(null);
      setError(null);
    } else {
      setError('Please select a valid video file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const analyzeVideo = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Safe': 'text-green-600 bg-green-100',
      'Violence': 'text-red-600 bg-red-100',
      'Sexual Content': 'text-purple-600 bg-purple-100',
      'Graphic Content': 'text-orange-600 bg-orange-100',
      'Hate Speech': 'text-red-800 bg-red-200',
      'Other': 'text-gray-600 bg-gray-100'
    };
    return colors[category] || colors['Other'];
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-400 mr-3" />
            <h1 className="text-4xl font-bold text-white">NSFW Video Analyzer</h1>
          </div>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            AI-powered content moderation using advanced machine learning models
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Upload Section */}
          <div className="bg-gray-800 rounded-xl shadow-2xl p-8 mb-8">
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
                dragOver
                  ? 'border-blue-400 bg-blue-900/20'
                  : 'border-gray-600 hover:border-gray-500'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                Upload Video for Analysis
              </h3>
              <p className="text-gray-400 mb-6">
                Drag and drop your video file here, or click to browse
                <br />
                <span className="text-sm text-gray-500">Videos longer than 60 seconds will be automatically trimmed</span>
              </p>
              
              <input
                type="file"
                accept="video/*"
                onChange={(e) => handleFileSelect(e.target.files[0])}
                className="hidden"
                id="video-upload"
              />
              <label
                htmlFor="video-upload"
                className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg cursor-pointer transition-colors duration-200"
              >
                Choose Video File
              </label>
            </div>

            {file && (
              <div className="mt-6 p-4 bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-gray-400 text-sm">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={analyzeVideo}
                    disabled={uploading}
                    className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors duration-200 flex items-center"
                  >
                    {uploading ? (
                      <>
                        <Clock className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Eye className="w-4 h-4 mr-2" />
                        Analyze Video
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-900/50 border border-red-600 rounded-lg p-4 mb-8">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
                <p className="text-red-200">{error}</p>
              </div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="bg-gray-800 rounded-xl shadow-2xl p-8">
              <div className="flex items-center mb-6">
                <CheckCircle className="w-6 h-6 text-green-400 mr-3" />
                <h2 className="text-2xl font-bold text-white">Analysis Results</h2>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {/* NSFW Status */}
                <div className="bg-gray-700 rounded-lg p-6">
                  <div className="flex items-center mb-3">
                    {result.is_nsfw ? (
                      <EyeOff className="w-5 h-5 text-red-400 mr-2" />
                    ) : (
                      <Eye className="w-5 h-5 text-green-400 mr-2" />
                    )}
                    <h3 className="text-lg font-semibold text-white">Content Status</h3>
                  </div>
                  <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                    result.is_nsfw 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {result.is_nsfw ? 'NSFW Content Detected' : 'Safe Content'}
                  </div>
                </div>

                {/* Category */}
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Category</h3>
                  <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(result.category)}`}>
                    {result.category}
                  </div>
                </div>

                {/* Confidence */}
                {result.confidence && (
                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-3">Confidence Score</h3>
                    <div className="flex items-center">
                      <div className={`text-2xl font-bold ${getConfidenceColor(result.confidence)}`}>
                        {(result.confidence * 100).toFixed(1)}%
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              result.confidence >= 0.8 ? 'bg-green-500' :
                              result.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${result.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Analysis Method */}
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Analysis Method</h3>
                  <div className="text-blue-400 font-medium capitalize">
                    {result.method.replace('-', ' + ')}
                  </div>
                </div>
              </div>

              {/* Explanation */}
              {result.explanation && (
                <div className="mt-6 bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Detailed Analysis</h3>
                  <p className="text-gray-300 leading-relaxed">{result.explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p>Powered by Gemini AI, Joy Caption, and Grok</p>
        </div>
      </div>
    </div>
  );
}

export default App; 
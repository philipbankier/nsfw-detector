import React, { useState, useCallback } from 'react';
import { Upload, AlertCircle, CheckCircle2, XCircle, Loader2, Github, ExternalLink, FileVideo, Clock, Tag, Shield } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please select a valid video file');
      setFile(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const analyzeVideo = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/analyze`, {
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
      setIsAnalyzing(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'pornography': 'bg-pink-100 text-pink-800 border-pink-200',
      'violence': 'bg-red-100 text-red-800 border-red-200',
      'self-harm': 'bg-orange-100 text-orange-800 border-orange-200',
      'weapons': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'profanity': 'bg-purple-100 text-purple-800 border-purple-200',
      'other': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[category] || colors.other;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      0: 'bg-green-50 text-green-800 border-green-200',
      1: 'bg-blue-50 text-blue-800 border-blue-200',
      2: 'bg-yellow-50 text-yellow-800 border-yellow-200',
      3: 'bg-orange-50 text-orange-800 border-orange-200',
      4: 'bg-red-50 text-red-800 border-red-200',
      5: 'bg-red-100 text-red-900 border-red-300'
    };
    return colors[severity] || colors[0];
  };

  const getSeverityLabel = (severity) => {
    const labels = {
      0: 'Safe',
      1: 'Suggestive',
      2: 'Mature',
      3: 'Explicit',
      4: 'Extreme',
      5: 'Illegal'
    };
    return labels[severity] || 'Unknown';
  };

  const getSeverityProgress = (severity) => {
    return (severity / 5) * 100;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Top navigation bar */}
      <div className="w-full bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo section */}
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <span className="text-lg font-semibold text-gray-900">NSFW Analyzer</span>
              </div>
            </div>

            {/* Right side buttons */}
            <div className="flex space-x-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors"
              >
                <Github className="h-4 w-4 mr-2" />
                GitHub
              </a>
              
              <a
                href="https://mixpeek.com/contact"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              >
                Contact Us
                <ExternalLink className="h-4 w-4 ml-2" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Enhanced centered title */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4 tracking-tight">
              NSFW Video Analyzer
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Upload a video to analyze its content using advanced AI models
            </p>
          </div>

          {/* Enhanced upload area */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-12">
            <div
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                isDragging 
                  ? 'border-blue-400 bg-blue-50 scale-105' 
                  : file 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <div className="flex flex-col items-center">
                {file ? (
                  <CheckCircle2 className="mx-auto h-16 w-16 text-green-500 mb-4" />
                ) : (
                  <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                )}
                
                <div className="mb-4">
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    {file ? 'File Selected!' : 'Drag and drop a video file here'}
                  </p>
                  <p className="text-sm text-gray-500">
                    or{' '}
                    <label className="text-blue-600 hover:text-blue-500 cursor-pointer font-medium">
                      browse from your computer
                      <input
                        type="file"
                        className="hidden"
                        accept="video/*"
                        onChange={(e) => handleFileSelect(e.target.files[0])}
                      />
                    </label>
                  </p>
                </div>

                <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-500">
                  <span className="px-2 py-1 bg-gray-100 rounded">MP4</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">WebM</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">AVI</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">MOV</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Max file size: 100MB • Max duration: 60 seconds</p>
              </div>
            </div>

            {file && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileVideo className="h-5 w-5 text-blue-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.name}</p>
                      <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <XCircle className="h-5 w-5" />
                  </button>
                </div>
              </div>
            )}

            {file && (
              <button
                onClick={analyzeVideo}
                disabled={isAnalyzing}
                className={`mt-6 w-full flex justify-center items-center px-6 py-4 border border-transparent rounded-xl shadow-sm text-base font-medium text-white transition-all duration-200 ${
                  isAnalyzing
                    ? 'bg-blue-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                    Analyzing Video...
                  </>
                ) : (
                  'Analyze Video'
                )}
              </button>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
              <div className="flex">
                <AlertCircle className="h-6 w-6 text-red-500 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              {/* Results header */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-8 py-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg mr-4">
                      <CheckCircle2 className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">Analysis Complete</h2>
                      <p className="text-sm text-gray-600 flex items-center mt-1">
                        <Clock className="h-4 w-4 mr-1" />
                        Method: {result.method}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    {result.status === 'safe' ? (
                      <div className="flex items-center text-green-700">
                        <CheckCircle2 className="h-8 w-8 mr-2" />
                        <span className="text-2xl font-bold">SAFE</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-red-700">
                        <XCircle className="h-8 w-8 mr-2" />
                        <span className="text-2xl font-bold">NSFW</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Results content */}
              <div className="p-8 space-y-8">
                {/* Categories section */}
                <div>
                  <div className="flex items-center mb-4">
                    <Tag className="h-5 w-5 text-gray-500 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">Categories</h3>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    {result.categories.map((category) => (
                      <span
                        key={category}
                        className={`px-4 py-2 rounded-full text-sm font-medium border ${getCategoryColor(category)}`}
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Severity section */}
                <div>
                  <div className="flex items-center mb-4">
                    <AlertCircle className="h-5 w-5 text-gray-500 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">Severity Level</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className={`px-4 py-2 rounded-full text-sm font-medium border ${getSeverityColor(result.severity)}`}>
                        {getSeverityLabel(result.severity)} (Level {result.severity})
                      </span>
                      <span className="text-sm text-gray-500">{result.severity}/5</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full transition-all duration-500 ${
                          result.severity === 0 ? 'bg-green-500' :
                          result.severity <= 2 ? 'bg-yellow-500' :
                          result.severity <= 3 ? 'bg-orange-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${getSeverityProgress(result.severity)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Description section */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Analysis Description</h3>
                  <div className="bg-gray-50 rounded-lg p-4 border">
                    <p className="text-gray-700 leading-relaxed">{result.description}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App; 
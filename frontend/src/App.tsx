import { useState, useEffect } from 'react';
import './index.css';

const App = () => {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark mode
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    document.body.className = isDarkMode ? 'dark-mode' : '';
  }, [isDarkMode]);

  const inputWordCount = inputText.trim().split(/\s+/).filter(word => word.length > 0).length;
  const outputWordCount = outputText.trim().split(/\s+/).filter(word => word.length > 0).length;
  
  const estimatedTime = Math.max(5, Math.ceil(inputWordCount * 0.05));

  const handleHumanize = async () => {
    if (!inputText.trim()) return;
    
    setIsLoading(true);
    setProgress(0);
    setOutputText(''); 
    setCopied(false);
    
    const interval = setInterval(() => {
      setProgress(prev => (prev < 90 ? prev + (90 / (estimatedTime * 2)) : prev));
    }, 500);
    
    try {
      const response = await fetch('/api/humanize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      
      setProgress(100);
      const data = await response.json();
      setOutputText(data.text);
    } catch (error) {
      console.error("Error:", error);
      setOutputText("An error occurred during processing.");
    } finally {
      clearInterval(interval);
      setIsLoading(false);
    }
  };

  const handleCopyInput = () => navigator.clipboard.writeText(inputText);
  const handleCopyOutput = () => {
    navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClearInput = () => setInputText('');
  const handleClearOutput = () => { setOutputText(''); };

  return (
    <div className={`app-container ${isDarkMode ? 'dark-mode' : ''}`}>
      <main className="main-content">
        <header className="main-header">
          <h2>Raghav's Humanizer</h2>
          <button className="theme-toggle" onClick={() => setIsDarkMode(!isDarkMode)}>
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </header>
        
        <div className="panels">
          <section className="panel">
            <div className="panel-header">
              <h3>Input Text</h3>
              <div className="result-actions">
                <button className="small-btn" onClick={handleCopyInput}>📋</button>
                <button className="clear-result-btn" onClick={handleClearInput}>✕</button>
              </div>
            </div>
            <textarea 
              value={inputText} 
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your AI-generated text here..."
              disabled={isLoading}
            />
            <div className="stats">
              <span>{inputWordCount} words</span> | <span>{inputText.length} characters</span>
            </div>
          </section>
          
          <section className="panel">
            <div className="panel-header">
              <h3>Humanized Result</h3>
              <div className="result-actions">
                {outputText && (
                  <>
                    <button className="small-btn" onClick={handleCopyOutput}>
                      {copied ? "✅ Copied!" : "📋 Copy"}
                    </button>
                    <button className="clear-result-btn" onClick={handleClearOutput}>✕</button>
                  </>
                )}
              </div>
            </div>
            <div className="result-container">
              {isLoading ? (
                <div className="loading-state">
                  <div className="progress-container">
                    <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                  </div>
                  <p>Humanizing... (~{estimatedTime}s remaining)</p>
                </div>
              ) : (
                <>
                  <p className="output-text">{outputText || "Result will appear here..."}</p>
                  {outputText && (
                    <div className="stats">
                      <span>{outputWordCount} words</span> | <span>{outputText.length} characters</span>
                    </div>
                  )}
                </>
              )}
            </div>
          </section>
        </div>
        
        <div className="controls">
          <button className="humanize-btn" onClick={handleHumanize} disabled={isLoading || !inputText.trim()}>
            {isLoading ? "⚡ PROCESSING..." : "⚡ HUMANIZE"}
          </button>
        </div>
      </main>
    </div>
  );
};

export default App;

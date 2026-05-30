import { useState } from 'react';
import './index.css';

const App = () => {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const wordCount = inputText.trim().split(/\s+/).filter(word => word.length > 0).length;

  const handleHumanize = async () => {
    setIsLoading(true);
    setOutputText(''); // Clear previous output
    try {
      const response = await fetch('http://localhost:8000/api/humanize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await response.json();
      setOutputText(data.text);
    } catch (error) {
      console.error("Error:", error);
      setOutputText("An error occurred during processing.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand-box">✨ Raghav AI</div>
      </aside>
      
      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>Raghav's Humanizer</h2>
          <div style={{ color: 'var(--text-muted)' }}>Dashboard | History</div>
        </header>
        
        <div className="panels">
          <section className="panel">
            <textarea 
              value={inputText} 
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your AI-generated text here..."
            />
            <div className="word-count">{wordCount} words</div>
          </section>
          
          <section className="panel">
            <p style={{ margin: 0, color: outputText ? 'var(--on-surface)' : 'var(--text-muted)' }}>
              {isLoading ? "Humanizing..." : (outputText || "Humanized content will appear here after processing...")}
            </p>
          </section>
        </div>
        
        <div className="controls">
          <button className="humanize-btn" onClick={handleHumanize} disabled={isLoading}>
            {isLoading ? "⚡ PROCESSING..." : "⚡ HUMANIZE"}
          </button>
        </div>
      </main>
    </div>
  );
};

export default App;

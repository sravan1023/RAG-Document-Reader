import React from 'react';
import { useState, useRef, useEffect } from 'react';

// --- Helper Components ---
const LoadingSpinner = () => ( <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div> );
const SendIcon = () => ( <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white"> <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /> <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /> </svg> );
const UserIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg> );
const BotIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg> );
const UploadIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" x2="12" y1="3" y2="15"></line></svg> );


// --- Main App Component ---
export default function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { setMessages([{ sender: 'bot', text: "Hello! Please upload a PDF to begin.", sources: [] }]); }, []);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setUploadStatus('Uploading and processing...');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }
      
      setUploadStatus(data.message);
      setMessages([{ sender: 'bot', text: "Great! Your document is ready. What would you like to know?", sources: [] }]);
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim() || isLoading) return;

    const newUserMessage = { sender: 'user', text: userInput };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userInput }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const newBotMessage = { sender: 'bot', text: data.answer, sources: data.sources || [] };
      setMessages((prevMessages) => [...prevMessages, newBotMessage]);
    } catch (error) {
      console.error('Failed to get answer:', error);
      const errorMessage = { sender: 'bot', text: 'Sorry, something went wrong. Please check the server and try again.', sources: [] };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="font-sans bg-gray-100 flex flex-col h-screen">
      <header className="bg-gray-800 text-white p-4 shadow-md flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Ask My Doc</h1>
          <p className="text-sm text-gray-400">Retrieve Augmented answers from your documents</p>
        </div>
        <div className="flex items-center gap-4">
          <input type="file" id="pdf-upload" className="hidden" onChange={handleFileChange} accept=".pdf" />
          <label htmlFor="pdf-upload" className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 cursor-pointer transition-colors">
            <UploadIcon />
          </label>
          {selectedFile && <span className="text-sm">{selectedFile.name}</span>}
          <button onClick={handleUpload} disabled={!selectedFile || isLoading} className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors">
            {isLoading && uploadStatus ? 'Processing...' : 'Upload'}
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
        <div className="max-w-4xl mx-auto">
          {uploadStatus && <div className="text-center text-gray-500 my-4">{uploadStatus}</div>}
          {messages.map((msg, index) => (
            <div key={index} className={`flex items-start gap-4 my-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
              {msg.sender === 'bot' && ( <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center"><BotIcon /></div> )}
              <div className={`max-w-lg p-4 rounded-2xl shadow ${ msg.sender === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none' }`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 border-t border-gray-200 pt-3">
                    <h3 className="text-xs font-bold text-gray-500 mb-2">Sources:</h3>
                    <div className="space-y-2">
                      {msg.sources.map((source, i) => (
                        <div key={i} className="p-2 bg-gray-100 rounded-lg text-xs text-gray-600">
                          <p className="truncate"><strong>Page {source.metadata.page || 'N/A'}:</strong> "{source.content}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {msg.sender === 'user' && ( <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center"><UserIcon /></div> )}
            </div>
          ))}
          {isLoading && !uploadStatus && (
            <div className="flex items-start gap-4 my-4">
               <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center"><BotIcon /></div>
              <div className="bg-white p-4 rounded-2xl shadow rounded-bl-none"><LoadingSpinner /></div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 p-4 shadow-inner">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex items-center gap-4">
            <input type="text" value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="Ask a question about your document..." className="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 transition" disabled={isLoading} />
            <button type="submit" className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 disabled:bg-blue-300 transition-colors" disabled={isLoading || !userInput.trim()}><SendIcon /></button>
          </form>
        </div>
      </footer>
    </div>
  );
}
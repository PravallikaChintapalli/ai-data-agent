import React, { useState } from 'react'
import axios from 'axios'

function Chat({ uploaded }) {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])

  const ask = async () => {
    if (!question.trim()) return
    
    setMessages(prev => [...prev, { from: 'user', text: question }])
    
    try {
      const res = await axios.post('http://localhost:8000/query', {
        question: question,
        table_name: uploaded?.sheets?.[0]?.table
      })
      const data = res.data
      setMessages(prev => [...prev, {
        from: 'assistant',
        text: JSON.stringify(data, null, 2),
        chart: data.chart
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        from: 'assistant',
        text: 'Error: ' + (e.response?.data?.detail || e.message)
      }])
    }
    setQuestion('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      ask()
    }
  }

  return (
    <div>
      <h3>Ask about your data</h3>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <input 
          style={{ flex: 1, padding: 8 }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="e.g. sum of sales by region"
        />
        <button onClick={ask} disabled={!question.trim()}>
          Ask
        </button>
      </div>

      <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 15, padding: 10, border: '1px solid #ddd', borderRadius: 5 }}>
            <strong style={{ color: msg.from === 'user' ? '#007bff' : '#28a745' }}>
              {msg.from === 'user' ? 'You' : 'AI Assistant'}:
            </strong>
            <pre style={{ 
              background: '#f8f9fa', 
              padding: 10, 
              marginTop: 5,
              whiteSpace: 'pre-wrap',
              fontSize: '14px'
            }}>
              {msg.text}
            </pre>
            {msg.chart && (
              <img 
                src={`http://localhost:8000${msg.chart}`} 
                style={{ maxWidth: '100%', marginTop: 10 }}
                alt="Generated chart"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Chat
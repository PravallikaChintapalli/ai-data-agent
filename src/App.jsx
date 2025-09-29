import React, { useState } from 'react'
import Upload from './components/Upload'
import Chat from './components/Chat'

function App() {
  const [uploaded, setUploaded] = useState(null)

  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>AI Data Agent</h1>
      <div style={{ display: 'flex', gap: 20 }}>
        <div style={{ width: 400 }}>
          <Upload onUploaded={(data) => setUploaded(data)} />
        </div>
        <div style={{ flex: 1 }}>
          <Chat uploaded={uploaded} />
        </div>
      </div>
    </div>
  )
}

export default App
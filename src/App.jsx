import React from 'react'
import Upload from './components/Upload'
import Chat from './components/Chat'

export default function App(){
  const [uploaded, setUploaded] = React.useState(null)
  return (
    <div style={{padding:20,fontFamily:'Arial'}}>
      <h1>AI Data Agent</h1>
      <div style={{display:'flex',gap:20}}>
        <div style={{width:400}}>
          <Upload onUploaded={(data)=>setUploaded(data)} />
        </div>
        <div style={{flex:1}}>
          <Chat uploaded={uploaded} />
        </div>
      </div>
    </div>
  )
}
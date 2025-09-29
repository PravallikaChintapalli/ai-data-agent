import React from 'react'
import axios from 'axios'

export default function Chat({uploaded}){
  const [q, setQ] = React.useState('')
  const [msgs, setMsgs] = React.useState([])

  const ask = async ()=>{
    if(!q) return
    setMsgs(prev=>[...prev,{from:'user',text:q}])
    try{
      const res = await axios.post('http://localhost:8000/query',{question:q, table_name: uploaded?.sheets?.[0]?.table})
      const data = res.data
      setMsgs(prev=>[...prev,{from:'assistant',text:JSON.stringify(data, null, 2), chart: data.chart}])
    }catch(e){
      setMsgs(prev=>[...prev,{from:'assistant',text: 'Error: '+(e.response?.data?.detail||e.message)}])
    }
    setQ('')
  }

  return (
    <div>
      <h3>Ask about your data</h3>
      <div style={{display:'flex',gap:10}}>
        <input style={{flex:1}} value={q} onChange={(e)=>setQ(e.target.value)} placeholder='e.g. sum of sales by region' />
        <button onClick={ask}>Ask</button>
      </div>

      <div style={{marginTop:12}}>
        {msgs.map((m,i)=> (
          <div key={i} style={{marginBottom:12}}>
            <strong>{m.from}</strong>
            <pre style={{background:'#f4f4f4',padding:10,whiteSpace:'pre-wrap'}}>{m.text}</pre>
            {m.chart && (
              <img src={`http://localhost:8000${m.chart}`} style={{maxWidth:'400px'}} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

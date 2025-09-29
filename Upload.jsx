import React from 'react'
import axios from 'axios'

export default function Upload({onUploaded}){
  const [file, setFile] = React.useState(null)
  const [status, setStatus] = React.useState('')

  const upload = async ()=>{
    if(!file) return
    const fd = new FormData()
    fd.append('file', file)
    setStatus('Uploading...')
    try{
      const res = await axios.post('http://localhost:8000/upload', fd, {headers:{'Content-Type':'multipart/form-data'}})
      setStatus('Uploaded')
      onUploaded(res.data)
    }catch(e){
      setStatus('Upload failed: '+ (e.response?.data?.detail||e.message))
    }
  }

  return (
    <div>
      <h3>Upload Excel</h3>
      <input type="file" accept=".xls,.xlsx" onChange={(e)=>setFile(e.target.files[0])} />
      <div style={{marginTop:10}}>
        <button onClick={upload}>Upload</button>
      </div>
      <div style={{marginTop:10}}>{status}</div>
    </div>
  )
}

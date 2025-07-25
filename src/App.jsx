import { useState } from 'react'
import reactLogo from './assets/react.svg'
import { invoke } from '@tauri-apps/api/tauri'
import { open } from '@tauri-apps/api/dialog'
import { appDir } from '@tauri-apps/api/path'
import './App.css'

function App() {
  const [pdfPath, setPdfPath] = useState('')
  const [outputFolder, setOutputFolder] = useState('')
  const [noCsv, setNoCsv] = useState(false)
  const [ocrOutput, setOcrOutput] = useState('')
  const [loadingOcr, setLoadingOcr] = useState(false)

  const [ocrCsvPath, setOcrCsvPath] = useState('')
  const [groundTruthJsonPath, setGroundTruthJsonPath] = useState('')
  const [iouThreshold, setIouThreshold] = useState(0.5)
  const [accuracyOutput, setAccuracyOutput] = useState('')
  const [loadingAccuracy, setLoadingAccuracy] = useState(false)

  const selectPdf = async () => {
    const selected = await open({
      multiple: false,
      filters: [{
        name: 'PDF',
        extensions: ['pdf']
      }]
    })
    if (selected) {
      setPdfPath(selected)
    }
  }

  const selectOutputFolder = async () => {
    const selected = await open({
      directory: true,
      multiple: false,
    })
    if (selected) {
      setOutputFolder(selected)
    }
  }

  const runOcr = async () => {
    setLoadingOcr(true)
    setOcrOutput('')
    try {
      const result = await invoke('run_ocr_process', {
        pdfPath,
        outputFolder: outputFolder || await appDir(), // Use appDir if no output folder is selected
        noCsv,
      })
      setOcrOutput(result)
    } catch (error) {
      setOcrOutput(`Error: ${error}`)
    } finally {
      setLoadingOcr(false)
    }
  }

  const selectOcrCsv = async () => {
    const selected = await open({
      multiple: false,
      filters: [{
        name: 'CSV',
        extensions: ['csv']
      }]
    })
    if (selected) {
      setOcrCsvPath(selected)
    }
  }

  const selectGroundTruthJson = async () => {
    const selected = await open({
      multiple: false,
      filters: [{
        name: 'JSON',
        extensions: ['json']
      }]
    })
    if (selected) {
      setGroundTruthJsonPath(selected)
    }
  }

  const runAccuracyReview = async () => {
    setLoadingAccuracy(true)
    setAccuracyOutput('')
    try {
      const result = await invoke('run_accuracy_review', {
        ocrCsvPath,
        groundTruthJsonPath,
        iouThreshold,
      })
      setAccuracyOutput(result)
    } catch (error) {
      setAccuracyOutput(`Error: ${error}`)
    } finally {
      setLoadingAccuracy(false)
    }
  }

  return (
    <div className="container">
      <h1>OCR Application</h1>

      <div className="section">
        <h2>Run OCR</h2>
        <div className="input-group">
          <label>PDF File:</label>
          <input type="text" value={pdfPath} readOnly placeholder="Select PDF file" />
          <button onClick={selectPdf}>Select PDF</button>
        </div>

        <div className="input-group">
          <label>Output Folder:</label>
          <input type="text" value={outputFolder} readOnly placeholder="Select output folder (optional)" />
          <button onClick={selectOutputFolder}>Select Folder</button>
        </div>

        <div className="input-group">
          <label>
            <input
              type="checkbox"
              checked={noCsv}
              onChange={(e) => setNoCsv(e.target.checked)}
            />
            Do not output CSV
          </label>
        </div>

        <button onClick={runOcr} disabled={!pdfPath || loadingOcr}>
          {loadingOcr ? 'Running OCR...' : 'Run OCR'}
        </button>

        {ocrOutput && (
          <div className="output-box">
            <h3>OCR Output:</h3>
            <pre>{ocrOutput}</pre>
          </div>
        )}
      </div>

      <div className="section">
        <h2>Accuracy Review</h2>
        <div className="input-group">
          <label>OCR CSV File:</label>
          <input type="text" value={ocrCsvPath} readOnly placeholder="Select OCR results CSV file" />
          <button onClick={selectOcrCsv}>Select CSV</button>
        </div>

        <div className="input-group">
          <label>Ground Truth JSON File:</label>
          <input type="text" value={groundTruthJsonPath} readOnly placeholder="Select ground truth JSON file" />
          <button onClick={selectGroundTruthJson}>Select JSON</button>
        </div>

        <div className="input-group">
          <label>IoU Threshold:</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={iouThreshold}
            onChange={(e) => setIouThreshold(parseFloat(e.target.value))}
          />
        </div>

        <button onClick={runAccuracyReview} disabled={!ocrCsvPath || !groundTruthJsonPath || loadingAccuracy}>
          {loadingAccuracy ? 'Running Accuracy Review...' : 'Run Accuracy Review'}
        </button>

        {accuracyOutput && (
          <div className="output-box">
            <h3>Accuracy Review Output:</h3>
            <pre>{accuracyOutput}</pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

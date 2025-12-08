import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import MetricChart from '../components/MetricChart'
import './DeviceDetail.css'

const DeviceDetail = () => {
  const { deviceId } = useParams<{ deviceId: string }>()

  const { data: healthData, isLoading } = useQuery({
    queryKey: ['deviceHealth', deviceId],
    queryFn: () => api.getDeviceHealth(deviceId!),
    enabled: !!deviceId,
  })

  if (isLoading) {
    return <div className="loading">Loading device health...</div>
  }

  if (!healthData) {
    return <div className="error">Device not found</div>
  }

  return (
    <div className="device-detail">
      <h1>Device: {healthData.device_id}</h1>

      <div className="health-status">
        <div className={`status-badge ${healthData.overall_health}`}>
          {healthData.overall_health.toUpperCase()}
        </div>
      </div>

      <div className="health-summary">
        <h2>Health Summary</h2>
        <p>{healthData.summary}</p>
      </div>

      <div className="metrics-section">
        <h2>Key Metrics</h2>
        <div className="metrics-grid">
          {Object.entries(healthData.key_metrics || {}).map(([type, stats]: [string, any]) => (
            <div key={type} className="metric-card">
              <h3>{type}</h3>
              <div className="metric-stats">
                <div>Current: {stats.current?.toFixed(2)}</div>
                <div>Average: {stats.average?.toFixed(2)}</div>
                <div>Range: {stats.min?.toFixed(2)} - {stats.max?.toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {healthData.anomalies_detected > 0 && (
        <div className="anomalies-alert">
          <h2>Anomalies Detected</h2>
          <p>{healthData.anomalies_detected} anomaly(ies) found in the monitoring period</p>
        </div>
      )}
    </div>
  )
}

export default DeviceDetail

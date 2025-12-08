import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import './NetworkDevices.css'

const NetworkDevices = () => {
  const { data: devices, isLoading } = useQuery({
    queryKey: ['networkDevices'],
    queryFn: () => api.getNetworkDevices(),
  })

  if (isLoading) {
    return <div className="loading">Loading network devices...</div>
  }

  return (
    <div className="network-devices">
      <h1>Network Devices</h1>

      <div className="device-types-section">
        <h2>Supported Device Types</h2>
        <div className="device-types-grid">
          {devices?.device_types?.map((type: string) => (
            <div key={type} className="device-type-card">
              <h3>{type.charAt(0).toUpperCase() + type.slice(1)}</h3>
            </div>
          ))}
        </div>
      </div>

      <div className="metrics-section">
        <h2>Supported Network Metrics</h2>
        <div className="metrics-list">
          {devices?.supported_metrics?.map((metric: string) => (
            <div key={metric} className="metric-item">
              {metric.replace(/_/g, ' ')}
            </div>
          ))}
        </div>
      </div>

      <div className="actions-section">
        <h2>Device Management</h2>
        <p>Use the API to monitor network devices and generate automation scripts.</p>
        <div className="api-info">
          <code>GET /api/v1/network/devices/{'{device_id}'}/summary</code>
          <code>GET /api/v1/network/devices/{'{device_id}'}/issues</code>
          <code>POST /api/v1/network/devices/{'{device_id}'}/remediation</code>
        </div>
      </div>
    </div>
  )
}

export default NetworkDevices

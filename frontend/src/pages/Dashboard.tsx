import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import MetricChart from '../components/MetricChart'
import './Dashboard.css'

const Dashboard = () => {
  const { data: networkDevices } = useQuery({
    queryKey: ['networkDevices'],
    queryFn: () => api.getNetworkDevices(),
  })

  return (
    <div className="dashboard">
      <h1>Device Metrics Dashboard</h1>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Network Devices</h2>
          <div className="device-list">
            {networkDevices?.device_types?.map((type: string) => (
              <div key={type} className="device-type">
                {type}
              </div>
            ))}
          </div>
          <Link to="/network" className="view-all-link">
            View All Network Devices →
          </Link>
        </div>

        <div className="dashboard-card">
          <h2>Supported Metrics</h2>
          <div className="metrics-list">
            {networkDevices?.supported_metrics?.slice(0, 8).map((metric: string) => (
              <span key={metric} className="metric-tag">
                {metric}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <h2>Quick Actions</h2>
        <div className="quick-actions">
          <Link to="/network" className="action-btn">
            Monitor Network Devices
          </Link>
          <Link to="/devices/device-001" className="action-btn">
            View Device Details
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

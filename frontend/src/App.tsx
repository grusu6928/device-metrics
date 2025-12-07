import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import DeviceDetail from './pages/DeviceDetail'
import NetworkDevices from './pages/NetworkDevices'
import Login from './pages/Login'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="devices/:deviceId" element={<DeviceDetail />} />
            <Route path="network" element={<NetworkDevices />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App


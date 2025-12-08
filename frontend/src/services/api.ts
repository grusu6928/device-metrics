import axios from 'axios'

const API_BASE_URL = '/api/v1'

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

export const api = {
  async getDeviceHealth(deviceId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/metrics/health/${deviceId}`,
      getAuthHeaders()
    )
    return response.data
  },

  async ingestMetrics(metrics: any[]) {
    const response = await axios.post(
      `${API_BASE_URL}/metrics`,
      { metrics },
      getAuthHeaders()
    )
    return response.data
  },

  async getNetworkDeviceSummary(deviceId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/network/devices/${deviceId}/summary`,
      getAuthHeaders()
    )
    return response.data
  },

  async getNetworkIssues(deviceId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/network/devices/${deviceId}/issues`,
      getAuthHeaders()
    )
    return response.data
  },

  async getNetworkDevices() {
    const response = await axios.get(
      `${API_BASE_URL}/network/devices`,
      getAuthHeaders()
    )
    return response.data
  },

  async getPrometheusMetrics() {
    const response = await axios.get(
      `${API_BASE_URL}/metrics/prometheus`,
      getAuthHeaders()
    )
    return response.data
  },
}

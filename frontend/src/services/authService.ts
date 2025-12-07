import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const authService = {
  async login(username: string, password: string): Promise<string> {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await axios.post(`${API_BASE_URL}/auth/token`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    return response.data.access_token
  },
}


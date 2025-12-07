import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface MetricChartProps {
  data: Array<{ timestamp: string; value: number }>
  metricType: string
}

const MetricChart: React.FC<MetricChartProps> = ({ data, metricType }) => {
  const chartData = data.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    value: item.value,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#667eea"
          strokeWidth={2}
          name={metricType}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default MetricChart


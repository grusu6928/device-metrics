# Device Metrics Dashboard

React/TypeScript frontend dashboard for visualizing device metrics, anomalies, and network health.

## Features

- Real-time metric visualization
- Network device monitoring
- Anomaly detection alerts
- Health summaries
- Interactive charts and graphs
- JWT authentication

## Setup

```bash
npm install
npm run dev
```

The application will be available at `http://localhost:3000`

## Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/           # Page components
│   ├── services/        # API service layer
│   ├── contexts/        # React contexts (Auth)
│   ├── App.tsx         # Main app component
│   └── main.tsx         # Entry point
├── package.json
└── vite.config.ts      # Vite configuration
```

## Technologies

- React 18
- TypeScript
- Vite
- React Router
- TanStack Query (React Query)
- Recharts
- Axios

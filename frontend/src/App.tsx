import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Enterprise from './pages/Enterprise'
import Admin from './pages/Admin'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/enterprise" element={<Enterprise />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
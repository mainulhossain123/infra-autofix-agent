import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import IncidentsPage from './pages/IncidentsPage';
import RemediationPage from './pages/RemediationPage';
import ManualControlPage from './pages/ManualControlPage';
import ConfigPage from './pages/ConfigPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="remediation" element={<RemediationPage />} />
          <Route path="manual" element={<ManualControlPage />} />
          <Route path="config" element={<ConfigPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

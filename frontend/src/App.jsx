import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import JobsPage from './pages/JobsPage';
import SubmitJobPage from './pages/SubmitJobPage';
import JobDetailsPage from './pages/JobDetailsPage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<JobsPage />} />
        <Route path="/submit" element={<SubmitJobPage />} />
        <Route path="/jobs/:jobId" element={<JobDetailsPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
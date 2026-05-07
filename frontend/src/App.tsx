import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import GeneratePage from './pages/GeneratePage'
import PreviewPage from './pages/PreviewPage'
import EditorPage from './pages/EditorPage'
import ArticlesPage from './pages/ArticlesPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate" element={<GeneratePage />} />
          <Route path="/articles" element={<ArticlesPage />} />
          <Route path="/article/:id" element={<PreviewPage />} />
          <Route path="/article/:id/edit" element={<EditorPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

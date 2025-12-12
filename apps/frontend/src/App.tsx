import React from 'react';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { theme } from './theme';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { ReviewWorkspace } from './pages/ReviewWorkspace';
import { QuizViewer } from './pages/QuizViewer';
import { MindMapViewer } from './pages/MindMapViewer';
import { useAppStore } from './store/useAppStore';

function App() {
  const { darkMode } = useAppStore();

  return (
    <>
      <ColorModeScript initialColorMode={darkMode ? 'dark' : 'light'} />
      <ChakraProvider theme={theme}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/review" element={<ReviewWorkspace />} />
              <Route path="/quiz" element={<QuizViewer />} />
              <Route path="/mindmap" element={<MindMapViewer />} />
            </Routes>
          </Layout>
        </Router>
      </ChakraProvider>
    </>
  );
}

export default App;

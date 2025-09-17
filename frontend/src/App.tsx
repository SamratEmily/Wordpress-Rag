import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

// Create a theme instance
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface QueryResponse {
  answer: string | null;
  sources?: string[];
  confidence?: number;
  message?: string;
}

interface DocumentUploadResponse {
  success: boolean;
  message: string;
  chunks_added?: number;
}

function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [documentCount, setDocumentCount] = useState<number>(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploadLoading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('source_name', uploadFile.name);

      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload document');
      }

      const data = await response.json();
      setUploadResult(data);
      
      if (data.success) {
        setUploadFile(null);
        // Refresh document count
        fetchDocumentCount();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploadLoading(false);
    }
  };

  const fetchDocumentCount = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/count');
      if (response.ok) {
        const data = await response.json();
        setDocumentCount(data.document_count);
      }
    } catch (err) {
      console.error('Failed to fetch document count:', err);
    }
  };

  // Fetch document count on component mount
  React.useEffect(() => {
    fetchDocumentCount();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            Document RAG Assistant
          </Typography>
          
          <Typography variant="body1" align="center" sx={{ mb: 3, color: 'text.secondary' }}>
            Upload documents and ask questions. The system will only answer if it finds relevant information.
          </Typography>

          {/* Document Upload Section */}
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Documents in system: {documentCount}
            </Typography>
            <form onSubmit={handleFileUpload}>
              <input
                type="file"
                accept=".txt,.md,.pdf"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                style={{ marginBottom: '16px', width: '100%' }}
              />
              <Button
                type="submit"
                variant="outlined"
                disabled={!uploadFile || uploadLoading}
                fullWidth
              >
                {uploadLoading ? 'Uploading...' : 'Upload Document'}
              </Button>
            </form>
            {uploadResult && (
              <Box sx={{ mt: 2, p: 2, bgcolor: uploadResult.success ? 'success.light' : 'error.light' }}>
                <Typography variant="body2">
                  {uploadResult.message}
                  {uploadResult.chunks_added && ` (${uploadResult.chunks_added} chunks added)`}
                </Typography>
              </Box>
            )}
          </Paper>
          
          {/* Question Section */}
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Ask Questions
            </Typography>
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Ask a question about your documents"
                variant="outlined"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={loading}
                sx={{ mb: 2 }}
                multiline
                rows={3}
              />
              <Button
                type="submit"
                variant="contained"
                endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                disabled={loading || !question.trim()}
                fullWidth
              >
                {loading ? 'Getting Answer...' : 'Ask Question'}
              </Button>
            </form>
          </Paper>

          {error && (
            <Paper elevation={3} sx={{ p: 3, mb: 3, bgcolor: 'error.light' }}>
              <Typography color="error">{error}</Typography>
            </Paper>
          )}

          {response && (
            <Paper elevation={3} sx={{ p: 3 }}>
              {response.answer ? (
                <>
                  <Typography variant="h6" gutterBottom>
                    Answer:
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <ReactMarkdown>{response.answer}</ReactMarkdown>
                  </Box>
                  
                  {response.sources && response.sources.length > 0 && (
                    <>
                      <Typography variant="h6" gutterBottom>
                        Sources:
                      </Typography>
                      <Box component="ul" sx={{ pl: 2 }}>
                        {response.sources.map((source, index) => (
                          <Typography component="li" key={index}>
                            {source}
                          </Typography>
                        ))}
                      </Box>
                    </>
                  )}
                  
                  {response.confidence && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      Confidence: {(response.confidence * 100).toFixed(1)}%
                    </Typography>
                  )}
                </>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Relevant Answer Found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {response.message || "The documents don't contain relevant information to answer this question."}
                  </Typography>
                </Box>
              )}
            </Paper>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App; 
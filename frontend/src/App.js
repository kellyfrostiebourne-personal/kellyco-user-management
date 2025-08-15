import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import { GoogleOAuthProvider } from '@react-oauth/google';

import Login from './Login';
import Dashboard from './Dashboard';
import TodoList from './TodoList';
import Calendar from './Calendar';



// Create Kelly's custom light blue theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#5dade2', // Kelly's light blue
      dark: '#3498db',
      light: '#85c1e9',
      contrastText: '#ffffff', // White text on primary color
    },
    secondary: {
      main: '#2980b9',
      dark: '#21618c',
      contrastText: '#ffffff', // White text on secondary color
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
      color: '#2c3e50',
    },
    h5: {
      fontWeight: 500,
      color: '#34495e',
    },
    h6: {
      fontWeight: 500,
      // Removed color override - let Material UI handle AppBar contrast
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(93, 173, 226, 0.1)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          '& .MuiTypography-root': {
            color: '#ffffff', // Ensure AppBar text is white
          },
        },
      },
    },
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing authentication on app load
  useEffect(() => {
    document.title = 'User Management';
    
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  // Protected Route Component
  const ProtectedRoute = ({ children }) => {
    if (loading) {
      return <div>Loading...</div>;
    }
    
    return user ? children : <Navigate to="/login" replace />;
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}>
          Loading...
        </div>
      </ThemeProvider>
    );
  }

  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || 'your_google_client_id_here.apps.googleusercontent.com';

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route 
              path="/login" 
              element={
                user ? <Navigate to="/todos" replace /> : <Login onLogin={handleLogin} />
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard user={user} onLogout={handleLogout} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/todos" 
              element={
                <ProtectedRoute>
                  <TodoList user={user} onLogout={handleLogout} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/calendar" 
              element={
                <ProtectedRoute>
                  <Calendar user={user} onLogout={handleLogout} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/" 
              element={<Navigate to={user ? "/todos" : "/login"} replace />} 
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
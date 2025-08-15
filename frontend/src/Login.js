import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Card,
  CardContent,
  InputAdornment,
  Divider
} from '@mui/material';
import {
  Login as LoginIcon,
  Person as PersonIcon,
  Lock as LockIcon,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { GoogleLogin } from '@react-oauth/google';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showLegacyLogin, setShowLegacyLogin] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(data.user));
        onLogin(data.user);
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Unable to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleGoogleLogin = async (credentialResponse) => {
    setOauthLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          credential: credentialResponse.credential
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Store user data and token in localStorage
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('auth_token', data.token);
        onLogin(data.user);
      } else {
        setError(data.error || 'OAuth login failed');
      }
    } catch (error) {
      console.error('OAuth login error:', error);
      setError('Unable to connect to server');
    } finally {
      setOauthLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Google login was cancelled or failed');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8f9fa 0%, #e8f4fd 50%, #f8f9fa 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2
      }}
    >
      <Container maxWidth="sm">
        <Card
          elevation={8}
          sx={{
            borderRadius: '16px',
            overflow: 'hidden',
            background: 'linear-gradient(145deg, #ffffff, #f8f9fa)',
          }}
        >
          <Box
            sx={{
              background: 'linear-gradient(45deg, #5dade2, #3498db)',
              color: 'white',
              padding: 4,
              textAlign: 'center'
            }}
          >
            <LoginIcon sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h4" component="h1" fontWeight="600">
              KellyCo Login
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9, mt: 1 }}>
              Access your User Management System
            </Typography>
          </Box>

          <CardContent sx={{ padding: 4 }}>
            {/* Google OAuth Login */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" component="h2" align="center" sx={{ mb: 3, color: '#2c3e50' }}>
                Sign in with your Google Account
              </Typography>
              
              {oauthLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 2 }}>
                  <CircularProgress size={24} sx={{ mr: 2 }} />
                  <Typography variant="body2">Signing in with Google...</Typography>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <GoogleLogin
                    onSuccess={handleGoogleLogin}
                    onError={handleGoogleError}
                    theme="outline"
                    size="large"
                    text="signin_with"
                    shape="rectangular"
                    logo_alignment="left"
                  />
                </Box>
              )}
            </Box>

            <Divider sx={{ my: 3 }}>
              <Typography color="text.secondary" variant="body2">
                OR
              </Typography>
            </Divider>

            {/* Legacy Login Toggle */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Button
                variant="text"
                onClick={() => setShowLegacyLogin(!showLegacyLogin)}
                startIcon={<PersonIcon />}
                sx={{ color: '#5dade2' }}
              >
                {showLegacyLogin ? 'Hide Legacy Login' : 'Use Legacy Login (Demo Users)'}
              </Button>
            </Box>

            {/* Legacy Form Login */}
            {showLegacyLogin && (
              <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username or Email"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                margin="normal"
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                  }
                }}
              />

              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleInputChange}
                required
                margin="normal"
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockIcon color="primary" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button
                        onClick={togglePasswordVisibility}
                        sx={{ minWidth: 'auto', p: 1 }}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </Button>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                  }
                }}
              />

              {error && (
                <Alert severity="error" sx={{ mt: 2, borderRadius: '8px' }}>
                  {error}
                </Alert>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 3,
                  mb: 2,
                  borderRadius: '12px',
                  padding: '12px',
                  fontSize: '16px',
                  fontWeight: 600,
                  background: 'linear-gradient(45deg, #5dade2, #3498db)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #3498db, #2980b9)',
                  }
                }}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>

                <Divider sx={{ my: 3 }}>
                  <Typography color="text.secondary" variant="body2">
                    Demo Login Instructions
                  </Typography>
                </Divider>

                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    background: '#f8f9fa',
                    borderRadius: '8px',
                    border: '1px solid #e3f2fd'
                  }}
                >
                  <Typography variant="body2" color="text.secondary" align="center">
                    <strong>Legacy Login (Demo Users Only):</strong><br />
                    1. First create a user in the User Management system<br />
                    2. Use the username/email as login<br />
                    3. Use the <strong>first name</strong> as the password<br />
                    <br />
                    <em>Example: Username "john_doe", Password "John"</em>
                  </Typography>
                </Paper>
              </Box>
            )}

            {/* Error Display */}
            {error && (
              <Alert severity="error" sx={{ mt: 2, borderRadius: '8px' }}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;

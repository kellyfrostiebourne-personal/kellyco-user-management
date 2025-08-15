import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Box,
  Chip,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Breadcrumbs,
  Link
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  MoreVert as MoreVertIcon,
  Home as HomeIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

// Enhanced KellyCo Logo Component with animations
const KellyCoLogo = () => {
  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <Box
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        display: 'flex',
        alignItems: 'center',
        background: isHovered 
          ? 'linear-gradient(135deg, #ffffff, #e8f4fd, #ffffff)' 
          : 'linear-gradient(45deg, #ffffff, #f0f8ff)',
        borderRadius: '12px',
        padding: '6px 16px',
        border: isHovered 
          ? '2px solid rgba(93, 173, 226, 0.4)' 
          : '1px solid rgba(255, 255, 255, 0.3)',
        boxShadow: isHovered 
          ? '0 4px 20px rgba(93, 173, 226, 0.3), 0 0 0 1px rgba(93, 173, 226, 0.1)' 
          : '0 2px 8px rgba(0, 0, 0, 0.1)',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        transform: isHovered ? 'translateY(-1px) scale(1.02)' : 'translateY(0) scale(1)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: isHovered ? '0%' : '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)',
          transition: 'left 0.6s ease',
        },
      }}
    >
      {/* Animated Logo Symbol */}
      <Box
        sx={{
          width: '24px',
          height: '24px',
          marginRight: '8px',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Outer Ring */}
        <Box
          sx={{
            position: 'absolute',
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            border: '2px solid transparent',
            background: 'linear-gradient(45deg, #5dade2, #2980b9) border-box',
            WebkitMask: 'linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'subtract',
            maskComposite: 'subtract',
            animation: isHovered ? 'spin 2s linear infinite' : 'none',
            '@keyframes spin': {
              '0%': { transform: 'rotate(0deg)' },
              '100%': { transform: 'rotate(360deg)' },
            },
          }}
        />
        {/* Inner Symbol - K */}
        <Box
          sx={{
            fontSize: '12px',
            fontWeight: '900',
            color: '#2980b9',
            fontFamily: '"Segoe UI", Arial, sans-serif',
            transform: isHovered ? 'scale(1.1)' : 'scale(1)',
            transition: 'transform 0.3s ease',
          }}
        >
          K
        </Box>
      </Box>

      {/* Company Name */}
      <Box sx={{ display: 'flex', alignItems: 'baseline' }}>
        <Box
          sx={{
            fontSize: '20px',
            fontWeight: '700',
            background: isHovered 
              ? 'linear-gradient(45deg, #3498db, #5dade2, #2980b9)' 
              : 'linear-gradient(45deg, #5dade2, #2980b9)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.5px',
            fontFamily: '"Segoe UI", Arial, sans-serif',
            transform: isHovered ? 'translateX(2px)' : 'translateX(0)',
            transition: 'all 0.3s ease',
            backgroundSize: isHovered ? '200% 200%' : '100% 100%',
            animation: isHovered ? 'gradientShift 2s ease infinite' : 'none',
            '@keyframes gradientShift': {
              '0%': { backgroundPosition: '0% 50%' },
              '50%': { backgroundPosition: '100% 50%' },
              '100%': { backgroundPosition: '0% 50%' },
            },
          }}
        >
          Kelly
        </Box>
        <Box
          sx={{
            fontSize: '20px',
            fontWeight: '700',
            color: isHovered ? '#1e5f8c' : '#2980b9',
            marginLeft: '1px',
            fontFamily: '"Segoe UI", Arial, sans-serif',
            transform: isHovered ? 'translateX(2px)' : 'translateX(0)',
            transition: 'all 0.3s ease',
          }}
        >
          Co
        </Box>
      </Box>

      {/* Enhanced accent elements */}
      <Box
        sx={{
          marginLeft: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '3px',
        }}
      >
        {[0, 1, 2].map((index) => (
          <Box
            key={index}
            sx={{
              width: isHovered ? '4px' : '3px',
              height: isHovered ? '4px' : '3px',
              borderRadius: '50%',
              background: 'linear-gradient(45deg, #5dade2, #2980b9)',
              boxShadow: isHovered 
                ? '0 0 8px rgba(93, 173, 226, 0.6)' 
                : '0 0 4px rgba(93, 173, 226, 0.3)',
              transition: 'all 0.3s ease',
              transform: isHovered 
                ? `translateY(${Math.sin((index * Math.PI) / 3) * 2}px)` 
                : 'translateY(0)',
              transitionDelay: `${index * 0.1}s`,
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success');
  const [anchorEl, setAnchorEl] = useState(null);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  // Load users on component mount
  useEffect(() => {
    loadUsers();
    document.title = 'Settings - User Management - Kelly\'s User Management';
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyboardShortcut = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
        event.preventDefault();
        setLogoutDialogOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyboardShortcut);
    
    // Cleanup event listener
    return () => {
      document.removeEventListener('keydown', handleKeyboardShortcut);
    };
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/users`);
      if (response.ok) {
        const userData = await response.json();
        setUsers(userData);
      } else {
        setMessage('Error loading users');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setMessage('Error connecting to server');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const newUser = await response.json();
        setUsers(prev => [...prev, newUser]);
        setFormData({
          username: '',
          email: '',
          first_name: '',
          last_name: ''
        });
        setMessage('User added successfully!');
        setMessageType('success');
        setTimeout(() => setMessage(''), 5000);
      } else {
        const error = await response.json();
        setMessage(error.error || 'Error adding user');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error adding user:', error);
      setMessage('Error connecting to server');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogoutClick = () => {
    setLogoutDialogOpen(true);
    handleMenuClose();
  };

  const handleLogoutConfirm = () => {
    // Clear user session
    localStorage.removeItem('user');
    // Clear any other session data if needed
    sessionStorage.clear();
    // Call parent logout function to update app state
    onLogout();
    setLogoutDialogOpen(false);
  };

  const handleLogoutCancel = () => {
    setLogoutDialogOpen(false);
  };

  const clearMessage = () => {
    setMessage('');
  };

  return (
    <Box>
      {/* App Bar */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <AccountCircleIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            ⚙️ Settings - User Management
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              Welcome, {user.first_name}!
              {user.oauth_provider && (
                <Typography component="span" variant="caption" sx={{ display: 'block', opacity: 0.8 }}>
                  Signed in with {user.oauth_provider.charAt(0).toUpperCase() + user.oauth_provider.slice(1)}
                </Typography>
              )}
            </Typography>
            {user.profile_picture && (
              <Box
                component="img"
                src={user.profile_picture}
                alt={`${user.first_name}'s profile`}
                sx={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                }}
              />
            )}
            <KellyCoLogo />
            
            {/* Prominent Logout Button */}
            <Button
              variant="outlined"
              color="inherit"
              startIcon={<LogoutIcon />}
              onClick={handleLogoutClick}
              title="Back to Login (Ctrl/⌘ + L)"
              sx={{
                ml: 2,
                borderColor: 'rgba(255, 255, 255, 0.5)',
                color: 'white',
                '&:hover': {
                  borderColor: 'white',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
                display: { xs: 'none', md: 'flex' }, // Hide on mobile, show on desktop
              }}
            >
              Back to Login
            </Button>
            
            {/* Mobile Menu */}
            <IconButton
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ 
                ml: 1,
                display: { xs: 'flex', md: 'none' }, // Show on mobile, hide on desktop
              }}
            >
              <MoreVertIcon />
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={handleLogoutClick}>
              <LogoutIcon sx={{ mr: 1 }} />
              Back to Login
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Navigation Breadcrumbs */}
        <Box sx={{ mb: 3 }}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link
              component="button"
              variant="body2"
              color="inherit"
              onClick={() => navigate('/todos')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              <HomeIcon sx={{ mr: 0.5, fontSize: 16 }} />
              My Todo List
            </Link>
            <Typography color="text.primary" variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonIcon sx={{ mr: 0.5, fontSize: 16 }} />
              User Management
            </Typography>
          </Breadcrumbs>
        </Box>



        <Grid container spacing={4}>
          
          {/* Add User Form */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <AddIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h5" component="h2">
                  Add New User
                </Typography>
              </Box>
              
              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Username"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                      InputProps={{
                        startAdornment: <PersonIcon color="action" sx={{ mr: 1 }} />,
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                      InputProps={{
                        startAdornment: <EmailIcon color="action" sx={{ mr: 1 }} />,
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
                      sx={{ mt: 2, minWidth: 140 }}
                    >
                      {loading ? 'Adding...' : 'Add User'}
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </Paper>
          </Grid>

          {/* Users List */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" component="h2">
                  Users ({users.length})
                </Typography>
                <Button
                  variant="outlined"
                  onClick={loadUsers}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={16} /> : <RefreshIcon />}
                  size="small"
                >
                  {loading ? 'Loading...' : 'Refresh'}
                </Button>
              </Box>
              
              <Box sx={{ maxHeight: '600px', overflowY: 'auto' }}>
                {users.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <PersonIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                      No users found. Add some users to get started!
                    </Typography>
                  </Box>
                ) : (
                  <Grid container spacing={2}>
                    {users.map((userItem, index) => (
                      <Grid item xs={12} key={userItem.id}>
                        <Card 
                          variant="outlined" 
                          sx={{ 
                            transition: 'all 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              boxShadow: '0 4px 12px rgba(93, 173, 226, 0.15)',
                            }
                          }}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                              <Typography variant="h6" component="h3" color="primary">
                                {userItem.first_name} {userItem.last_name}
                              </Typography>
                              <Chip
                                label={userItem.is_active ? 'Active' : 'Inactive'}
                                color={userItem.is_active ? 'success' : 'default'}
                                size="small"
                              />
                            </Box>
                            
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              <strong>Username:</strong> {userItem.username}
                            </Typography>
                            
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              <strong>Email:</strong> {userItem.email}
                            </Typography>
                            
                            <Typography variant="body2" color="text.secondary">
                              <strong>Created:</strong> {new Date(userItem.created_at).toLocaleString()}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Success/Error Messages */}
        {message && (
          <Box sx={{ position: 'fixed', bottom: 20, right: 20, zIndex: 1000 }}>
            <Alert 
              severity={messageType}
              onClose={clearMessage}
              sx={{ 
                minWidth: 300,
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              }}
            >
              {message}
            </Alert>
          </Box>
        )}

        {/* Logout Confirmation Dialog */}
        <Dialog
          open={logoutDialogOpen}
          onClose={handleLogoutCancel}
          aria-labelledby="logout-dialog-title"
          aria-describedby="logout-dialog-description"
        >
          <DialogTitle id="logout-dialog-title">
            {"Confirm Logout"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="logout-dialog-description">
              Are you sure you want to logout and return to the login page? 
              Any unsaved changes will be lost.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleLogoutCancel} color="primary">
              Cancel
            </Button>
            <Button 
              onClick={handleLogoutConfirm} 
              color="primary" 
              variant="contained"
              startIcon={<ArrowBackIcon />}
              autoFocus
            >
              Yes, Back to Login
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default Dashboard;

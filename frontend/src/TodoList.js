import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Checkbox,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  AppBar,
  Toolbar,
  Container,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Schedule as ScheduleIcon,
  Flag as FlagIcon,
  Settings as SettingsIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const TodoList = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTodo, setEditingTodo] = useState(null);
  const [newTodo, setNewTodo] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: ''
  });

  // Fetch todos from API
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8080/api/todos?user_id=${user?.id || '2365999676'}`);
      if (response.ok) {
        const todosData = await response.json();
        setTodos(todosData);
      } else {
        setError('Failed to fetch todos');
      }
    } catch (err) {
      setError('Unable to connect to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, [user]);

  useEffect(() => {
    document.title = 'My Todo List - Kelly\'s User Management';
  }, []);

  // Handle creating a new todo
  const handleCreateTodo = async () => {
    if (!newTodo.title.trim()) return;

    try {
      const response = await fetch('http://localhost:8080/api/todos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newTodo,
          user_id: user?.id || '2365999676'
        }),
      });

      if (response.ok) {
        const todo = await response.json();
        setTodos(prev => [todo, ...prev]);
        setNewTodo({ title: '', description: '', priority: 'medium', due_date: '' });
        setOpenDialog(false);
      } else {
        setError('Failed to create todo');
      }
    } catch (err) {
      setError('Unable to connect to server');
    }
  };

  // Handle updating a todo
  const handleUpdateTodo = async () => {
    if (!editingTodo || !editingTodo.title.trim()) return;

    try {
      const response = await fetch(`http://localhost:8080/api/todos/${editingTodo.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editingTodo),
      });

      if (response.ok) {
        const updatedTodo = await response.json();
        setTodos(prev => prev.map(todo => 
          todo.id === updatedTodo.id ? updatedTodo : todo
        ));
        setEditingTodo(null);
        setOpenDialog(false);
      } else {
        setError('Failed to update todo');
      }
    } catch (err) {
      setError('Unable to connect to server');
    }
  };

  // Handle toggling todo completion
  const handleToggleComplete = async (todo) => {
    try {
      const response = await fetch(`http://localhost:8080/api/todos/${todo.id}/complete`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ completed: !todo.completed }),
      });

      if (response.ok) {
        const updatedTodo = await response.json();
        setTodos(prev => prev.map(t => 
          t.id === updatedTodo.id ? updatedTodo : t
        ));
      } else {
        setError('Failed to update todo');
      }
    } catch (err) {
      setError('Unable to connect to server');
    }
  };

  // Handle deleting a todo
  const handleDeleteTodo = async (todoId) => {
    try {
      const response = await fetch(`http://localhost:8080/api/todos/${todoId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setTodos(prev => prev.filter(todo => todo.id !== todoId));
      } else {
        setError('Failed to delete todo');
      }
    } catch (err) {
      setError('Unable to connect to server');
    }
  };

  // Filter todos based on current filter
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true; // all
  });

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  // Open dialog for new todo
  const openNewTodoDialog = () => {
    setNewTodo({ title: '', description: '', priority: 'medium', due_date: '' });
    setEditingTodo(null);
    setOpenDialog(true);
  };

  // Open dialog for editing todo
  const openEditTodoDialog = (todo) => {
    setEditingTodo({ ...todo });
    setNewTodo({ title: '', description: '', priority: 'medium', due_date: '' });
    setOpenDialog(true);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/dashboard')}
            sx={{ mr: 2 }}
            title="User Management Settings"
          >
            <SettingsIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📝 My Todo List
          </Typography>
          <IconButton
            color="inherit"
            onClick={() => navigate('/calendar')}
            sx={{ mr: 1 }}
            title="Calendar View"
          >
            <CalendarIcon />
          </IconButton>
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 3, mb: 3 }}>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Stats Card */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {todos.length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Tasks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {todos.filter(t => !t.completed).length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {todos.filter(t => t.completed).length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Completed
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Filter Tabs */}
        <Paper sx={{ mb: 2 }}>
          <Tabs
            value={filter}
            onChange={(e, newValue) => setFilter(newValue)}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab label="All" value="all" />
            <Tab label="Active" value="active" />
            <Tab label="Completed" value="completed" />
          </Tabs>
        </Paper>

        {/* Todo List */}
        <Paper>
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : filteredTodos.length === 0 ? (
            <Box p={4} textAlign="center">
              <Typography variant="h6" color="textSecondary" gutterBottom>
                {filter === 'all' ? 'No todos yet!' : `No ${filter} todos`}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {filter === 'all' ? 'Click the + button to add your first todo' : `Switch to "All" to see other todos`}
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredTodos.map((todo, index) => (
                <React.Fragment key={todo.id}>
                  <ListItem>
                    <ListItemIcon>
                      <Checkbox
                        edge="start"
                        checked={todo.completed}
                        onChange={() => handleToggleComplete(todo)}
                        icon={<RadioButtonUncheckedIcon />}
                        checkedIcon={<CheckCircleIcon />}
                        color="primary"
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography
                            variant="body1"
                            sx={{
                              textDecoration: todo.completed ? 'line-through' : 'none',
                              opacity: todo.completed ? 0.6 : 1
                            }}
                          >
                            {todo.title}
                          </Typography>
                          <Chip
                            size="small"
                            label={todo.priority}
                            color={getPriorityColor(todo.priority)}
                            variant="outlined"
                            icon={<FlagIcon />}
                          />
                          {todo.due_date && (
                            <Chip
                              size="small"
                              label={new Date(todo.due_date).toLocaleDateString()}
                              variant="outlined"
                              icon={<ScheduleIcon />}
                            />
                          )}
                        </Box>
                      }
                      secondary={todo.description}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => openEditTodoDialog(todo)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        edge="end"
                        onClick={() => handleDeleteTodo(todo.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < filteredTodos.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>

        {/* Add Todo FAB */}
        <Fab
          color="primary"
          aria-label="add"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={openNewTodoDialog}
        >
          <AddIcon />
        </Fab>

        {/* Add/Edit Todo Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingTodo ? 'Edit Todo' : 'Add New Todo'}
          </DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Title"
              fullWidth
              variant="outlined"
              value={editingTodo ? editingTodo.title : newTodo.title}
              onChange={(e) => editingTodo 
                ? setEditingTodo(prev => ({ ...prev, title: e.target.value }))
                : setNewTodo(prev => ({ ...prev, title: e.target.value }))
              }
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              value={editingTodo ? editingTodo.description : newTodo.description}
              onChange={(e) => editingTodo 
                ? setEditingTodo(prev => ({ ...prev, description: e.target.value }))
                : setNewTodo(prev => ({ ...prev, description: e.target.value }))
              }
              sx={{ mb: 2 }}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={editingTodo ? editingTodo.priority : newTodo.priority}
                    label="Priority"
                    onChange={(e) => editingTodo 
                      ? setEditingTodo(prev => ({ ...prev, priority: e.target.value }))
                      : setNewTodo(prev => ({ ...prev, priority: e.target.value }))
                    }
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={editingTodo ? editingTodo.due_date || '' : newTodo.due_date}
                  onChange={(e) => editingTodo 
                    ? setEditingTodo(prev => ({ ...prev, due_date: e.target.value }))
                    : setNewTodo(prev => ({ ...prev, due_date: e.target.value }))
                  }
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button 
              onClick={editingTodo ? handleUpdateTodo : handleCreateTodo}
              variant="contained"
              disabled={editingTodo ? !editingTodo.title.trim() : !newTodo.title.trim()}
            >
              {editingTodo ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default TodoList;

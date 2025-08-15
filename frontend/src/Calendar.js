import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Grid,
  Paper,
  AppBar,
  Toolbar,
  Button,
  Tooltip,
  Badge
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ArrowBack as ArrowBackIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Calendar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [todos, setTodos] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [loading, setLoading] = useState(true);

  // Fetch todos when component mounts
  useEffect(() => {
    fetchTodos();
    document.title = 'Calendar - Kelly\'s User Management';
  }, [user]);

  // Debug effect to log todos state changes
  useEffect(() => {
    console.log('📊 Todos state updated:', todos);
    console.log('📊 Number of todos with due dates:', todos.length);
    todos.forEach((todo, index) => {
      console.log(`📊 Todo ${index + 1}: ${todo.title} - Due: ${todo.due_date} - Completed: ${todo.completed}`);
    });
  }, [todos]);

  const fetchTodos = async () => {
    try {
      console.log('Fetching todos from /api/todos...');
      const response = await fetch('http://localhost:8080/api/todos', {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('API Response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Raw API response:', data);
        const todosWithDates = data.filter(todo => todo.due_date);
        console.log('Filtered todos with due dates:', todosWithDates);
        setTodos(todosWithDates); // Only todos with due dates
      } else {
        const errorText = await response.text();
        console.error('Failed to fetch todos:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error fetching todos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get the first day of the month and number of days
  const getMonthData = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday
    
    const days = [];
    const current = new Date(startDate);
    
    // Generate 42 days (6 weeks) to fill the calendar grid
    for (let i = 0; i < 42; i++) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    return {
      days,
      month,
      year,
      firstDay,
      lastDay
    };
  };

  // Get todos for a specific date
  const getTodosForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    console.log(`Looking for todos on date: ${dateStr}`);
    const matchingTodos = todos.filter(todo => {
      console.log(`  Comparing todo due_date "${todo.due_date}" with "${dateStr}"`);
      return todo.due_date === dateStr;
    });
    console.log(`  Found ${matchingTodos.length} todos for ${dateStr}`);
    return matchingTodos;
  };

  // Determine background color based on todo status and date
  const getDayBackgroundColor = (date) => {
    const todosForDay = getTodosForDate(date);
    
    // Only log for days that might have todos (reduce noise)
    const dateStr = date.toISOString().split('T')[0];
    if (dateStr.includes('2025-08-13') || dateStr.includes('2025-08-16') || dateStr.includes('2025-08-18')) {
      console.log(`🎯 Checking important date: ${dateStr}, Found ${todosForDay.length} todos`);
    }
    
    if (todosForDay.length === 0) return 'transparent';

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const compareDate = new Date(date);
    compareDate.setHours(0, 0, 0, 0);
    
    const diffTime = compareDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    // Debug logging for days with todos
    console.log(`📅 Date: ${dateStr}, Todos: ${todosForDay.length}, DiffDays: ${diffDays}`);
    todosForDay.forEach(todo => {
      console.log(`  📝 Todo: ${todo.title}, Completed: ${todo.completed}, Due: ${todo.due_date}`);
    });

    // Priority-based color logic (incomplete todos take precedence)
    const incompleteTodos = todosForDay.filter(todo => !todo.completed);
    const completedTodos = todosForDay.filter(todo => todo.completed);

    console.log(`  📊 Breakdown: ${incompleteTodos.length} incomplete, ${completedTodos.length} completed`);

    // PRIORITY 1: Incomplete todos (always show these first)
    if (incompleteTodos.length > 0) {
      if (diffDays < 0) {
        // Past incomplete todos - RED (highest priority)
        console.log(`  🔴 -> RED (past incomplete - HIGH PRIORITY)`);
        return '#ffebee'; // Light red background
      } else if (diffDays <= 5) {
        // Within 5 days incomplete todos - ORANGE
        console.log(`  🟠 -> ORANGE (due soon incomplete)`);
        return '#fff3e0'; // Light orange background
      } else {
        // Future incomplete todos (>5 days) - GREEN
        console.log(`  🟢 -> GREEN (future incomplete)`);
        return '#e8f5e8'; // Light green background
      }
    }
    
    // PRIORITY 2: Only completed todos (no incomplete ones)
    else if (completedTodos.length > 0 && diffDays < 0) {
      // Past completed todos - BLUE
      console.log(`  🔵 -> BLUE (past completed only)`);
      return '#e3f2fd'; // Light blue background
    }

    console.log(`  ⚪ -> TRANSPARENT (no matching conditions)`);
    return 'transparent';
  };

  // Get border color for stronger indication
  const getDayBorderColor = (date) => {
    const todosForDay = getTodosForDate(date);
    if (todosForDay.length === 0) return 'transparent';

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const compareDate = new Date(date);
    compareDate.setHours(0, 0, 0, 0);
    
    const diffTime = compareDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const hasIncompleteTodos = todosForDay.some(todo => !todo.completed);
    const hasCompletedTodos = todosForDay.some(todo => todo.completed);

    if (hasIncompleteTodos) {
      if (diffDays < 0) {
        return '#f44336'; // Red border
      } else if (diffDays <= 5) {
        return '#ff9800'; // Orange border
      } else {
        return '#4caf50'; // Green border
      }
    } else if (hasCompletedTodos && diffDays < 0) {
      return '#2196f3'; // Blue border
    }

    return 'transparent';
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  // Navigate to next month
  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  // Navigate to current month
  const goToCurrentMonth = () => {
    setCurrentDate(new Date());
  };

  const monthData = getMonthData(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/todos')}
            sx={{ mr: 2 }}
            title="Back to Todo List"
          >
            <ArrowBackIcon />
          </IconButton>
          <CalendarIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📅 Calendar
          </Typography>
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Calendar Content */}
      <Box sx={{ p: 3 }}>
        {/* Calendar Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <IconButton onClick={goToPreviousMonth} size="large">
            <ChevronLeftIcon />
          </IconButton>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h4" component="h1">
              {monthNames[monthData.month]} {monthData.year}
            </Typography>
            <Button 
              variant="outlined" 
              onClick={goToCurrentMonth}
              size="small"
              startIcon={<CalendarIcon />}
            >
              Today
            </Button>
          </Box>
          
          <IconButton onClick={goToNextMonth} size="large">
            <ChevronRightIcon />
          </IconButton>
        </Box>

        {/* Color Legend */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            <strong>Legend:</strong>
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#ffebee', border: '2px solid #f44336', borderRadius: 1 }} />
              <Typography variant="body2">Overdue (Incomplete)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#fff3e0', border: '2px solid #ff9800', borderRadius: 1 }} />
              <Typography variant="body2">Due Soon (≤5 days)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#e8f5e8', border: '2px solid #4caf50', borderRadius: 1 }} />
              <Typography variant="body2">Future (>5 days)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#e3f2fd', border: '2px solid #2196f3', borderRadius: 1 }} />
              <Typography variant="body2">Completed (Past)</Typography>
            </Box>
          </Box>
        </Box>

        {/* Day Headers */}
        <Grid container spacing={1} sx={{ mb: 1 }}>
          {dayNames.map((dayName) => (
            <Grid item xs key={dayName}>
              <Paper
                elevation={0}
                sx={{
                  p: 1,
                  textAlign: 'center',
                  backgroundColor: '#e0e0e0',
                  fontWeight: 'bold'
                }}
              >
                <Typography variant="body2">{dayName}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Debug Info */}
        {todos.length > 0 && (
          <Box sx={{ mb: 2, p: 2, backgroundColor: '#fff3e0', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Debug Info:</strong>
            </Typography>
            <Typography variant="body2">
              Total todos loaded: {todos.length}
            </Typography>
            {todos.map((todo, index) => (
              <Typography key={index} variant="body2">
                • {todo.title} - Due: {todo.due_date} - {todo.completed ? 'Completed' : 'Incomplete'}
              </Typography>
            ))}
          </Box>
        )}

        {/* Calendar Grid */}
        <Grid container spacing={1}>
          {monthData.days.map((date, index) => {
            const todosForDay = getTodosForDate(date);
            const backgroundColor = getDayBackgroundColor(date);
            const borderColor = getDayBorderColor(date);
            
            return (
              <Grid item xs key={index}>
                <Tooltip
                  title={
                    todosForDay.length > 0
                      ? `${todosForDay.length} todo(s): ${todosForDay.map(t => t.title).join(', ')}`
                      : ''
                  }
                  arrow
                >
                  <Paper
                    elevation={isToday(date) ? 3 : 1}
                    sx={{
                      p: 1,
                      minHeight: 80,
                      textAlign: 'center',
                      cursor: todosForDay.length > 0 ? 'pointer' : 'default',
                      backgroundColor,
                      border: borderColor !== 'transparent' ? `2px solid ${borderColor}` : '1px solid #e0e0e0',
                      position: 'relative',
                      '&:hover': todosForDay.length > 0 ? {
                        elevation: 3,
                        boxShadow: 3
                      } : {}
                    }}
                    onClick={() => {
                      if (todosForDay.length > 0) {
                        navigate('/todos', { 
                          state: { 
                            filterDate: date.toISOString().split('T')[0] 
                          } 
                        });
                      }
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: isToday(date) ? 'bold' : 'normal',
                        color: isCurrentMonth(date) ? 'text.primary' : 'text.secondary',
                        fontSize: isToday(date) ? '1.1rem' : '0.875rem'
                      }}
                    >
                      {date.getDate()}
                    </Typography>
                    
                    {todosForDay.length > 0 && (
                      <Badge
                        badgeContent={todosForDay.length}
                        color="primary"
                        sx={{
                          position: 'absolute',
                          top: 4,
                          right: 4,
                          '& .MuiBadge-badge': {
                            fontSize: '0.6rem',
                            minWidth: 16,
                            height: 16
                          }
                        }}
                      />
                    )}
                    
                    {isToday(date) && (
                      <Box
                        sx={{
                          position: 'absolute',
                          bottom: 2,
                          left: '50%',
                          transform: 'translateX(-50%)',
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          backgroundColor: '#1976d2'
                        }}
                      />
                    )}
                  </Paper>
                </Tooltip>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </Box>
  );
};

export default Calendar;

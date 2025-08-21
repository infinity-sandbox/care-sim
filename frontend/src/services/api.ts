import axios from 'axios';
import type { ExpenseItem, FormData, InsightData, Recommendations } from '../types/simulatorTypes';

const API_URL = process.env.REACT_APP_BACKEND_API_URL;

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_URL
});

// Add request interceptor to include access token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Add response interceptor to handle token expiration
api.interceptors.response.use(response => {
  return response;
}, error => {
  if (error.response?.status === 401) {
    // Handle token expiration or invalid token
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '/login';
  }
  return Promise.reject(error);
});

// Add this function to your API service
export const getProFormaDashboardData = async (formData: FormData): Promise<any> => {
  try {
    const response = await api.post('/api/v1/insight/pro-forma-dashboard-data', formData);
    return response.data;
  } catch (error) {
    console.error('Error fetching pro forma dashboard data:', error);
    
    // Return dummy data if the API is not available
    return generateDummyDashboardData(formData);
  }
};


// Generate realistic dummy data for the dashboard
const generateDummyDashboardData = (formData: FormData) => {
  // Calculate current year totals from form data
  const currentYearRevenue = formData.revenueSources.reduce((sum, source) => sum + (source.monthlyAmount || 0), 0) * 12;
  
  const expenseCategories = ["employees", "facilities", "administrative", "supplies"];
  const currentYearExpenses = expenseCategories.reduce((sum, category) => {
    const categoryExpenses = formData[category as keyof FormData] as ExpenseItem[];
    return sum + categoryExpenses.reduce((catSum, item) => catSum + (item.monthlyAmount || 0), 0) * 12;
  }, 0);
  
  const currentYearProfit = currentYearRevenue - currentYearExpenses;
  
  // Calculate classroom utilization
  const totalCapacity = formData.classrooms.reduce((sum, classroom) => sum + (classroom.capacity || 0), 0);
  const totalStudents = formData.classrooms.reduce((sum, classroom) => sum + (classroom.avgStudents || 0), 0);
  const currentUtilization = totalCapacity > 0 ? (totalStudents / totalCapacity) * 100 : 0;
  
  // Get goal percentages from form data
  const revenueGoal = formData.goals.find(goal => goal.goal.includes("Revenue")) || { targetPercentage: 10 };
  const expenseGoal = formData.goals.find(goal => goal.goal.includes("Expense")) || { targetPercentage: 5 };
  const utilizationGoal = formData.goals.find(goal => goal.goal.includes("Utilization")) || { targetPercentage: 15 };
  
  const revenueIncreasePct = revenueGoal.targetPercentage || 10;
  const expenseReductionPct = expenseGoal.targetPercentage || 5;
  const utilizationIncreasePct = utilizationGoal.targetPercentage || 15;
  
  // Calculate next year projections
  const nextYearRevenue = currentYearRevenue * (1 + revenueIncreasePct / 100);
  const nextYearExpenses = currentYearExpenses * (1 - expenseReductionPct / 100);
  const nextYearProfit = nextYearRevenue - nextYearExpenses;
  const nextYearUtilization = Math.min(currentUtilization * (1 + utilizationIncreasePct / 100), 100);
  
  // Generate line chart data (24 months)
  const lineChartData = [];
  const monthlyRevenueGrowth = (nextYearRevenue - currentYearRevenue) / 12;
  const monthlyExpenseReduction = (currentYearExpenses - nextYearExpenses) / 12;
  const monthlyUtilizationGrowth = (nextYearUtilization - currentUtilization) / 12;
  
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  
  for (let month = 0; month < 24; month++) {
    if (month < 12) {
      // Current year - constant values
      lineChartData.push({
        month: `${month % 12 + 1}/${currentYear}`,
        revenue: currentYearRevenue / 12,
        expenses: currentYearExpenses / 12,
        utilization: currentUtilization
      });
    } else {
      // Next year - linear progression
      const progress = (month - 11) / 12;
      lineChartData.push({
        month: `${month % 12 + 1}/${currentYear + 1}`,
        revenue: (currentYearRevenue / 12) + (monthlyRevenueGrowth * progress),
        expenses: (currentYearExpenses / 12) - (monthlyExpenseReduction * progress),
        utilization: currentUtilization + (monthlyUtilizationGrowth * progress)
      });
    }
  }
  
  // Generate bar chart data (yearly comparison)
  const barChartData = [
    {
      year: "Current Year",
      revenue: currentYearRevenue,
      expenses: currentYearExpenses,
      profit: currentYearProfit,
      utilization: currentUtilization
    },
    {
      year: "Next Year",
      revenue: nextYearRevenue,
      expenses: nextYearExpenses,
      profit: nextYearProfit,
      utilization: nextYearUtilization
    }
  ];
  
  // Generate goal-oriented chart data
  const goalChartData = [
    {
      goal_type: "Increase Revenue",
      target_percentage: revenueIncreasePct,
      achieved_percentage: Math.min(revenueIncreasePct, 100)
    },
    {
      goal_type: "Reduce Expense",
      target_percentage: expenseReductionPct,
      achieved_percentage: Math.min(expenseReductionPct, 100)
    },
    {
      goal_type: "Improve Utilization",
      target_percentage: utilizationIncreasePct,
      achieved_percentage: Math.min(utilizationIncreasePct, 100)
    }
  ];
  
  return {
    line_chart: lineChartData,
    bar_chart: barChartData,
    goal_chart: goalChartData,
    summary: {
      current_year: {
        revenue: currentYearRevenue,
        expenses: currentYearExpenses,
        profit: currentYearProfit,
        utilization: currentUtilization
      },
      next_year: {
        revenue: nextYearRevenue,
        expenses: nextYearExpenses,
        profit: nextYearProfit,
        utilization: nextYearUtilization
      },
      growth_rates: {
        revenue: revenueIncreasePct,
        expenses: -expenseReductionPct,
        profit: currentYearProfit !== 0 ? ((nextYearProfit - currentYearProfit) / currentYearProfit * 100) : 0,
        utilization: utilizationIncreasePct
      }
    }
  };
};



export const generateExcelReport = async (): Promise<Blob> => {
  try {
    const response = await api.get('/api/v1/insight/generate-excel-report', {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('Error generating Excel report:', error);
    throw error;
  }
};

// Add these functions to your existing api.ts file
export const generatePdfReport = async (): Promise<Blob> => {
  try {
    const response = await api.get('/api/v1/insight/generate-pdf-report', {
      responseType: 'blob' // Important for handling PDF files
    });
    return response.data;
  } catch (error) {
    console.error('Error generating PDF report:', error);
    throw error;
  }
};

export const sendEmailReport = async (): Promise<{status: string, message: string}> => {
  try {
    const response = await api.post('/api/v1/insight/send-email-report');
    return response.data;
  } catch (error) {
    console.error('Error sending email report:', error);
    throw error;
  }
};

export const saveFormData = async (data: FormData) => {
  try {
    const response = await api.post('/api/v1/insight/save-inputs', data);
    return response.data;
  } catch (error) {
    console.error('Error saving form data:', error);
    throw error;
  }
};



export const generateInsights = async (data: FormData) => {
  try {
    const response = await api.post<InsightData>('/api/v1/insight/generate-insights', data);
    return response.data;
  } catch (error) {
    console.error('Error generating insights:', error);
    throw error;
  }
};


export const getRecommendations = async () => {
  try {
    const response = await api.get<Recommendations>('/api/v1/insight/recommendations');
    return response.data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

export const uploadFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/v1/insight/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};


export const logoutUser = () => {
  try {
    // Remove stored tokens (localStorage, sessionStorage, or cookies)
    localStorage.removeItem('accessToken'); // or your token key
    localStorage.removeItem('refreshToken'); // if you have a refresh token
    // sessionStorage.removeItem('accessToken'); // if stored in sessionStorage

    // Redirect to login page
    window.location.href = '/login';
  } catch (error) {
    console.error('Error during logout:', error);
  }
};

export const getUserData = async (): Promise<{email: string, username?: string}> => {
  try {
    const response = await api.get('/api/v1/insight/user');
    return response.data;
  } catch (error) {
    console.error('Error getting user data:', error);
    throw error;
  }
};

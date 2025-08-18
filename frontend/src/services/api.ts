import axios from 'axios';
import type { FormData, InsightData, Recommendations } from '../types/simulatorTypes';

const API_URL = 'http://0.0.0.0:8000';

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

export const getUserData = async () => {
  try {
    const response = await axios.get<{email: string}>(`${API_URL}/user`);
    return response.data;
  } catch (error) {
    console.error('Error getting user data:', error);
    throw error;
  }
};
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Typography, 
  Button, 
  Statistic,
  Progress,
  Spin,
  Alert
} from 'antd';
import { 
  LineChart, 
  BarChart, 
  Bar, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import UserAvatar from './UserAvatar';
import { getProFormaDashboardData } from '../../services/api';

const { Title, Text } = Typography;

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{ 
        backgroundColor: '#fff', 
        padding: '10px', 
        border: '1px solid #ccc',
        borderRadius: '4px'
      }}>
        <p className="label">{`Month: ${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }}>
            {`${entry.name}: ${entry.value.toFixed(2)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const ProFormaDashboard: React.FC = () => {
  const { 
    userEmail, 
    setCurrentStep,
    formData,
    dashboardData,
    setDashboardData // Make sure this is included
  } = useSimulatorContext();
  
  // const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await getProFormaDashboardData(formData);
        setDashboardData(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [formData, setDashboardData]);

  useEffect(() => {
    console.log('ProFormaDashboard component mounted');
    return () => {
      console.log('ProFormaDashboard component unmounted');
    };
  }, []);

  // Update the useEffect to handle data fetching if not already available
  useEffect(() => {
    // If dashboard data is not available in context, try to fetch it
    if (!dashboardData) {
      const fetchData = async () => {
        try {
          setLoading(true);
          const data = await getProFormaDashboardData(formData);
          setDashboardData(data);
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Failed to load dashboard data');
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    } else {
      setLoading(false);
    }
  }, [dashboardData, formData, setDashboardData]);

  if (loading) {
    return (
      <div className="simulator-container">
        <Card className="simulator-header-card">
          <div className="header-content">
            <div>
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Center Operations Simulator
              </Title>
              <p style={{ margin: 0, color: '#666' }}>
                Pro Forma Financial Dashboard
              </p>
            </div>
            <UserAvatar email={userEmail} />
          </div>
        </Card>
        
        <Card className="simulator-card">
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="Loading dashboard data..." />
          </div>
        </Card>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="simulator-container">
        <Card className="simulator-header-card">
          <div className="header-content">
            <div>
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Center Operations Simulator
              </Title>
              <p style={{ margin: 0, color: '#666' }}>
                Pro Forma Financial Dashboard
              </p>
            </div>
            <UserAvatar email={userEmail} />
          </div>
        </Card>
        
        <Card className="simulator-card">
          <Alert
            message="Error Loading Dashboard"
            description={error || 'No data available'}
            type="error"
            showIcon
          />
          <Button 
            onClick={() => setCurrentStep(2)} 
            style={{ marginTop: '16px' }}
          >
            Back to Insights
          </Button>
        </Card>
      </div>
    );
  }

  // Prepare data for charts
  const { line_chart, bar_chart, goal_chart, summary } = dashboardData;

  return (
    <div className="simulator-container">
      <Card className="simulator-header-card">
        <div className="header-content">
          <div>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              Center Operations Simulator
            </Title>
            <p style={{ margin: 0, color: '#666' }}>
              Pro Forma Financial Dashboard
            </p>
          </div>
          <UserAvatar email={userEmail} />
        </div>
      </Card>

      <Card className="simulator-card">
        <Title level={3} style={{ marginBottom: '24px', color: '#1890ff' }}>
          Financial Projections & Goals
        </Title>

        {/* Summary Statistics */}
        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Current Year Revenue"
                value={summary.current_year.revenue}
                precision={2}
                valueStyle={{ color: '#3f8600' }}
                prefix="$"
                formatter={value => `${Number(value).toLocaleString()}`}
              />
              <Text type={summary.growth_rates.revenue >= 0 ? "success" : "danger"}>
                {summary.growth_rates.revenue >= 0 ? "+" : ""}{summary.growth_rates.revenue.toFixed(2)}%
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Current Year Expenses"
                value={summary.current_year.expenses}
                precision={2}
                valueStyle={{ color: '#cf1322' }}
                prefix="$"
                formatter={value => `${Number(value).toLocaleString()}`}
              />
              <Text type={summary.growth_rates.expenses <= 0 ? "success" : "danger"}>
                {summary.growth_rates.expenses >= 0 ? "+" : ""}{summary.growth_rates.expenses.toFixed(2)}%
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Current Year Profit"
                value={summary.current_year.profit}
                precision={2}
                valueStyle={{ color: summary.current_year.profit >= 0 ? '#3f8600' : '#cf1322' }}
                prefix="$"
                formatter={value => `${Number(value).toLocaleString()}`}
              />
              <Text type={summary.growth_rates.profit >= 0 ? "success" : "danger"}>
                {summary.growth_rates.profit >= 0 ? "+" : ""}{summary.growth_rates.profit.toFixed(2)}%
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Utilization Rate"
                value={summary.current_year.utilization}
                precision={2}
                valueStyle={{ color: '#1890ff' }}
                suffix="%"
              />
              <Text type={summary.growth_rates.utilization >= 0 ? "success" : "danger"}>
                {summary.growth_rates.utilization >= 0 ? "+" : ""}{summary.growth_rates.utilization.toFixed(2)}%
              </Text>
            </Card>
          </Col>
        </Row>

        {/* Line Chart */}
        <Card title="Monthly Trends (24 Months)" style={{ marginBottom: '24px' }}>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={line_chart} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                  name="Revenue ($)"
                />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="expenses" 
                  stroke="#ff7300" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                  name="Expenses ($)"
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="utilization" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                  name="Utilization (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Bar Chart */}
        <Card title="Yearly Comparison" style={{ marginBottom: '24px' }}>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bar_chart} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip formatter={(value) => [`${Number(value).toLocaleString()}`, '']} />
                <Legend />
                <Bar dataKey="revenue" fill="#82ca9d" name="Revenue ($)" />
                <Bar dataKey="expenses" fill="#ff7300" name="Expenses ($)" />
                <Bar dataKey="profit" fill="#8884d8" name="Profit ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Goal Progress Chart */}
        <Card title="Goal Progress" style={{ marginBottom: '24px' }}>
          <Row gutter={[24, 24]}>
            {goal_chart.map((goal: any, index: number) => (
              <Col xs={24} md={8} key={index}>
                <Card type="inner" title={goal.goal_type}>
                  <Progress
                    type="dashboard"
                    percent={goal.achieved_percentage}
                    format={percent => `${percent}%`}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                  <div style={{ textAlign: 'center', marginTop: '16px' }}>
                    <Text>Target: {goal.target_percentage}%</Text>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>

        {/* Action Buttons */}
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <Button onClick={() => setCurrentStep(2)}>
            Back to Insights
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default ProFormaDashboard;
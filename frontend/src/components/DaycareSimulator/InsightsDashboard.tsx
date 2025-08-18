import React, { useEffect, useState } from 'react';
import {
  Card, 
  Statistic, 
  Progress, 
  Row, 
  Col, 
  Typography, 
  Button,
  Alert,
  List,
  Spin
} from 'antd';
import { DownloadOutlined, MailOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import UserAvatar from './UserAvatar';

const { Title, Text } = Typography;

const InsightsDashboard: React.FC = () => {
  const {
    insights, 
    setCurrentStep,
    userEmail,
    fetchRecommendations
  } = useSimulatorContext();

   // Add this state to track if we're waiting for insights
  const [isLoading, setIsLoading] = useState(!insights);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Add this useEffect to handle the loading state
  useEffect(() => {
    if (!insights) {
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 3000); // Simulate loading delay
      
      return () => clearTimeout(timer);
    }
  }, [insights]);
  
  // Update the loading condition
  if (!insights || isLoading) {
    return (
      <div className="simulator-container">
        <Card className="simulator-header-card">
          <div className="header-content">
            <div>
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Center Operations Simulator
              </Title>
              <p style={{ margin: 0, color: '#666' }}>
                Simulation Results & Key Performance Indicators
              </p>
            </div>
            <UserAvatar email={userEmail} />
          </div>
        </Card>
        
        <Card className="simulator-card">
          <Title level={3} style={{ marginBottom: '24px', color: '#1890ff' }}>
            Insights
          </Title>
          
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="Generating insights...">
              <Alert
                message="Analysis in Progress"
                description="Our AI is analyzing your financial data. This may take a few moments."
                type="info"
              />
            </Spin>
          </div>
        </Card>
      </div>
    );
  }


  return (
    <div className="simulator-container">
      <Card className="simulator-header-card">
        <div className="header-content">
          <div>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              Center Operations Simulator
            </Title>
            <p style={{ margin: 0, color: '#666' }}>
              Simulation Results & Key Performance Indicators
            </p>
          </div>
          <UserAvatar email={userEmail} />
        </div>
      </Card>

      <Card className="simulator-card">
        <Title level={3} style={{ marginBottom: '24px', color: '#1890ff' }}>
          Insights
        </Title>

        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col xs={24} md={12} lg={6}>
            <Card>
              <Statistic
                title="Net Monthly Income"
                value={insights.net_monthly_income.value}
                precision={2}
                valueStyle={{ 
                  color: insights.net_monthly_income.value >= 0 ? '#3f8600' : '#cf1322',
                  fontWeight: 'bold'
                }}
                prefix="$"
              />
              <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
                {insights.net_monthly_income.note}
              </Text>
            </Card>
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Card>
              <Statistic
                title="Break-Even Enrollment"
                value={insights.break_even_enrollment.value}
                precision={0}
                suffix={insights.break_even_enrollment.unit}
                valueStyle={{ fontWeight: 'bold' }}
              />
              <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
                {insights.break_even_enrollment.note}
              </Text>
            </Card>
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Text strong style={{ marginBottom: '16px', display: 'block' }}>
                  Largest Expense
                </Text>
                <Progress
                  type="dashboard"
                  percent={insights.largest_expense.percentage_of_total_expenses}
                  format={() => (
                    <div>
                      <div>{insights.largest_expense.category}</div>
                      <div>{insights.largest_expense.percentage_of_total_expenses.toFixed(1)}%</div>
                    </div>
                  )}
                  strokeColor="#1890ff"
                  width={150}
                />
              </div>
            </Card>
          </Col>
          <Col xs={24} md={12} lg={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Text strong style={{ marginBottom: '16px', display: 'block' }}>
                  Capacity Utilization
                </Text>
                <Progress
                  type="dashboard"
                  percent={insights.capacity_utilization.value}
                  format={() => `${insights.capacity_utilization.value.toFixed(1)}%`}
                  status={insights.capacity_utilization.value > 85 ? 'success' : 'normal'}
                  strokeColor={insights.capacity_utilization.value > 85 ? '#52c41a' : '#1890ff'}
                  width={150}
                />
                <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
                  {insights.capacity_utilization.note}
                </Text>
              </div>
            </Card>
          </Col>
        </Row>

        <Card style={{ marginBottom: '24px' }}>
          <Title level={4} style={{ color: '#1890ff' }}>
            Executive Summary
          </Title>
          <div style={{ padding: '16px 0' }}>
            <p><Text strong>Financial Overview:</Text> {insights.executive_summary.financial_overview}</p>
            <p><Text strong>Profitability Status:</Text> {insights.executive_summary.profitability_status}</p>
            <p><Text strong>Enrollment Status:</Text> {insights.executive_summary.enrollment_status}</p>
            
            <Title level={5} style={{ marginTop: '16px', color: '#1890ff' }}>
              Recommendations:
            </Title>
            <List
              bordered
              dataSource={insights.executive_summary.recommendations}
              renderItem={item => <List.Item>{item}</List.Item>}
            />
          </div>
        </Card>

        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col span={24} md={12}>
            <Card title="Export Results">
              <Button 
                type="primary" 
                icon={<DownloadOutlined />} 
                style={{ marginRight: '16px', marginBottom: '16px' }}
                block
              >
                Download PDF Report
              </Button>
              <Button 
                icon={<MailOutlined />} 
                block
              >
                Send Report to My Email
              </Button>
            </Card>
          </Col>
          <Col span={24} md={12}>
            <Card title="Next Steps">
              <Button 
                type="primary" 
                icon={<ArrowRightOutlined />} 
                onClick={async () => {
                    // Fetch recommendations before navigating
                    await fetchRecommendations();
                    setCurrentStep(3)
                }}
                block
              >
                View Personalized Action Plan
              </Button>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default InsightsDashboard;
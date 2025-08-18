import React, { useEffect, useState } from 'react';
import { Card, Progress, Checkbox, Row, Col, Typography, Button, Alert, Spin } from 'antd';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import UserAvatar from './UserAvatar';
import { getRecommendations } from '../../services/api';
import { ReloadOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const NextSteps: React.FC = () => {
  const {
    recommendations, 
    setRecommendations,
    setCurrentStep,
    userEmail,
    fetchRecommendations
  } = useSimulatorContext();
  const [checkedItems, setCheckedItems] = useState<boolean[]>([]);

  // Load recommendations if not already loaded
  // Initialize checked items when recommendations are set
  useEffect(() => {
    if (recommendations) {
      setCheckedItems(new Array(recommendations.recommendations.length).fill(false));
    }
  }, [recommendations]);

  // Load recommendations if not already loaded
  useEffect(() => {
    if (!recommendations) {
      fetchRecommendations();
    }
  }, [recommendations, fetchRecommendations]);

  const handleCheck = (index: number) => {
    const newCheckedItems = [...checkedItems];
    newCheckedItems[index] = !newCheckedItems[index];
    setCheckedItems(newCheckedItems);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchRecommendations();
    } finally {
      setRefreshing(false);
    }
  };

  const completedCount = checkedItems.filter(Boolean).length;
  const totalCount = recommendations?.recommendations.length || 0;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="simulator-container">
      <Card className="simulator-header-card">
        <div className="header-content">
          <div>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              Center Operations Simulator
            </Title>
            <p style={{ margin: 0, color: '#666' }}>
              Personalized Action Plan for Improvement
            </p>
          </div>
          <UserAvatar email={userEmail} />
        </div>
      </Card>

      <Card className="simulator-card">
        <Title level={3} style={{ marginBottom: '24px', color: '#1890ff' }}>
          Next Steps
        </Title>

        <Card style={{ marginBottom: '24px' }}>
          <Title level={4} style={{ color: '#1890ff' }}>
            Personalized Action Plan
          </Title>
          {/* <Button 
              icon={<ReloadOutlined />} 
              loading={refreshing}
              onClick={handleRefresh}
              size="small"
            >
              Refresh
            </Button> */}
          <Text>
            Based on your simulation results, here are targeted recommendations to improve your center's performance
          </Text>
{/* 
          {loading ? (
            <Alert
              message="Loading recommendations..."
              type="info"
              showIcon
              style={{ marginTop: '24px' }}
            />
          ) : (
            <div style={{ marginTop: '24px' }}>
              {recommendations?.recommendations.map((rec, index) => (
                <div key={index} className="recommendation-item">
                  <Checkbox 
                    checked={checkedItems[index]} 
                    onChange={() => handleCheck(index)}
                  />
                  <Text style={{ marginLeft: '16px' }}>{rec}</Text>
                </div>
              ))}
            </div>
          )} */}

          {!recommendations ? (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <Spin tip="Loading recommendations..." />
            </div>
          ) : (
            <div style={{ marginTop: '24px' }}>
              {recommendations.recommendations.map((rec, index) => (
                <div key={index} className="recommendation-item">
                  <Checkbox 
                    checked={checkedItems[index]} 
                    onChange={() => handleCheck(index)}
                  />
                  <Text style={{ marginLeft: '16px' }}>{rec}</Text>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <Title level={4} style={{ color: '#1890ff' }}>
            Your Progress
          </Title>
          
          <Progress 
            percent={progress} 
            status={progress === 100 ? 'success' : 'active'} 
            strokeColor={progress === 100 ? '#52c41a' : '#1890ff'}
            style={{ margin: '24px 0' }}
          />
          
          {progress === 100 ? (
            <Alert
              message="Excellent Performance!"
              description="Your center simulation shows strong financial health with no immediate action items. Keep monitoring your metrics and consider growth opportunities."
              type="success"
              showIcon
            />
          ) : progress > 75 ? (
            <Alert
              message="Great Progress!"
              description="You're well on your way to optimizing your daycare center operations. Complete the remaining items to maximize your potential."
              type="info"
              showIcon
            />
          ) : (
            <Alert
              message="Getting Started"
              description="Begin implementing these recommendations to improve your center's financial health and operational efficiency."
              type="info"
              showIcon
            />
          )}

          <div className="action-buttons" style={{ marginTop: '24px' }}>
            <Button onClick={() => setCurrentStep(1)}>
              Back to Inputs
            </Button>
            <Button 
              type="primary" 
              onClick={() => setCurrentStep(2)}
              style={{ marginLeft: '16px' }}
            >
              View Insights
            </Button>
          </div>
        </Card>
      </Card>
    </div>
  );
};

export default NextSteps;

function setRefreshing(arg0: boolean) {
    throw new Error('Function not implemented.');
}

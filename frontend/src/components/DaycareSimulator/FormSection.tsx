import React from 'react';
import { 
  Row, 
  Col, 
  Input, 
  InputNumber, 
  Button, 
  Tooltip, 
  Select,
  Upload,
  message,
  Form
} from 'antd';
import { 
  PlusOutlined, 
  MinusOutlined, 
  InfoCircleOutlined,
  UploadOutlined
} from '@ant-design/icons';
import { RevenueSource, ExpenseItem, Classroom, BusinessGoal } from '../../types/simulatorTypes';

const { Option } = Select;

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const FormSection: React.FC<FormSectionProps> = ({ title, description, children }) => {
  return (
    <div className="form-section">
      <div className="section-header">
        <h3>{title}</h3>
        {description && (
          <Tooltip title={description}>
            <InfoCircleOutlined style={{ color: '#1890ff', marginLeft: '8px' }} />
          </Tooltip>
        )}
      </div>
      {children}
    </div>
  );
};

interface RevenueSourcesProps {
  sources: RevenueSource[];
  onAdd: () => void;
  onChange: (id: string, field: keyof RevenueSource, value: any) => void;
  onRemove: (id: string) => void;
}

export const RevenueSources: React.FC<RevenueSourcesProps> = ({ 
  sources, 
  onAdd, 
  onChange, 
  onRemove 
}) => (
    <>
    {sources.length === 0 ? (
      <div style={{ textAlign: 'center', margin: '16px 0' }}>
        <Button 
          type="dashed" 
          onClick={onAdd} 
          icon={<PlusOutlined />}
        >
          Add First Revenue Source
        </Button>
      </div>
    ) : (
    <>
    {sources.map((source) => (
      <Row gutter={16} key={source.id} className="form-row">
        <Col span={8}>
          <Form.Item 
          label="Source Name" 
          labelCol={{ span: 24 }} 
          wrapperCol={{ span: 24 }} 
          rules={[{ 
              required: true, 
              message: 'Please input your expense source name!' 
            }
          ]}>
            <Input
              placeholder="e.g. Tuition"
              value={source.sourceName}
              onChange={(e) => onChange(source.id, 'sourceName', e.target.value)}
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Monthly Amount ($)" 
          labelCol={{ span: 24 }} 
          wrapperCol={{ span: 24 }}
          rules={[{ 
              required: true, 
              message: 'Please input your monthly amount!' 
            }
          ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0"
              value={source.monthlyAmount}
              onChange={(value) => onChange(source.id, 'monthlyAmount', value)}
              min={0}
              addonBefore="$"
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Tag/Note" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <Input
              placeholder="Tag/Note"
              value={source.tag}
              onChange={(e) => onChange(source.id, 'tag', e.target.value)}
            />
          </Form.Item>
        </Col>
        <Col span={4}>
          <Button 
            danger 
            icon={<MinusOutlined />} 
            onClick={() => onRemove(source.id)}
            disabled={sources.length <= 1}
          />
        </Col>
      </Row>
    ))}
    <Button 
      type="dashed" 
      onClick={onAdd} 
      icon={<PlusOutlined />}
      className="add-button"
    >
      Add Revenue Source
    </Button>
     </>
    )}
  </>
);

interface ExpenseItemsProps {
  expenses: ExpenseItem[];
  onAdd: () => void;
  onChange: (id: string, field: keyof ExpenseItem, value: any) => void;
  onRemove: (id: string) => void;
  showHours?: boolean;
  category?: string; // Add category to customize labels
}

export const ExpenseItems: React.FC<ExpenseItemsProps> = ({
  expenses, 
  onAdd, 
  onChange, 
  onRemove,
  showHours = false,
  category
}) => {
  // Get appropriate labels based on category
  const getLabels = () => {
    switch(category) {
      case 'employees':
        return {
          expenseName: 'Role/Position',
          hoursPerMonth: 'Hours/Month',
          monthlyAmount: 'Monthly Amount ($)',
          type: 'Billing Frequency'
        };
      case 'facilities':
        return {
          expenseName: 'Facility Item',
          monthlyAmount: 'Monthly Amount ($)',
          type: 'Billing Frequency'
        };
      case 'administrative':
        return {
          expenseName: 'Administrative Item',
          monthlyAmount: 'Monthly Amount ($)',
          type: 'Billing Frequency'
        };
      case 'supplies':
        return {
          expenseName: 'Supply Item',
          monthlyAmount: 'Monthly Amount ($)',
          type: 'Billing Frequency'
        };
      default:
        return {
          expenseName: 'Expense Name',
          monthlyAmount: 'Monthly Amount ($)',
          type: 'Type'
        };
    }
  };

  const labels = getLabels();

  return (
    <>
      {expenses.map((expense) => (
        <Row gutter={16} key={expense.id} className="form-row">
          <Col span={showHours ? 6 : 8}>
            <Form.Item label={labels.expenseName} labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
              <Input
                placeholder={category === 'employees' ? 'e.g. Teacher' : 'e.g. Rent'}
                value={expense.expenseName}
                onChange={(e) => onChange(expense.id, 'expenseName', e.target.value)}
              />
            </Form.Item>
          </Col>
          {showHours && (
            <Col span={6}>
              <Form.Item label={labels.hoursPerMonth} labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="0"
                  value={expense.hoursPerMonth}
                  onChange={(value) => onChange(expense.id, 'hoursPerMonth', value)}
                  min={0}
                />
              </Form.Item>
            </Col>
          )}
          <Col span={6}>
            <Form.Item label={labels.monthlyAmount} labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
              <InputNumber
                style={{ width: '100%' }}
                placeholder="0.00"
                value={expense.monthlyAmount}
                onChange={(value) => onChange(expense.id, 'monthlyAmount', value)}
                min={0}
                // formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                // parser={value => value ? parseFloat(value.replace(/\$\s?|(,*)/g, '')) : 0}
              />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item label={labels.type} labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
              <Select
                style={{ width: '100%' }}
                value={expense.type}
                onChange={(value) => onChange(expense.id, 'type', value)}
              >
                <Option value="Monthly">Monthly</Option>
                <Option value="Hourly">Hourly</Option>
                <Option value="Daily">Daily</Option>
                <Option value="Yearly">Yearly</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={2}>
            <Button 
              danger 
              icon={<MinusOutlined />} 
              onClick={() => onRemove(expense.id)}
              style={{ marginTop: '30px' }}
            />
          </Col>
        </Row>
      ))}
      <Button 
        type="dashed" 
        onClick={onAdd} 
        icon={<PlusOutlined />}
        className="add-button"
      >
        Add {(category ? category.charAt(0).toUpperCase() + category.slice(1) : 'General')} Expense
      </Button>
    </>
  );
};

interface ClassroomsProps {
  classrooms: Classroom[];
  onAdd: () => void;
  onChange: (id: string, field: keyof Classroom, value: any) => void;
  onRemove: (id: string) => void;
}

export const Classrooms: React.FC<ClassroomsProps> = ({ 
  classrooms, 
  onAdd, 
  onChange, 
  onRemove 
}) => (
  <>
    {classrooms.map((classroom) => (
      <Row gutter={16} key={classroom.id} className="form-row">
        <Col span={6}>
          <Form.Item label="Classroom Name" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <Input
              placeholder="e.g. Toddler Room"
              value={classroom.name}
              onChange={(e) => onChange(classroom.id, 'name', e.target.value)}
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Capacity" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0"
              value={classroom.capacity}
              onChange={(value) => onChange(classroom.id, 'capacity', value)}
              min={0}
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Teacher Ratio" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0.0"
              value={classroom.ratio}
              onChange={(value) => onChange(classroom.id, 'ratio', value)}
              min={0}
              step={0.1}
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Avg Students" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0"
              value={classroom.avgStudents}
              onChange={(value) => onChange(classroom.id, 'avgStudents', value)}
              min={0}
            />
          </Form.Item>
        </Col>
        <Col span={24} style={{ textAlign: 'right', marginTop: '8px' }}>
          <Button 
            danger 
            onClick={() => onRemove(classroom.id)}
            disabled={classrooms.length <= 1}
          >
            Remove Classroom
          </Button>
        </Col>
      </Row>
    ))}
    <Button 
      type="dashed" 
      onClick={onAdd} 
      icon={<PlusOutlined />}
      className="add-button"
    >
      Add Classroom
    </Button>
  </>
);

interface BusinessGoalsProps {
  goals: BusinessGoal[];
  onAdd: () => void;
  onChange: (id: string, field: keyof BusinessGoal, value: any) => void;
  onRemove: (id: string) => void;
}

export const BusinessGoals: React.FC<BusinessGoalsProps> = ({ 
  goals, 
  onAdd, 
  onChange, 
  onRemove 
}) => (
  <>
    {goals.map((goal) => (
      <Row gutter={16} key={goal.id} className="form-row">
        <Col span={16}>
          <Form.Item label="Business Goal" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <Input
              placeholder="e.g., Increase Enrollment"
              value={goal.goal}
              onChange={(e) => onChange(goal.id, 'goal', e.target.value)}
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="Target (%)" labelCol={{ span: 24 }} wrapperCol={{ span: 24 }}>
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0"
              value={goal.targetPercentage}
              onChange={(value) => onChange(goal.id, 'targetPercentage', value)}
              min={0}
              max={100}
            />
          </Form.Item>
        </Col>
        <Col span={2}>
          <Button 
            danger 
            icon={<MinusOutlined />} 
            onClick={() => onRemove(goal.id)}
            style={{ marginTop: '30px' }}
          />
        </Col>
      </Row>
    ))}
    <Button 
      type="dashed" 
      onClick={onAdd} 
      icon={<PlusOutlined />}
      className="add-button"
    >
      Add Goal
    </Button>
  </>
);

interface FileUploadProps {
  file: File | null;
  onUpload: (file: File) => void;
  onRemove: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ file, onUpload, onRemove }) => {
  const beforeUpload = (file: File) => {
    if (file.type !== 'application/pdf') {
      message.error('You can only upload PDF files!');
      return false;
    }
    onUpload(file);
    return false;
  };

  return (
    <div className="file-upload-container">
      {file ? (
        <div className="file-preview">
          <span>{file.name}</span>
          <Button type="link" danger onClick={onRemove}>
            Remove
          </Button>
        </div>
      ) : (
        <Upload
          beforeUpload={beforeUpload}
          showUploadList={false}
          accept=".pdf"
        >
          <Button icon={<UploadOutlined />}>Upload PDF File</Button>
        </Upload>
      )}
    </div>
  );
};
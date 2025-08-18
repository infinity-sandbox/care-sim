import React, { useState } from 'react';
import { Avatar, Dropdown, Menu, Button } from 'antd';
import { LogoutOutlined } from '@ant-design/icons';
import { logoutUser } from '../../services/api';

interface UserAvatarProps {
  email: string;
}

const UserAvatar: React.FC<UserAvatarProps> = ({ email }) => {
  const [visible, setVisible] = useState(false);
  
  const handleLogout = async () => {
    try {
      await logoutUser();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const menu = (
    <Menu>
      <Menu.Item key="logout" onClick={handleLogout} icon={<LogoutOutlined />}>
        Logout
      </Menu.Item>
    </Menu>
  );

  return (
    <Dropdown 
      overlay={menu} 
      trigger={['click']}
      visible={visible}
      onVisibleChange={setVisible}
      placement="bottomRight"
    >
      <Avatar 
        style={{ 
          backgroundColor: '#1890ff', 
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '18px'
        }}
      >
        {email.charAt(0).toUpperCase()}
      </Avatar>
    </Dropdown>
  );
};

export default UserAvatar;
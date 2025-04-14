import React from 'react';
import { Result, Button } from 'antd';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <Result
      status="404"
      title="404"
      subTitle="죄송합니다. 요청하신 페이지를 찾을 수 없습니다."
      extra={
        <Link to="/">
          <Button type="primary">홈으로 돌아가기</Button>
        </Link>
      }
    />
  );
};

export default NotFound; 
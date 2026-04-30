import React, { useState, useEffect } from 'react';
import { Card, Button, Progress, Avatar } from 'antd';
import { CameraOutlined, BulbOutlined, ShoppingCartOutlined, SyncOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getClosetStats, getDailyRecommendation } from '../services/clothingService';

const HomePage = () => {
  const [stats, setStats] = useState({
    totalItems: 0,
    unusedItems: 0,
    favoriteOutfits: 0,
    recommendationAccuracy: 0
  });
  const [dailyRecommendation, setDailyRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsData, recommendation] = await Promise.all([
          getClosetStats(),
          getDailyRecommendation()
        ]);
        setStats(statsData);
        setDailyRecommendation(recommendation);
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleAddClothing = () => {
    navigate('/add-clothing');
  };

  const handleGenerateOutfit = () => {
    navigate('/outfit-generator');
  };

  const handleShoppingRecommendation = () => {
    navigate('/recommendations');
  };

  const handleRefreshRecommendation = async () => {
    setLoading(true);
    try {
      const recommendation = await getDailyRecommendation();
      setDailyRecommendation(recommendation);
    } catch (error) {
      console.error('刷新推荐失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 欢迎卡片 */}
        <div className="mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar size={64} icon={<CameraOutlined />} className="bg-blue-100 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">你好，时尚达人！👋</h1>
                <p className="text-gray-600 mt-1">今天是 {new Date().toLocaleDateString('zh-CN', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}</p>
              </div>
            </div>
            <Button 
              type="primary" 
              size="large" 
              icon={<CameraOutlined />}
              onClick={handleAddClothing}
              className="bg-blue-600 hover:bg-blue-700"
            >
              添加衣物
            </Button>
          </div>
        </div>

        {/* 数据统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="总衣物数"
            value={stats.totalItems}
            icon={<CameraOutlined className="text-blue-500 text-2xl" />}
            color="bg-blue-50"
          />
          <StatCard
            title="闲置衣物"
            value={stats.unusedItems}
            icon={<SyncOutlined className="text-yellow-500 text-2xl" />}
            color="bg-yellow-50"
            warning={stats.unusedItems > 10}
          />
          <StatCard
            title="收藏搭配"
            value={stats.favoriteOutfits}
            icon={<BulbOutlined className="text-green-500 text-2xl" />}
            color="bg-green-50"
          />
          <StatCard
            title="推荐准确率"
            value={`${stats.recommendationAccuracy}%`}
            icon={<ShoppingCartOutlined className="text-purple-500 text-2xl" />}
            color="bg-purple-50"
          />
        </div>

        {/* 今日推荐卡片 */}
        <div className="mb-8">
          <Card 
            title={
              <div className="flex items-center justify-between">
                <span className="text-xl font-bold text-gray-900">今日穿搭推荐</span>
                <Button 
                  type="text" 
                  icon={<SyncOutlined spin={loading} />} 
                  onClick={handleRefreshRecommendation}
                >
                  刷新
                </Button>
              </div>
            }
            className="rounded-2xl shadow-lg border-blue-100"
          >
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <SyncOutlined spin className="text-3xl text-blue-500" />
              </div>
            ) : dailyRecommendation ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-xl">
                    <h3 className="font-bold text-lg mb-2 text-blue-800">推荐理由</h3>
                    <p className="text-gray-700">{dailyRecommendation.reason}</p>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-xl">
                    <h3 className="font-bold text-lg mb-2 text-green-800">天气适应</h3>
                    <p className="text-gray-700">
                      {dailyRecommendation.weather.temp}°C, {dailyRecommendation.weather.condition}
                    </p>
                  </div>
                  
                  <div className="bg-purple-50 p-4 rounded-xl">
                    <h3 className="font-bold text-lg mb-2 text-purple-800">搭配评分</h3>
                    <Progress 
                      percent={dailyRecommendation.score} 
                      status={dailyRecommendation.score > 80 ? 'success' : 'normal'}
                      strokeColor={dailyRecommendation.score > 80 ? '#108ee9' : '#faad14'}
                    />
                  </div>
                </div>
                
                <div className="flex justify-center items-center">
                  <div className="bg-gray-100 rounded-xl p-4 w-full h-64 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-5xl mb-4">👕👖👟</div>
                      <p className="text-gray-600">搭配预览加载中...</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500 mb-4">暂无今日推荐，请先添加一些衣物</p>
                <Button 
                  type="primary" 
                  onClick={handleAddClothing}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  开始添加衣物
                </Button>
              </div>
            )}
          </Card>
        </div>

        {/* 快捷操作卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ActionCard
            title="智能搭配"
            description="根据天气、场合自动生成3套专业搭配"
            icon={<BulbOutlined className="text-blue-500 text-3xl" />}
            onClick={handleGenerateOutfit}
            color="bg-blue-50 border-blue-200"
          />
          
          <ActionCard
            title="购物推荐"
            description="根据搭配缺口推荐高性价比单品"
            icon={<ShoppingCartOutlined className="text-green-500 text-3xl" />}
            onClick={handleShoppingRecommendation}
            color="bg-green-50 border-green-200"
          />
          
          <ActionCard
            title="衣柜分析"
            description="智能分析衣柜利用率，优化购物决策"
            icon={<SyncOutlined className="text-purple-500 text-3xl" />}
            onClick={() => navigate('/closet-analysis')}
            color="bg-purple-50 border-purple-200"
          />
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color, warning = false }) => (
  <Card className={`rounded-2xl shadow-md ${color} ${warning ? 'border-yellow-300' : 'border-gray-200'}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-500 text-sm mb-1">{title}</p>
        <p className={`text-2xl font-bold ${warning ? 'text-yellow-600' : 'text-gray-900'}`}>
          {value}
        </p>
      </div>
      <div className="p-3 bg-white rounded-lg shadow-sm">
        {icon}
      </div>
    </div>
  </Card>
);

const ActionCard = ({ title, description, icon, onClick, color }) => (
  <Card 
    hoverable 
    onClick={onClick}
    className={`rounded-2xl shadow-md cursor-pointer transition-all hover:shadow-lg ${color}`}
  >
    <div className="flex items-center space-x-4 p-4">
      <div className="p-3 bg-white rounded-lg shadow-sm">
        {icon}
      </div>
      <div>
        <h3 className="font-bold text-lg text-gray-900">{title}</h3>
        <p className="text-gray-600 mt-1">{description}</p>
      </div>
    </div>
  </Card>
);

export default HomePage;

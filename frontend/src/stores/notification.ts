import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Component } from 'vue';

// 通知类型
export type NotificationType = 'success' | 'warning' | 'error' | 'info';

// 通知项接口
export interface NotificationItem {
  id: string;
  title: string;
  content: string;
  type: NotificationType;
  time: string;
  read: boolean;
  source?: string; // 来源：API错误、系统错误等
  details?: string; // 详细错误信息
}

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// 格式化时间
const formatTime = (date: Date) => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return `${Math.floor(diff / 86400000)}天前`;
};

export const useNotificationStore = defineStore('notification', () => {
  // 通知列表
  const notifications = ref<NotificationItem[]>([]);
  
  // 最大存储数量
  const MAX_NOTIFICATIONS = 50;
  
  // 从localStorage加载
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('notifications');
      if (stored) {
        notifications.value = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load notifications:', e);
    }
  };
  
  // 保存到localStorage
  const saveToStorage = () => {
    try {
      localStorage.setItem('notifications', JSON.stringify(notifications.value.slice(0, MAX_NOTIFICATIONS)));
    } catch (e) {
      console.error('Failed to save notifications:', e);
    }
  };
  
  // 未读数量
  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length;
  });
  
  // 添加通知
  const addNotification = (notification: Omit<NotificationItem, 'id' | 'time'>) => {
    const newNotification: NotificationItem = {
      ...notification,
      id: generateId(),
      time: formatTime(new Date())
    };
    
    notifications.value.unshift(newNotification);
    
    // 限制数量
    if (notifications.value.length > MAX_NOTIFICATIONS) {
      notifications.value = notifications.value.slice(0, MAX_NOTIFICATIONS);
    }
    
    saveToStorage();
    return newNotification.id;
  };
  
  // 添加错误通知
  const addError = (title: string, content: string, details?: string, source?: string) => {
    return addNotification({
      title,
      content,
      type: 'error',
      read: false,
      source: source || '系统',
      details
    });
  };
  
  // 添加成功通知
  const addSuccess = (title: string, content: string) => {
    return addNotification({
      title,
      content,
      type: 'success',
      read: false
    });
  };
  
  // 添加警告通知
  const addWarning = (title: string, content: string, source?: string) => {
    return addNotification({
      title,
      content,
      type: 'warning',
      read: false,
      source
    });
  };
  
  // 添加信息通知
  const addInfo = (title: string, content: string) => {
    return addNotification({
      title,
      content,
      type: 'info',
      read: false
    });
  };
  
  // 标记为已读
  const markAsRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id);
    if (notification) {
      notification.read = true;
      saveToStorage();
    }
  };
  
  // 标记所有为已读
  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true);
    saveToStorage();
  };
  
  // 删除通知
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) {
      notifications.value.splice(index, 1);
      saveToStorage();
    }
  };
  
  // 清空所有通知
  const clearAll = () => {
    notifications.value = [];
    saveToStorage();
  };
  
  // 获取图标
  const getNotificationIcon = (type: NotificationType): string => {
    const iconMap: Record<NotificationType, string> = {
      success: 'SuccessFilled',
      warning: 'WarningFilled',
      error: 'CircleCloseFilled',
      info: 'InfoFilled'
    };
    return iconMap[type];
  };
  
  // 初始化时加载
  loadFromStorage();
  
  return {
    notifications,
    unreadCount,
    addNotification,
    addError,
    addSuccess,
    addWarning,
    addInfo,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    getNotificationIcon
  };
});

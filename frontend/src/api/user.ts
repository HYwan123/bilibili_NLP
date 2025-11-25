import request from '@/utils/request';
import type { LoginData, RegisterData } from './types';

export const login = (data: LoginData) => {
  return request({
    method: 'POST',
    url: '/user/login',
    data
  });
};

export const register = (data: RegisterData) => {
  return request({
    method: 'POST',
    url: '/user/register',
    data
  });
};

export const getUserProfile = () => {
  return request({
    method: 'GET',
    url: '/user/profile'
  });
};

export const updateUserProfile = (profileData: any) => {
  return request({
    method: 'POST',
    url: '/user/profile',
    data: profileData
  });
};

export const getUserProfileById = (userId: number) => {
  return request({
    method: 'GET',
    url: `/user/profile/${userId}`
  });
}; 
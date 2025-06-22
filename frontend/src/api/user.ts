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
export interface BaseResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface UserComment {
  comment_text: string;
}

export interface UserCommentsResponse {
  uid: number;
  comment_count: number;
  comments: UserComment[];
} 
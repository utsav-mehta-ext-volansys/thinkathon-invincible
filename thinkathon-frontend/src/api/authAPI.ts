import axios from 'axios';
import {UserCreate,UserLogin} from "@/interface/AuthInterface"

const API_BASE_URL = 'http://localhost:8000'; // update if different

export const signup = async (body:UserCreate) => {
  const response = await axios.post(`${API_BASE_URL}/api/auth/signup`,body);
  return response.data;
};

export const login = async (body:UserLogin) => {
  const response = await axios.post(`${API_BASE_URL}/api/auth/login`, body);
  return response.data;
};

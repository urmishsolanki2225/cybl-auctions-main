// src/components/ToastProvider.js
import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Helper function to show toast anywhere
export const showToast = (message, type = 'success') => {
  switch(type) {
    case 'error':
      toast.error(message);
      break;
    case 'info':
      toast.info(message);
      break;
    case 'warning':
      toast.warn(message);
      break;
    default:
      toast.success(message);
      break;
  }
};

const ToastProvider = () => {
  return (
    <ToastContainer
      position="top-right"
      autoClose={3000}
      hideProgressBar={false}
      newestOnTop={false}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="colored"
    />
  );
};

export default ToastProvider;
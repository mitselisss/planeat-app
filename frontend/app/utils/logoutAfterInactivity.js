import React, { useState, useEffect } from 'react';
import { useNavigate } from '@remix-run/react';
import { getDecodedToken } from 'utils/tokenUtils';

const LogoutAfterInactivity = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    const checkForInactivity = () => {
        const expireTime = localStorage.getItem('expireTime');

        if (expireTime < Date.now()) {
            Logout();
        }
    };

    const updateExpireTime = () => {
        const expireTime = Date.now() + 43200000;
        localStorage.setItem('expireTime', expireTime);
    };

    useEffect(() => {
        const interval = setInterval(() => {
            checkForInactivity();
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        updateExpireTime();

        window.addEventListener('click', updateExpireTime);
        window.addEventListener('keypress', updateExpireTime);
        window.addEventListener('scroll', updateExpireTime);
        window.addEventListener('mousemove', updateExpireTime);

        return () => {
            window.addEventListener('click', updateExpireTime);
            window.addEventListener('keypress', updateExpireTime);
            window.addEventListener('scroll', updateExpireTime);
            window.addEventListener('mousemove', updateExpireTime);
        };
    }, []);

    const Logout = async () => {
        localStorage.removeItem('token');
        localStorage.removeItem('expireTime');
        localStorage.remove('shoppingList');
        navigate('/pages/login');
    };
    return null;
};

export default LogoutAfterInactivity;

import { jwtDecode } from 'jwt-decode';

export const getDecodedToken = () => {
    if (typeof window === 'undefined' || !window.localStorage) {
        // Return null if not in a browser environment
        return null;
    }

    const token = localStorage.getItem('token');
    if (!token) return null;

    try {
        return jwtDecode(token);
    } catch {
        return null;
    }
};

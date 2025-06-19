// project imports
import { useEffect } from 'react';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';

// export meta
export const meta = () => ({
    title: 'PLANEAT'
});

// ==============================|| DAFAULT PAGE ||============================== //

export default function Index() {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    useEffect(() => {
        if (!decodedToken || Object.keys(decodedToken).length === 0) {
            navigate('/pages/login');
        } else {
            navigate('/meal-plan');
        }
    }, []);
}

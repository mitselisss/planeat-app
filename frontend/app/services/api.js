import axios from 'axios';

const BASE_URL = 'http://195.251.117.56:7000/api';
// const BASE_URL = 'http://127.0.0.1:8000/api';

// --- Login - Register - Create User Profile --- //

export const login = async (email, password) => {
    try {
        const response = await axios.post(`${BASE_URL}/login`, {
            email: email,
            password: password
        });
        return response;
    } catch (error) {
        throw error;
    }
};

export const register = async (username, email, password) => {
    try {
        const response = await axios.post(`${BASE_URL}/register`, {
            username: username,
            email: email,
            password: password
        });
        return response;
    } catch (error) {
        throw error;
    }
};

export const forgotPassword = async (email) => {
    try {
        const response = await axios.post(`${BASE_URL}/resetPasswordEmail/${email}`);
        return response;
    } catch (error) {
        throw error;
    }
};

export const newPassword = async (token, password) => {
    try {
        const response = await axios.post(`${BASE_URL}/resetPassword/${token}`, {
            password: password
        });
        return response;
    } catch (error) {
        throw error;
    }
};

export const createUserPro = async (token_id, formData) => {
    try {
        const response = await axios.post(`${BASE_URL}/${token_id}/create_profile`, {
            role: formData.role,
            country: formData.country,
            sex: formData.sex,
            yob: formData.yob,
            height: formData.height,
            weight: formData.weight,
            PAL: formData.PAL,
            target_weight: formData.target_weight,
            goal: formData.goal,
            targetGoal: formData.targetGoal,
            allergies: formData.allergies,
            dietaryPreferences: formData.dietaryPreferences,
            selectedCuisines: formData.selectedCuisines
        });
        return response;
    } catch (error) {
        throw error;
    }
};

// -------------- User Actions --------------------- //

export const userActions = async (token_id, action) => {
    try {
        const response = await axios.post(`${BASE_URL}/user_actions`, {
            user_id: token_id,
            action: action
        });
        return response;
    } catch (error) {
        throw error;
    }
};

// -------------- Meals.js --------------------- //

export const fetchWeeklyNP = async (userId, monday, sunday) => {
    try {
        const response = await axios.get(`${BASE_URL}/check_weekly_np/${userId}/${monday}/${sunday}`);
        return response;
    } catch (error) {
        throw error;
    }
};

export const fetchUserWeeks = async (userId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_user_weeks/${userId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchWeeklyNPs = async (userId, week) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_weekly_np/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchDailyNP = async (userId, week, day) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_daily_np/${userId}/${week}/${day}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const createNPs = async (userId, monday, sunday) => {
    try {
        const response = await axios.get(`${BASE_URL}/create_nps/${userId}/${monday}/${sunday}`);
        return response;
    } catch (error) {
        throw error;
    }
};

export const updateCurrentWeekNPs = async (userId, monday, sunday) => {
    try {
        const response = await axios.put(`${BASE_URL}/update_current_week_nps/${userId}/${monday}/${sunday}`);
        return response;
    } catch (error) {
        throw error;
    }
};

// -------------- Dishes.js --------------------- //

export const fetchMealInfo = async (mealId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_meal_info/${mealId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchDishesInfo = async (mealId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_dishes_info/${mealId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// -------------- Analytics --------------------- //

export const fetchNPsAnalytics = async (userId, week) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_nutritional_info/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchNPsFoodCategoriesWeekly = async (userId, week, day) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_weekly_food_categories/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchNPsFoodCategories = async (userId, week, day) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_daily_food_categories/${userId}/${week}/${day}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchNPsUserFoodCategoriesWeekly = async (userId, week, day) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_weekly_food_user_goal_categories/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const fetchNPsUserFoodCategories = async (userId, week, day) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_daily_food_user_goal_categories/${userId}/${week}/${day}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// -------------- userProfile --------------------- //

export const getUserProfile = async (userId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_user_profile/${userId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const updateUserProfile = async (userId, formData) => {
    try {
        const response = await axios.put(`${BASE_URL}/update_user_profile/${userId}`, formData);
        return response;
    } catch (error) {
        throw error;
    }
};

export const updateUserMainScreen = async (userId, mainScreenValue) => {
    try {
        const response = await axios.put(`${BASE_URL}/update_user_main_screen/${userId}`, { main_screen: mainScreenValue });
        return response.data; // or just `response` if you prefer full response
    } catch (error) {
        throw error;
    }
};

// -------------- Shopping List --------------------- //

export const getShoppingList = async (userId, week) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_shopping_list/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getShoppingListIngredients = async (userId, week) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_shopping_list_ingredients/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const addShoppingList = async (userId, week, data) => {
    try {
        const response = await axios.put(`${BASE_URL}/add_to_shopping_list/${userId}/${week}`, data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const removeShoppingList = async (userId, week, data) => {
    try {
        const response = await axios.put(`${BASE_URL}/remove_from_shopping_list/${userId}/${week}`, data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// -------------- Eaten List --------------------- //

export const getEatenList = async (userId, week) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_check_eaten_list/${userId}/${week}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const addEatenList = async (userId, week, data) => {
    try {
        const response = await axios.put(`${BASE_URL}/add_to_check_eaten_list/${userId}/${week}`, data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const removeEatenList = async (userId, week, data) => {
    try {
        const response = await axios.put(`${BASE_URL}/remove_from_check_eaten_list/${userId}/${week}`, data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// -------------- Achievments --------------------- //

export const getUserAchievments = async (userId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_user_achievements/${userId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getUserActionAchievments = async (userId) => {
    try {
        const response = await axios.get(`${BASE_URL}/get_user_action_achievements/${userId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// -------------- Feedback --------------------- //

export const userFeedback = async (userId, feedbackText) => {
    try {
        const response = await axios.post(`${BASE_URL}/feedback/${userId}`, { feedback: feedbackText });
        return response;
    } catch (error) {
        throw error;
    }
};

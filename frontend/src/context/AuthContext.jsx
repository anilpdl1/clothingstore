import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";
const Auth = createContext();
export const useAuth = () => useContext(Auth);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    if (localStorage.token)
      api
        .get("/auth/me")
        .then((r) => setUser(r.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    else setLoading(false);
  }, []);
  const login = async (data) => {
    localStorage.setItem("token", data.access_token);
    const r = await api.get("/auth/me");
    setUser(r.data);
    return r.data;
  };
  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };
  return (
    <Auth.Provider value={{ user, loading, login, logout }}>
      {children}
    </Auth.Provider>
  );
}

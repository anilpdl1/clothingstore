import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

const errorMessage = (error) => {
  const detail = error.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((issue) => {
        const field = issue.loc?.filter((part) => part !== "body").join(".");
        return field ? `${field}: ${issue.msg}` : issue.msg;
      })
      .join(" ");
  }

  return typeof detail === "string" ? detail : "Please try again";
};

export default function Login() {
  const [mode, setMode] = useState("login"),
    [form, setForm] = useState({ name: "", email: "", password: "" }),
    [error, setError] = useState(""),
    nav = useNavigate(),
    { login } = useAuth();
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    const payload =
      mode === "login"
        ? { email: form.email.trim(), password: form.password }
        : { name: form.name, email: form.email.trim(), password: form.password };

    try {
      const r = await api.post(
        `/auth/${mode === "login" ? "login" : "register"}`,
        payload,
      );
      const user = await login(r.data);
      nav(user.role === "ADMIN" ? "/admin" : "/");
    } catch (e) {
      setError(errorMessage(e));
    }
  };
  return (
    <section className="mx-auto max-w-md px-5 py-16">
      <h1 className="text-4xl font-bold">
        {mode === "login" ? "Welcome back" : "Create account"}
      </h1>
      <form onSubmit={submit} className="mt-8 space-y-4">
        {mode === "register" && (
          <input
            required
            placeholder="Full name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        )}
        <input
          required
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          required
          type="password"
          minLength="8"
          placeholder="Password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        {error && <p className="text-red-600">{error}</p>}
        <button className="w-full rounded-full bg-ink py-3 text-white">
          {mode === "login" ? "Sign in" : "Register"}
        </button>
      </form>
      <button
        className="mt-5 underline"
        onClick={() => {
          setError("");
          setMode(mode === "login" ? "register" : "login");
        }}
      >
        {mode === "login"
          ? "New here? Create an account"
          : "Already a member? Sign in"}
      </button>
    </section>
  );
}

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login(): React.ReactElement {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="card w-full max-w-md p-6">
        <h1 className="mb-1 text-xl font-semibold">Welcome back</h1>
        <p className="mb-6 text-sm text-gray-600">Sign in to continue</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Username</label>
            <input className="input mt-1" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium">Password</label>
            <input type="password" className="input mt-1" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="btn btn-primary w-full" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-6 space-y-2">
          <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            <p className="font-medium">Demo credentials</p>
            <p>Username: <span className="font-mono">admin</span> · Password: <span className="font-mono">password</span></p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              className="btn border border-gray-300"
              onClick={() => { setUsername("admin"); setPassword("password"); }}
            >
              Fill demo credentials
            </button>
            <button
              type="button"
              className="btn btn-primary"
              disabled={loading}
              onClick={async () => {
                setError(null);
                setLoading(true);
                try {
                  await login("admin", "password");
                  navigate("/");
                } catch {
                  setError("Demo login failed");
                } finally {
                  setLoading(false);
                }
              }}
            >
              Sign in as demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}



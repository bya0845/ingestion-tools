import Layout from "../components/Layout";
import "../styles/shared.css";
import { useContext } from "react";
import { TeamsContext } from "../context/TeamContext";

export default function DailyLogsPage() {
  const { teams, error } = useContext(TeamsContext);
  return (
    <Layout>
      <h2 className="page-title">Daily Logs</h2>
      <p className="page-hint">Coming soon.</p>
    </Layout>
  );
}

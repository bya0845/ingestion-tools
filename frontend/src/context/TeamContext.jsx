import { createContext, useState, useEffect } from "react";
import { fetchTeams } from "../api/client";

export const TeamsContext = createContext();

export const TeamsProvider = ({ children }) => {
  const [teams, setTeams] = useState([]);
  const [error, setError] = useState(null);

  console.log("TeamsProvider: Rendering with teams:", teams, "error:", error);

  useEffect(() => {
    console.log("TeamsProvider: useEffect mounting, fetching teams...");
    fetchTeams()
      .then((data) => {
        console.log("TeamsProvider: Teams fetched successfully", data);
        setTeams(data);
      })
      .catch((err) => {
        console.error("TeamsProvider: Error fetching teams", err);
        setError(err.message);
      });
  }, []);

  return (
    <TeamsContext.Provider value={{ teams, error }}>
      {children}
    </TeamsContext.Provider>
  );
};

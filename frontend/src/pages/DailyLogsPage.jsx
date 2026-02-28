import { useState, useCallback, useContext } from "react";
import { previewSchedule, generateDailyLogs } from "../api/client";
import Layout from "../components/Layout";
import { TeamsContext } from "../context/TeamContext";
import { useFileGeneration } from "../hooks/useFileGeneration";
import "../styles/shared.css";

const MASTER_SCHEDULE_COLUMNS = {
  county: 0,
  bin: 1,
  feature_carried: 2,
  feature_crossed: 3,
  prev_inspection_due_date: 5,
  due_date: 6,
  gr: 9,
  access: 15,
  scheduled_date: 16,
  town: 19,
};

const DAY_NAMES = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

function DailyLogPreview({ entries }) {
  const [activeDay, setActiveDay] = useState(null);

  // Group entries by day of week
  const entriesByDay = {};
  entries.forEach((entry) => {
    const date = new Date(entry.scheduled_date);
    const dayIndex = date.getDay();
    if (!entriesByDay[dayIndex]) {
      entriesByDay[dayIndex] = [];
    }
    entriesByDay[dayIndex].push(entry);
  });

  const daysWithEntries = Object.keys(entriesByDay)
    .map((d) => parseInt(d))
    .sort();

  if (daysWithEntries.length === 0) {
    return null;
  }

  if (activeDay === null) {
    setActiveDay(daysWithEntries[0]);
  }

  const currentDayIndex = activeDay;
  const currentEntries = entriesByDay[currentDayIndex] || [];
  const currentDate = currentEntries[0]?.scheduled_date || "";

  return (
    <>
      <h3 style={{ marginTop: "1.5rem", marginBottom: "0.5rem" }}>
        Daily Log Preview
      </h3>
      <div
        style={{
          display: "flex",
          gap: "0.5rem",
          marginBottom: "1rem",
          borderBottom: "1px solid var(--wsp-border)",
        }}
      >
        {daysWithEntries.map((dayIndex) => (
          <button
            key={dayIndex}
            onClick={() => setActiveDay(dayIndex)}
            style={{
              padding: "0.5rem 1rem",
              border: "none",
              background: dayIndex === activeDay ? "var(--wsp-red)" : "#f0f0f0",
              color: dayIndex === activeDay ? "#fff" : "#000",
              cursor: "pointer",
              fontSize: "0.9rem",
              borderBottom:
                dayIndex === activeDay ? "3px solid var(--wsp-red)" : "none",
            }}
          >
            {DAY_NAMES[dayIndex]} ({entriesByDay[dayIndex].length})
          </button>
        ))}
      </div>

      {currentEntries.length > 0 && (
        <div style={{ marginBottom: "1.5rem" }}>
          <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem", color: "#666" }}>
            {currentDate}
          </p>
          <table className="data-table">
            <thead>
              <tr>
                <th>Region</th>
                <th>County</th>
                <th>BIN</th>
                <th>Feature Carried</th>
                <th>Feature Crossed</th>
                <th>Access</th>
              </tr>
            </thead>
            <tbody>
              {currentEntries.slice(0, 7).map((entry, idx) => (
                <tr key={idx}>
                  <td>{entry.region || "8"}</td>
                  <td>{entry.county || ""}</td>
                  <td>{entry.bin || ""}</td>
                  <td>{entry.feature_carried || ""}</td>
                  <td>{entry.feature_crossed || ""}</td>
                  <td>{entry.access || ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {currentEntries.length > 7 && (
            <p style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: "#f00" }}>
              Note: Daily log sheet can hold max 7 entries. {currentEntries.length - 7} entries will not be displayed.
            </p>
          )}
        </div>
      )}
    </>
  );
}

export default function DailyLogsPage() {
  const { teams, error: teamsError } = useContext(TeamsContext);
  const [selectedTeam, setSelectedTeam] = useState("");
  const [rawTsv, setRawTsv] = useState("");
  const [entries, setEntries] = useState([]);

  const {
    error,
    setError,
    successMessage,
    loading,
    setLoading,
    outputDir,
    setOutputDir,
    useDefaultDownload,
    setUseDefaultDownload,
    createGenerateHandler,
  } = useFileGeneration("DailyLogsPage");

  const handlePreview = async (e) => {
    e.preventDefault();
    console.log("DailyLogsPage: Preview button clicked");
    if (!rawTsv.trim()) {
      console.warn("DailyLogsPage: TSV data is empty, aborting preview");
      setError("Data is empty, cannot generate preview");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      console.log("DailyLogsPage: Calling previewSchedule API...");
      const result = await previewSchedule(rawTsv);
      console.log("DailyLogsPage: Preview successful, entries:", result.entries);
      setEntries(result.entries);
    } catch (err) {
      console.error("DailyLogsPage: Preview error", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCellChange = useCallback((rowIndex, field, value) => {
    console.log(
      `DailyLogsPage: Cell changed - Row ${rowIndex}, Field: ${field}, Value: ${value}`,
    );
    setEntries((prev) => {
      const updated = [...prev];
      updated[rowIndex] = { ...updated[rowIndex], [field]: value };
      return updated;
    });
  }, []);

  const handleGenerate = createGenerateHandler(
    "Daily Logs",
    (trimmedDir) =>
      generateDailyLogs(selectedTeam, entries, trimmedDir, !!trimmedDir),
    () => {
      if (!selectedTeam || entries.length === 0) {
        const errorMsg = !selectedTeam
          ? "Please select a team"
          : "Please preview data to add entries";
        return { valid: false, error: errorMsg };
      }
      return { valid: true };
    },
  );

  return (
    <Layout>
      <h2 className="page-title">Daily Logs Generator</h2>
      <div className="page-hint">
        <p>
          Select your team, then copy rows from the master spreadsheet and paste
          below. Pasted data must follow the column index mapping below from the
          master schedule.
        </p>
        <p>
          <b>Column : Index</b>
        </p>
        <pre
          style={{
            backgroundColor: "#f5f5f5",
            padding: "12px",
            borderRadius: "4px",
            fontSize: "12px",
            overflow: "auto",
          }}
        >
          {JSON.stringify(MASTER_SCHEDULE_COLUMNS, null, 2)}
        </pre>
      </div>

      <form onSubmit={handlePreview}>
        <div className="field">
          <label htmlFor="team_name">Team</label>
          <select
            id="team_name"
            value={selectedTeam}
            onChange={(e) => {
              const value = e.target.value;
              console.log("DailyLogsPage: Selected team changed to", value);
              setSelectedTeam(value);
            }}
            required
          >
            <option value="" disabled>
              -- Select team leader --
            </option>
            {teams.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="use_default_download">
            <input
              type="checkbox"
              id="use_default_download"
              checked={useDefaultDownload}
              onChange={(e) => {
                console.log(
                  "DailyLogsPage: useDefaultDownload changed to",
                  e.target.checked,
                );
                setUseDefaultDownload(e.target.checked);
              }}
            />
            Save to default download folder
          </label>
        </div>

        {!useDefaultDownload && (
          <div className="field">
            <label htmlFor="output_dir">Output directory</label>
            <input
              type="text"
              id="output_dir"
              value={outputDir}
              onChange={(e) => {
                const value = e.target.value;
                console.log("DailyLogsPage: Output directory changed to", value);
                setOutputDir(value);
              }}
              placeholder="Leave blank to select folder via browser"
              spellCheck="false"
            />
            <span className="hint-inline">
              Full path on the host machine, e.g. /home/user/logs, or leave
              blank to pick folder
            </span>
          </div>
        )}

        <div className="field">
          <label htmlFor="raw_tsv">Paste data</label>
          <textarea
            id="raw_tsv"
            value={rawTsv}
            onChange={(e) => {
              const value = e.target.value;
              console.log(
                "DailyLogsPage: TSV data changed, length:",
                value.length,
              );
              setRawTsv(value);
            }}
            placeholder="Paste tab-separated rows here..."
          />
        </div>

        <button type="submit" className="btn" disabled={loading}>
          Preview
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading || entries.length === 0 || !selectedTeam}
        >
          Generate Daily Logs
        </button>
      </form>

      {teamsError && <p className="error-msg">{teamsError}</p>}
      {error && <p className="error-msg">{error}</p>}
      {successMessage && <p className="success-msg">{successMessage}</p>}

      {entries.length > 0 && (
        <>
          <p className="count-msg">
            {entries.length} row{entries.length !== 1 ? "s" : ""} parsed.
          </p>
          <table className="data-table">
            <thead>
              <tr>
                <th>BIN</th>
                <th>County</th>
                <th>Feature Carried</th>
                <th>Feature Crossed</th>
                <th>Due Date</th>
                <th>Scheduled Date</th>
                <th>Access</th>
                <th>Lane Closed</th>
                <th>Town</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, idx) => (
                <tr key={idx}>
                  {[
                    "bin",
                    "county",
                    "feature_carried",
                    "feature_crossed",
                    "due_date",
                    "scheduled_date",
                    "access",
                    "lane_closed",
                    "town",
                  ].map((field) => (
                    <td
                      key={field}
                      contentEditable
                      suppressContentEditableWarning
                      spellCheck="false"
                      className={
                        field === "lane_closed" && entry[field] === "Y"
                          ? "lc-y"
                          : ""
                      }
                      onBlur={(e) =>
                        handleCellChange(idx, field, e.target.innerText.trim())
                      }
                    >
                      {entry[field] || (field === "due_date" ? "-" : "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          <DailyLogPreview entries={entries} />
        </>
      )}
    </Layout>
  );
}

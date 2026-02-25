import { useState, useCallback, useContext } from "react";
import { previewSchedule, generateSchedule } from "../api/client";
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

export default function SchedulePage() {
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
  } = useFileGeneration("SchedulePage");

  const handlePreview = async (e) => {
    e.preventDefault();
    console.log("SchedulePage: Preview button clicked");
    if (!rawTsv.trim()) {
      console.warn("SchedulePage: TSV data is empty, aborting preview");
      setError("Data is empty, cannot generate preview");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      console.log("SchedulePage: Calling previewSchedule API...");
      const result = await previewSchedule(rawTsv);
      console.log("SchedulePage: Preview successful, entries:", result.entries);
      setEntries(result.entries);
    } catch (err) {
      console.error("SchedulePage: Preview error", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCellChange = useCallback((rowIndex, field, value) => {
    console.log(
      `SchedulePage: Cell changed - Row ${rowIndex}, Field: ${field}, Value: ${value}`,
    );
    setEntries((prev) => {
      const updated = [...prev];
      updated[rowIndex] = { ...updated[rowIndex], [field]: value };
      return updated;
    });
  }, []);

  const handleGenerate = createGenerateHandler(
    "Schedules",
    (trimmedDir) => generateSchedule(selectedTeam, entries, trimmedDir),
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
      <h2 className="page-title">Inspection Schedule Batch Generator</h2>
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
              console.log("SchedulePage: Selected team changed to", value);
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
                  "SchedulePage: useDefaultDownload changed to",
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
                console.log("SchedulePage: Output directory changed to", value);
                setOutputDir(value);
              }}
              placeholder="Leave blank to select folder via browser"
              spellCheck="false"
            />
            <span className="hint-inline">
              Full path on the host machine, e.g. /home/user/schedules, or leave
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
                "SchedulePage: TSV data changed, length:",
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
          Generate Schedules
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
        </>
      )}
    </Layout>
  );
}

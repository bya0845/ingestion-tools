import { useState, useEffect, useCallback } from 'react';
import { fetchTeams, previewSchedule, generateSchedule } from '../api/client';
import Layout from '../components/Layout';
import '../styles/shared.css';

export default function SchedulePage() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [rawTsv, setRawTsv] = useState('');
  const [entries, setEntries] = useState([]);
  const [outputDir, setOutputDir] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTeams().then(setTeams).catch((err) => setError(err.message));
  }, []);

  const handlePreview = async (e) => {
    e.preventDefault();
    if (!rawTsv.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await previewSchedule(rawTsv);
      setEntries(result.entries);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCellChange = useCallback((rowIndex, field, value) => {
    setEntries((prev) => {
      const updated = [...prev];
      updated[rowIndex] = { ...updated[rowIndex], [field]: value };
      return updated;
    });
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedTeam || entries.length === 0) return;

    const dir = prompt('Save to directory (leave blank to download to browser):', outputDir);
    if (dir === null) return;

    const trimmedDir = dir.trim();
    setOutputDir(trimmedDir);
    setLoading(true);
    setError(null);
    try {
      const { blob, filename } = await generateSchedule(selectedTeam, entries, trimmedDir);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h2 className="page-title">Generate Inspection Schedule</h2>
      <p className="page-hint">
        Select your team, then copy rows from the master spreadsheet and paste below.
        Columns: Cty, BIN, Carried, Crossed, Due Date, Access, Booked Access, TOWN.
      </p>

      <form onSubmit={handlePreview}>
        <div className="field">
          <label htmlFor="team_name">Team</label>
          <select id="team_name" value={selectedTeam} onChange={(e) => setSelectedTeam(e.target.value)} required>
            <option value="" disabled>-- Select team leader --</option>
            {teams.map((t) => (<option key={t.value} value={t.value}>{t.label}</option>))}
          </select>
        </div>

        <details className="settings">
          <summary>Settings</summary>
          <div className="field settings-field">
            <label htmlFor="output_dir">Output directory</label>
            <input type="text" id="output_dir" value={outputDir} onChange={(e) => setOutputDir(e.target.value)} placeholder="Leave blank to use default output/ folder" spellCheck="false" />
            <span className="hint-inline">Full path on the host machine, e.g. /home/user/schedules</span>
          </div>
        </details>

        <div className="field">
          <label htmlFor="raw_tsv">Paste data</label>
          <textarea id="raw_tsv" value={rawTsv} onChange={(e) => setRawTsv(e.target.value)} placeholder="Paste tab-separated rows here..." />
        </div>

        <button type="submit" className="btn" disabled={loading}>Preview</button>
        <button type="button" className="btn btn-primary" onClick={handleGenerate} disabled={loading || entries.length === 0 || !selectedTeam}>Generate Schedules</button>
      </form>

      {error && <p className="error-msg">{error}</p>}

      {entries.length > 0 && (
        <>
          <p className="count-msg">{entries.length} row{entries.length !== 1 ? 's' : ''} parsed.</p>
          <table className="data-table">
            <thead>
              <tr>
                <th>BIN</th><th>County</th><th>Feature Carried</th><th>Feature Crossed</th>
                <th>Due Date</th><th>Scheduled Date</th><th>Access</th><th>Lane Closed</th><th>Town</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, idx) => (
                <tr key={idx}>
                  {['bin', 'county', 'feature_carried', 'feature_crossed', 'due_date', 'scheduled_date', 'access', 'lane_closed', 'town'].map((field) => (
                    <td
                      key={field}
                      contentEditable
                      suppressContentEditableWarning
                      spellCheck="false"
                      className={field === 'lane_closed' && entry[field] === 'Y' ? 'lc-y' : ''}
                      onBlur={(e) => handleCellChange(idx, field, e.target.innerText.trim())}
                    >
                      {entry[field] || (field === 'due_date' ? '-' : '')}
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

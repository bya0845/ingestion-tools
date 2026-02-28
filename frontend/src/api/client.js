const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function fetchTeams() {
  const response = await fetch(`${API_BASE_URL}/teams/`);
  if (!response.ok) throw new Error('Failed to fetch teams');
  return response.json();
}

export async function previewSchedule(rawTsv) {
  const response = await fetch(`${API_BASE_URL}/inspections/preview/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_tsv: rawTsv }),
  });
  if (!response.ok) throw new Error('Failed to preview schedule');
  return response.json();
}

export async function generateSchedule(teamName, entries, outputDir = '', saveToSystem = false) {
  const response = await fetch(`${API_BASE_URL}/inspections/schedule/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      team_name: teamName,
      entries_json: JSON.stringify(entries),
      output_dir: outputDir,
      save_to_system: saveToSystem,
    }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Failed to generate schedule' }));
    throw new Error(error.error || 'Failed to generate schedule');
  }
  const contentType = response.headers.get('Content-Type') || '';
  const filename = response.headers.get('Content-Disposition')?.match(/filename="(.+)"/)?.[1] || 'schedule.xlsx';
  const blob = await response.blob();
  return { blob, filename, contentType };
}

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SchedulePage from "./pages/SchedulePage";
import DailyLogsPage from "./pages/DailyLogsPage";
import BatSurveyPage from "./pages/BatSurveyPage";
import Sketch801Page from "./pages/Sketch801Page";
import { TeamsProvider } from "./context/TeamContext";

function App() {
  return (
    <TeamsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/daily-logs" element={<DailyLogsPage />} />
          <Route path="/bat-survey" element={<BatSurveyPage />} />
          <Route path="/801-sketch" element={<Sketch801Page />} />
        </Routes>
      </BrowserRouter>
    </TeamsProvider>
  );
}

export default App;

import { NavLink } from "react-router-dom";
import "./Layout.css";

const menuItems = [
  { to: "/", label: "Home" },
  { to: "/schedule", label: "Schedule" },
  { to: "/daily-logs", label: "Daily Logs" },
  { to: "/bat-survey", label: "Bat Survey Forms" },
  { to: "/801-sketch", label: "ADE-801 (Stream Hydraulics)" },
];

export default function Layout({ children }) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-mark" />
          <span className="logo-text">
            <span className="accent">WSP USA</span>
          </span>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}

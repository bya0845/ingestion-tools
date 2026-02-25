import Layout from "../components/Layout";
import "../styles/shared.css";

export default function Home() {
  return (
    <Layout>
      <h2 className="page-title">
        <span style={{ fontSize: "32px" }}>*TEST*</span>
        <br />
        <br />
        Bridge Inspection Automation Toolkit
        <br />
        <br />
      </h2>
      <p className="page-hint">
        Apps for generating bridge inspection documents.
      </p>
      <p className="page-hint">Use the menu on the left to navigate.</p>
    </Layout>
  );
}

import Layout from '../components/Layout';
import '../styles/shared.css';

export default function Home() {
  return (
    <Layout>
      <h2 className="page-title">NYSDOT Region 8 Bridge Inspection</h2>
      <p className="page-hint">
        Tools for generating inspection schedules and documentation.
      </p>
      <p className="page-hint">
        Use the menu on the left to navigate.
      </p>
    </Layout>
  );
}

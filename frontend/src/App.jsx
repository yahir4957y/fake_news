import { SignedIn, SignedOut } from "@clerk/clerk-react";
import "./App.css";

// Importacion componentes
import Landing from "./pages/Landing";
import DashboardLayout from "./layouts/DashboardLayout";

function App() {
  return (
    <>
      {}
      <SignedIn>
        <DashboardLayout />
      </SignedIn>

      {}
      <SignedOut>
        <Landing />
      </SignedOut>
    </>
  );
}

export default App;
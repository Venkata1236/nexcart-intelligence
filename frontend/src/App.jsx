import { BrowserRouter, Routes, Route } from "react-router-dom";
import StorePage from "./pages/StorePage";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StorePage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
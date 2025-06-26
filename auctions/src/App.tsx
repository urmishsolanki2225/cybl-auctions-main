import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Homepage from "./pages/Homepage";
import Login from "./pages/Login";
import Registration from "./pages/Registration";
import AuctionsListing from "./pages/AuctionsListing";
import AuctionDetails from "./pages/AuctionDetails";
import LotDetails from "./pages/LotDetails";
import Category from "./pages/Category";
import Contact from "./pages/Contact";
import UserProfile from "./pages/UserProfile";
import SellerActivity from "./pages/SellerActivity";
import Watchlist from "./pages/Watchlist"
import CatLots from "./pages/CatLots.tsx";
import NotFound from "./pages/NotFound";
import "./styles/global.css";
import PrivateRoute from "./routes/PrivateRoute";
import ToastProvider from "./components/ToastProvider";
import { WatchlistProvider } from "./context/WatchlistContext";
const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <WatchlistProvider>
      <ToastProvider />
      <BrowserRouter>
        <div className="app">
          <Navbar />
          <main className="main-content">
            
            <Routes>
              <Route path="/" element={<Homepage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Registration />} />
              <Route path="/auctions" element={<AuctionsListing />} />
              <Route path="/auction/:id" element={<AuctionDetails />} />
              <Route path="/category/lots" element={<CatLots />} />
              <Route path="/lot/:id" element={<LotDetails />} />
              <Route path="/category" element={<Category />} />
              <Route path="/contact" element={<Contact />} />      
              <Route path="/watchlist" element={<Watchlist />} />     
              <Route path="/account" element={
                <PrivateRoute>
                  <UserProfile />
                </PrivateRoute>
              } />


              <Route path="/seller-activity" element={
                <PrivateRoute>
                  <SellerActivity />
                </PrivateRoute>
              } />

              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>    
    </WatchlistProvider>
  </QueryClientProvider>
);

export default App;
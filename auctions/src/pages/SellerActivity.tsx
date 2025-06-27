import React, { useState, useEffect } from "react";
import axios from "axios";

const SellerActivity = () => {
  const userData = JSON.parse(localStorage.getItem("user"));
  const [inventory, setInventory] = useState([]);
  const [filteredInventory, setFilteredInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bidHistory, setBidHistory] = useState([]);
  const [statusFilter, setStatusFilter] = useState("all");

  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 5;

  const [showModal, setShowModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const [modalPage, setModalPage] = useState(1);
  const modalRowsPerPage = 3;

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const response = await axios.get(
          `http://192.168.2.108:8000/api/seller_inventory/${userData.id}/`
        );
        setInventory(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchInventory();
  }, [userData.id]);

  useEffect(() => {
    let filtered = inventory;

    if (statusFilter !== "all") {
      if (statusFilter === "auction") {
        filtered = inventory.filter((item) => item.status === "auction");
      } else {
        filtered = inventory.filter((item) => item.status === statusFilter);
      }
    }

    setFilteredInventory(filtered);
    setCurrentPage(1);
  }, [inventory, statusFilter]);

  const fetchBidHistory = async (itemId) => {
    try {
      const response = await axios.get(
        `http://192.168.2.108:8000/api/item_bid_history/${itemId}/`
      );
      setBidHistory(response.data);
      setModalPage(1);
    } catch (err) {
      console.error("Error fetching bid history:", err);
    }
  };

  const handleRowClick = async (item) => {
    if (item.status === "sold") {
      setSelectedItem(item);
      await fetchBidHistory(item.id);
      setShowModal(true);
    }
  };

  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;
  const currentRows = filteredInventory.slice(indexOfFirstRow, indexOfLastRow);
  const totalPages = Math.ceil(filteredInventory.length / rowsPerPage);

  const modalStart = (modalPage - 1) * modalRowsPerPage;
  const modalEnd = modalStart + modalRowsPerPage;
  const currentBidHistory = bidHistory.slice(modalStart, modalEnd);
  const modalTotalPages = Math.ceil(bidHistory.length / modalRowsPerPage);

  const handleStatusFilterChange = (e) => setStatusFilter(e.target.value);

  if (loading) return <div style={styles.loader}>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Seller Inventory</h2>

      <div style={styles.filterContainer}>
        <label htmlFor="statusFilter" style={styles.filterLabel}>Filter: </label>
        <select
          id="statusFilter"
          value={statusFilter}
          onChange={handleStatusFilterChange}
          style={styles.filterSelect}
        >
          <option value="all">All Items</option>
          <option value="sold">Sold Items</option>
          <option value="unsold">Unsold Items</option>
          <option value="auction">Auction Items</option>
        </select>
      </div>

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>ID</th>
            <th style={styles.th}>Title</th>
            <th style={styles.th}>Category</th>
            <th style={styles.th}>Starting Bid</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}>Buyer</th>
          </tr>
        </thead>
        <tbody>
          {currentRows.map((item) => (
            <tr
              key={item.id}
              style={{
                ...styles.tr,
                cursor: item.status === "sold" ? "pointer" : "default",
                backgroundColor:
                  item.status === "sold"
                    ? "#e8f5e9"
                    : item.status === "unsold"
                    ? "#ffebee"
                    : "#f3f3f3",
              }}
              onClick={() => handleRowClick(item)}
            >
              <td style={styles.td}>{item.id}</td>
              <td style={styles.td}>{item.title}</td>
              <td style={styles.td}>{item.category}</td>
              <td style={styles.td}>${item.starting_bid}</td>
              <td style={styles.td}>
                <strong
                  style={{
                    color:
                      item.status === "sold"
                        ? "green"
                        : item.status === "unsold"
                        ? "red"
                        : "orange",
                  }}
                >
                  {item.status}
                </strong>
              </td>
              <td style={styles.td}>{item.buyer || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={styles.pagination}>
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i}
            onClick={() => setCurrentPage(i + 1)}
            style={{
              ...styles.pageButton,
              backgroundColor: currentPage === i + 1 ? "#6c63ff" : "#f0f0f0",
              color: currentPage === i + 1 ? "#fff" : "#333",
            }}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h3 style={{ marginBottom: "10px" }}>
              Bid History: {selectedItem.title}
            </h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Bidder name</th>
                  <th style={styles.th}>Amount</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {currentBidHistory.map((bid, index) => (
                  <tr>
                    <td style={styles.td}>{bid.bidder}</td>
                    <td style={styles.td}>{bid.bid_amount}</td>
                    <td style={styles.td}>{bid.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            <div style={styles.pagination}>
              {Array.from({ length: modalTotalPages }, (_, i) => (
                <button
                  key={i}
                  onClick={() => setModalPage(i + 1)}
                  style={{
                    ...styles.pageButton,
                    backgroundColor: modalPage === i + 1 ? "#6c63ff" : "#f0f0f0",
                    color: modalPage === i + 1 ? "#fff" : "#333",
                  }}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button style={styles.closeButton} onClick={() => setShowModal(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: { padding: "30px", maxWidth: "1000px", margin: "0 auto" },
  heading: { textAlign: "center", marginBottom: "30px", fontSize: "24px" },
  filterContainer: {
    marginBottom: "20px",
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
  },
  filterLabel: { marginRight: "10px", fontWeight: "bold" },
  filterSelect: {
    padding: "8px 12px",
    borderRadius: "4px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  table: {
    borderCollapse: "collapse",
    width: "100%",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    borderRadius: "8px",
    overflow: "hidden",
    marginBottom: "20px",
  },
  th: {
    backgroundColor: "#6c63ff",
    color: "#fff",
    padding: "12px",
    textAlign: "left",
  },
  td: {
    padding: "12px",
    borderBottom: "1px solid #ddd",
  },
  tr: {},
  pagination: {
    display: "flex",
    justifyContent: "center",
    gap: "8px",
    margin: "20px 0",
  },
  pageButton: {
    padding: "6px 12px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
  },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.4)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  modal: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "10px",
    width: "500px",
    maxHeight: "80vh",
    overflowY: "auto",
    boxShadow: "0 0 15px rgba(0,0,0,0.2)",
  },
  closeButton: {
    marginTop: "15px",
    backgroundColor: "#6c63ff",
    color: "#fff",
    padding: "10px 20px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  bidRow: {
    padding: "10px",
    borderBottom: "1px solid #eee",
  },
  loader: {
    textAlign: "center",
    padding: "40px",
    fontSize: "18px",
    color: "#555",
  },
};

export default SellerActivity;

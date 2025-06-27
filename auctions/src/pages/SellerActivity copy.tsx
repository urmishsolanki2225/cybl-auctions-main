import React, { useState } from 'react';

const SellerActivity = () => {
  const inventory = [
    { id: 1, name: 'Item 1', category: 'Category A', quantity: 10, status: 'Available' },
    { id: 2, name: 'Item 2', category: 'Category B', quantity: 5, status: 'Sold', buyer: 'John Doe' },
    { id: 3, name: 'Item 3', category: 'Category C', quantity: 7, status: 'Available' },
    { id: 4, name: 'Item 4', category: 'Category A', quantity: 0, status: 'UnSold' },
    { id: 5, name: 'Item 5', category: 'Category B', quantity: 12, status: 'Sold', buyer: 'Jane Smith' },
    { id: 6, name: 'Item 6', category: 'Category C', quantity: 8, status: 'Available' },
    { id: 7, name: 'Item 7', category: 'Category A', quantity: 0, status: 'UnSold' },
    { id: 8, name: 'Item 8', category: 'Category B', quantity: 4, status: 'Sold', buyer: 'Michael Green' },
    { id: 9, name: 'Item 9', category: 'Category A', quantity: 6, status: 'Available' },
    { id: 10, name: 'Item 10', category: 'Category C', quantity: 2, status: 'Sold', buyer: 'Emily Johnson' },
  ];

  const staticBidHistory = [
    { bidder: 'Alice', amount: '$100', date: '2025-06-20' },
    { bidder: 'Bob', amount: '$120', date: '2025-06-21' },
    { bidder: 'John Doe', amount: '$140', date: '2025-06-22' },
    { bidder: 'Carol', amount: '$160', date: '2025-06-23' },
    { bidder: 'Dave', amount: '$180', date: '2025-06-24' },
    { bidder: 'Eva', amount: '$200', date: '2025-06-25' },
  ];

  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 5;
  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;
  const currentRows = inventory.slice(indexOfFirstRow, indexOfLastRow);
  const totalPages = Math.ceil(inventory.length / rowsPerPage);

  const [showModal, setShowModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  // Modal pagination
  const [modalPage, setModalPage] = useState(1);
  const modalRowsPerPage = 3;
  const modalTotalPages = Math.ceil(staticBidHistory.length / modalRowsPerPage);
  const modalStart = (modalPage - 1) * modalRowsPerPage;
  const modalEnd = modalStart + modalRowsPerPage;
  const currentBidHistory = staticBidHistory.slice(modalStart, modalEnd);

  const handlePageChange = (pageNumber) => setCurrentPage(pageNumber);

  const handleRowClick = (item) => {
    if (item.status === 'Sold') {
      setSelectedItem(item);
      setModalPage(1); // Reset to page 1 when opening modal
      setShowModal(true);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Seller Inventory</h2>

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>ID</th>
            <th style={styles.th}>Name</th>
            <th style={styles.th}>Category</th>
            <th style={styles.th}>Quantity</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}>Buyer</th>
          </tr>
        </thead>
        <tbody>
          {currentRows.map(item => (
            <tr
              key={item.id}
              style={{ ...styles.tr, cursor: item.status === 'Sold' ? 'pointer' : 'default' }}
              onClick={() => handleRowClick(item)}
            >
              <td style={styles.td}>{item.id}</td>
              <td style={styles.td}>{item.name}</td>
              <td style={styles.td}>{item.category}</td>
              <td style={styles.td}>{item.quantity}</td>
              <td style={styles.td}>{item.status}</td>
              <td style={styles.td}>{item.status === 'Sold' ? item.buyer : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={styles.pagination}>
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i}
            onClick={() => handlePageChange(i + 1)}
            style={{
              ...styles.pageButton,
              backgroundColor: currentPage === i + 1 ? '#6c63ff' : '#f0f0f0',
              color: currentPage === i + 1 ? '#fff' : '#333',
            }}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {showModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h3>Bid History for {selectedItem.name}</h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Bidder</th>
                  <th style={styles.th}>Amount</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {currentBidHistory.map((bid, index) => (
                  <tr key={index}>
                    <td style={styles.td}>{bid.bidder}</td>
                    <td style={styles.td}>{bid.amount}</td>
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
                    backgroundColor: modalPage === i + 1 ? '#6c63ff' : '#f0f0f0',
                    color: modalPage === i + 1 ? '#fff' : '#333',
                  }}
                >
                  {i + 1}
                </button>
              ))}
            </div>

            <button style={styles.closeButton} onClick={() => setShowModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1000px',
    margin: '0 auto',
  },
  table: {
    borderCollapse: 'collapse',
    width: '100%',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    borderRadius: '12px',
    overflow: 'hidden',
    marginBottom: '20px',
  },
  th: {
    backgroundColor: '#6c63ff',
    color: '#fff',
    padding: '12px 15px',
    textAlign: 'left',
  },
  td: {
    padding: '12px 15px',
    borderBottom: '1px solid #ddd',
  },
  tr: {
    backgroundColor: '#fafafa',
  },
  pagination: {
    marginTop: '10px',
    textAlign: 'center',
  },
  pageButton: {
    padding: '8px 12px',
    margin: '0 5px',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  modal: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '12px',
    width: '500px',
    maxHeight: '80vh',
    overflowY: 'auto',
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
  },
  closeButton: {
    marginTop: '15px',
    backgroundColor: '#6c63ff',
    color: '#fff',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  }
};

export default SellerActivity;

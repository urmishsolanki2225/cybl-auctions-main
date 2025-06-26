import React from 'react';

const colors = ['#e63946', '#f1fa8c', '#a8dadc', '#457b9d', '#ff006e', '#06d6a0'];

const SellerActivity = () => {
  return (
    <div style={styles.container}>
      {colors.map((color, index) => (
        <div
          key={index}
          style={{ ...styles.box, backgroundColor: color }}
        />
      ))}
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    justifyContent: 'center',
    padding: '20px',
  },
  box: {
    width: '100px',
    height: '100px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  },
};

export default SellerActivity;
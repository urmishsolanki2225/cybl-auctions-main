import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div >
      <div className="container" style={{ textAlign: 'center', padding: '50px 0' }}>
        <div className="category-content">
          <h1 style={{ fontSize: '120px', fontWeight: 'bold', margin: '0', color: '#ff6b6b' }}>404</h1>
          <h2 style={{ fontSize: '32px', margin: '20px 0' }}>Oops! Page Not Found</h2>
          <p style={{ fontSize: '18px', marginBottom: '30px' }}>
            The page you're looking for doesn't exist or has been moved.
          </p>
          <button 
            onClick={() => navigate('/')}
            style={{
              padding: '12px 30px',
              backgroundColor: '#4a6cf7',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              fontSize: '16px',
              cursor: 'pointer',
              transition: 'background-color 0.3s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#3a5be8'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#4a6cf7'}
          >
            Go Back Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
import { useState } from 'react';
import '../styles/Contact.css';
import BASE_URL from '../api/endpoints';
import { toast } from 'react-toastify';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch(BASE_URL+'/api/contact/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      toast.success(` Message sent!!`);
      setFormData({ name: '', email: '', subject: '', message: '' });
    } else {
      alert('Failed to send message');
    }
  };


  return (
    <div className="contact-page">
      <div className="auctions-container">     

        <div className="contact-content">
          <div className="contact-info">
            <h2>Contact Information</h2>
            <div className="contact-item">
              <div className="contact-icon">📧</div>
              <div>
                <h3>Email</h3>
                <p>support@auctionhub.com</p>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">📞</div>
              <div>
                <h3>Phone</h3>
                <p>+1 (555) 123-4567</p>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">📍</div>
              <div>
                <h3>Address</h3>
                <p>123 Auction Street<br />New York, NY 10001</p>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">🕒</div>
              <div>
                <h3>Business Hours</h3>
                <p>Monday - Friday: 9:00 AM - 6:00 PM<br />Saturday: 10:00 AM - 4:00 PM</p>
              </div>
            </div>
          </div>

          <div className="contact-form-wrapper">
            <form onSubmit={handleSubmit} className="contact-form">
              <div className="form-group">
                <label htmlFor="name" className="form-label">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email" className="form-label">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="subject" className="form-label">Subject</label>
                <select
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className="form-input"
                  required
                >
                  <option value="">Select a subject</option>
                  <option value="general">General Inquiry</option>
                  <option value="bidding">Bidding Support</option>
                  <option value="payment">Payment Issues</option>
                  <option value="technical">Technical Support</option>
                  <option value="seller">Seller Support</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="message" className="form-label">Message</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  className="form-textarea"
                  rows={6}
                  required
                ></textarea>
              </div>

              <button type="submit" className="btn btn-primary contact-submit">
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;

import React, { useState } from 'react'
import { motion } from 'framer-motion'

const Admin: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: ''
  })

  const supportOptions = [
    {
      title: 'Technical Support',
      description: 'Get help with platform integration and technical issues',
      contact: 'support@culturalos.com',
      hours: '24/7 Support Available'
    },
    {
      title: 'Sales Inquiries',
      description: 'Learn about enterprise solutions and pricing',
      contact: 'sales@culturalos.com',
      hours: 'Mon-Fri, 9AM-6PM EST'
    },
    {
      title: 'Partnership Opportunities',
      description: 'Explore integration and partnership possibilities',
      contact: 'partnerships@culturalos.com',
      hours: 'Mon-Fri, 9AM-5PM EST'
    },
    {
      title: 'Media & Press',
      description: 'Press inquiries and media resources',
      contact: 'press@culturalos.com',
      hours: 'Mon-Fri, 9AM-5PM EST'
    }
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log('Form submitted:', formData)
    // Reset form
    setFormData({
      name: '',
      email: '',
      company: '',
      subject: '',
      message: ''
    })
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-24">
        <div className="container">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                We're Here to <span className="text-blue-600">Help You Succeed</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Get the support you need to maximize your cultural intelligence platform. 
                Our expert team is ready to assist with technical questions, implementation, and strategic guidance.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Support Options */}
      <section className="py-16 bg-gray-50">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How Can We Help?</h2>
            <p className="text-lg text-gray-600">
              Choose the support option that best fits your needs
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {supportOptions.map((option, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card p-8"
              >
                <h3 className="text-2xl font-bold mb-4">{option.title}</h3>
                <p className="text-gray-600 mb-6 leading-relaxed">{option.description}</p>
                <div className="space-y-2">
                  <div className="flex items-center text-gray-700">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                    <a href={`mailto:${option.contact}`} className="text-blue-600 hover:text-blue-700 font-medium">
                      {option.contact}
                    </a>
                  </div>
                  <div className="flex items-center text-gray-700">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                    {option.hours}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-16">
        <div className="container max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Send Us a Message</h2>
            <p className="text-lg text-gray-600">
              Fill out the form below and we'll get back to you within 24 hours
            </p>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="card p-8"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="label">Full Name *</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="input"
                    placeholder="Enter your full name"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="label">Email Address *</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="input"
                    placeholder="Enter your email address"
                  />
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="company" className="label">Company</label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Enter your company name"
                  />
                </div>
                <div>
                  <label htmlFor="subject" className="label">Subject *</label>
                  <select
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    className="input"
                  >
                    <option value="">Select a subject</option>
                    <option value="technical">Technical Support</option>
                    <option value="sales">Sales Inquiry</option>
                    <option value="partnership">Partnership</option>
                    <option value="billing">Billing Question</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label htmlFor="message" className="label">Message *</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  rows={6}
                  className="input resize-none"
                  placeholder="Tell us how we can help you..."
                />
              </div>
              
              <div className="text-center">
                <button type="submit" className="btn btn-primary px-8 py-3 text-lg">
                  Send Message
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-gray-50">
        <div className="container max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-lg text-gray-600">Quick answers to common questions</p>
          </div>
          
          <div className="space-y-6">
            {[
              {
                question: 'How do I integrate CulturalOS with my existing systems?',
                answer: 'CulturalOS offers comprehensive APIs and SDKs for seamless integration. Our technical team provides full implementation support and documentation.'
              },
              {
                question: 'What data sources does the platform analyze?',
                answer: 'We analyze social media platforms (Instagram, TikTok, Spotify), web browsing patterns, content engagement, and other digital touchpoints while maintaining strict privacy standards.'
              },
              {
                question: 'Is my data secure and private?',
                answer: 'Yes, we employ enterprise-grade security measures including end-to-end encryption, SOC 2 compliance, and GDPR adherence. Your data is never shared with third parties.'
              },
              {
                question: 'Can I customize the cultural intelligence metrics?',
                answer: 'Absolutely. Enterprise customers can define custom cultural dimensions, create branded dashboards, and configure metrics specific to their industry needs.'
              },
              {
                question: 'What kind of support is included with my subscription?',
                answer: 'All plans include email support, comprehensive documentation, and access to our knowledge base. Enterprise plans include dedicated account management and phone support.'
              }
            ].map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card p-6"
              >
                <h3 className="text-lg font-bold mb-3">{faq.question}</h3>
                <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Emergency Support */}
      <section className="py-16 bg-red-600 text-white">
        <div className="container text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Need Immediate Assistance?</h2>
            <p className="text-xl text-red-100 mb-8 max-w-3xl mx-auto">
              For critical issues affecting your production environment, 
              our emergency support team is available 24/7.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="tel:+1-800-CULTURAL"
                className="btn bg-white text-red-600 hover:bg-red-50 px-8 py-3 text-lg"
              >
                Call Emergency Support
              </a>
              <a
                href="mailto:emergency@culturalos.com"
                className="btn border-white text-white hover:bg-white hover:text-red-600 px-8 py-3 text-lg"
              >
                Email Emergency Team
              </a>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Admin
import React, { useEffect, useState } from 'react';
import Header from '../components/generalComponents/header.js';
import Sidebar from '../components/faqPage/faqSidebar.js'; 
import './FaqPage.css';
import { checkAuth, fetchUserInfo } from '../services/api';
import { useNavigate } from 'react-router-dom';

const FAQPage = () => {
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');
  const navigate = useNavigate();

  
  useEffect(() => {
    const checkAuthAndFetchUserInfo = async () => {
      try {
        const authStatus = await checkAuth();
        if (authStatus.authenticated) {
          const userInfo = await fetchUserInfo();
          setUserEmail(userInfo.email);
          setUserName(userInfo.name);
        } else {
          navigate('/login');
        }
      } catch (error) {
        console.error('Failed to fetch user info:', error);
      }
    };
  
    checkAuthAndFetchUserInfo();
  }, [navigate]);
  
  const faqData = 
    [
        {
    question: "How do I upload files to Diganise?",
    answer: "To upload files, click the 'New' button in the top-left corner and select 'Upload File'. You can also drag and drop files directly into the Diganise interface."
  },
  {
    question: "How can I share files or folders?",
    answer: "Select the file or folder you want to share via the file action menu. This can be accessed via the three vertical dotted icon. After that, click the 'Share' button. You can then share a link with the user with the access permission that you desire. More specific share functionality shall be added in later versions."
  },
  {
    question: "How do I organise my files in Diganise?",
    answer: "You can create folders to organise your files. To create a new folder, click the 'New' button in the top-left corner and select 'New Folder'. You can move files into the folder by clicking on the action menu button and selecting 'Move', which will open up a popup. You can then select the folder you want to move the file to."
  },
  {
    question: "Can I access my Diganise files offline?",
    answer: "Unfortunately, offline access is not yet available directly through Diganise. However, you are able to access your Diganise files offline via Google Drive. You can enable offline access by going to the settings in Google Drive and checking the 'Offline' box. This will allow you to access your files offline via the Google Drive app on your device."
  },
  {
    question: "How do I search for a specific file or folder?",
    answer: "At this moment in time, you will have to find the file or folder manually. However, future versions of the software will include a search functionality."
  },
  {
    question: "What file types can I store in Diganise?",
    answer: "Diganise supports a wide range of file types, including documents, spreadsheets, presentations, PDFs, images, videos, and more. However, there are some restrictions on file sizes and types for security reasons."
  },
  {
    question: "How do I rename a file or folder?",
    answer: "In order to rename a file, you will have to open the file action menu using the three vertical dots icon. After opening the menu, click the rename icon (pencil symbol) in the top menu, and enter your preferred name."
  },
  {
    question: "Can I recover deleted files?",
    answer: "No, once a file is deleted, it cannot be recovered. Please be cautious when deleting files, as they will be permanently removed from your Diganise account. Future versions of the software may include a trash bin functionality."
  },
  {
    question: "How do I change the colour of a folder?",
    answer: "This functionality is not available currently, but will be added in future versions."
  },
  {
    question: "Is there a limit to how much I can store on Diganise?",
    answer: "The storage limit depends on your Google account type. Free accounts typically come with 15 GB of storage, shared across Google Drive (Diganise), Gmail, and Google Photos. You can purchase additional storage if needed, but be sure to contact the administrator of your Google Account. Diganise will update automatically depending on the status of your Google Account."
  },
  {
    question: "How do I create a new document directly in Diganise?",
    answer: "Click the 'New' button in the top-left corner, then select the type of document you want to create (e.g., Google Docs and Sheets). The new document will automatically be saved in your Diganise. More document types will be added in the future."
  },
  {
    question: "Can I use Diganise collaboratively with others?",
    answer: "Yes, Diganise is excellent for collaboration. You can share files and folders with others, allowing them to view, comment on, or edit the contents depending on the permissions you set."
  },
  {
    question: "Is Diganise open-source?",
    answer: "Yes, Diganise is indeed open-source. This means that the source code for Diganise is publicly available and can be viewed, modified, and distributed by anyone, subject to the terms of its open-source license."
  }
  ];

  return (
    <div className="faq-page">
      <div className="faq-header">
        <Header userEmail={userEmail} userName={userName} />
      </div>
      <div className="faq-sidebar">
        <Sidebar />
      </div>
      <div className="faq-main-content">
        <div className="faq-content">
          <h1>Frequently Asked Questions</h1>
          {faqData.map((item, index) => (
            <div key={index} className="faq-item">
              <h2>{item.question}</h2>
              <p>{item.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FAQPage;
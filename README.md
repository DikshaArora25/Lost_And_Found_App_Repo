# 🚀 LostNoMore - Your Digital Lost & Found Companion  

## 🌟 Introduction  
Ever misplaced something and wished there was an easier way to find it? LostNoMore is here to make that happen! It’s a smart, bifunctional **lost and found web application** designed to connect people with their lost belongings. Built with **Django** for frontend management and **Flask APIs** for seamless backend communication, LostNoMore bridges the gap between seekers and finders efficiently.

## 🏆 Why LostNoMore?  
In today’s fast-paced world, items get misplaced all the time—phones left in cafés, keys forgotten in parks, backpacks lost on public transport. Searching manually is frustrating and inefficient. LostNoMore brings people together, using technology to **increase the chances of recovery** with an intuitive interface and **AI-powered matching system**.

## 🔥 Features  
- 📌 **Report lost items** with details & images  
- 🔍 **Browse found items** posted by other users  
- 🤖 **Intelligent item matching** using Flask backend APIs  
- 🔐 **User authentication** for secure tracking & interactions  
- ⚡ **Real-time notifications** when a potential match is found  

## 🛠️ Tech Stack  
LostNoMore is powered by:  
- **Frontend:** Django, HTML, CSS, JavaScript  
- **Backend:** Flask APIs  
- **Database:** PostgreSQL  
- **Authentication:** JWT-based secure login system  

## 💡 How It Works  
### 1️⃣ Reporting a Lost Item  
Users log in and submit details of their lost item, including description, location, and image.  

### 2️⃣ Browsing Found Items  
Anyone can browse the list of found items and filter by category, location, and time.  

### 3️⃣ Smart Matching System  
LostNoMore scans entries and uses **Flask APIs** to suggest possible matches, notifying users when a similar item is found.  

### 4️⃣ Direct Communication  
Matched users can securely chat via the platform to arrange pickup and verification.  

## 🎯 Installation Guide  
Want to run LostNoMore on your machine? Follow these steps!  

```bash
git clone https://github.com/yourusername/LostNoMore.git
cd LostNoMore
python -m venv venv
source venv/bin/activate  # Windows users: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # Starts Django frontend
python flask_api.py  # Starts Flask backend
